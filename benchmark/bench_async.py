"""Async benchmark: aerospike-py AsyncClient vs official C client sync.

The official C client has no async API, so we compare:
  - aerospike-py AsyncClient (sequential & concurrent via asyncio.gather)
  - official C client sync (sequential baseline)

This demonstrates the throughput advantage of async + concurrency.

Usage:
    python benchmark/bench_async.py [--count N] [--concurrency C] [--host HOST] [--port PORT]

Requirements:
    pip install aerospike   # official C client (comparison target)
"""

import argparse
import asyncio
import statistics
import time

NAMESPACE = "test"
SET_NAME = "bench_async"


# ── helpers ──────────────────────────────────────────────────


def _summarize(times: list[float]) -> dict:
    ms = [t * 1000 for t in times]
    total = sum(times)
    return {
        "avg_ms": statistics.mean(ms),
        "p50_ms": statistics.median(ms),
        "p99_ms": sorted(ms)[int(len(ms) * 0.99)] if len(ms) >= 100 else max(ms),
        "ops_per_sec": len(times) / total if total > 0 else 0,
    }


def _bulk_summary(count: int, elapsed: float) -> dict:
    return {
        "avg_ms": (elapsed / count) * 1000 if count > 0 else 0,
        "ops_per_sec": count / elapsed if elapsed > 0 else 0,
    }


# ── aerospike-py AsyncClient ────────────────────────────────


async def bench_async_client(
    host: str, port: int, count: int, concurrency: int
) -> dict:
    from aerospike import AsyncClient

    client = AsyncClient({"hosts": [(host, port)], "cluster_name": "docker"})
    await client.connect()

    results = {}
    sem = asyncio.Semaphore(concurrency)

    # Sequential PUT
    times = []
    for i in range(count):
        key = (NAMESPACE, SET_NAME, f"async_{i}")
        t0 = time.perf_counter()
        await client.put(key, {"name": f"user_{i}", "age": i, "score": i * 1.1})
        times.append(time.perf_counter() - t0)
    results["put_seq"] = _summarize(times)

    # Concurrent PUT
    t0 = time.perf_counter()

    async def _put(i):
        async with sem:
            await client.put(
                (NAMESPACE, SET_NAME, f"async_conc_{i}"),
                {"name": f"user_{i}", "age": i},
            )

    await asyncio.gather(*[_put(i) for i in range(count)])
    elapsed = time.perf_counter() - t0
    results["put_conc"] = _bulk_summary(count, elapsed)

    # Sequential GET
    times = []
    for i in range(count):
        key = (NAMESPACE, SET_NAME, f"async_{i}")
        t0 = time.perf_counter()
        await client.get(key)
        times.append(time.perf_counter() - t0)
    results["get_seq"] = _summarize(times)

    # Concurrent GET
    t0 = time.perf_counter()

    async def _get(i):
        async with sem:
            await client.get((NAMESPACE, SET_NAME, f"async_{i}"))

    await asyncio.gather(*[_get(i) for i in range(count)])
    elapsed = time.perf_counter() - t0
    results["get_conc"] = _bulk_summary(count, elapsed)

    # BATCH GET
    keys = [(NAMESPACE, SET_NAME, f"async_{i}") for i in range(count)]
    t0 = time.perf_counter()
    await client.get_many(keys)
    elapsed = time.perf_counter() - t0
    results["batch_get"] = _bulk_summary(count, elapsed)

    # Cleanup
    cleanup = [(NAMESPACE, SET_NAME, f"async_{i}") for i in range(count)]
    cleanup += [(NAMESPACE, SET_NAME, f"async_conc_{i}") for i in range(count)]
    await client.batch_remove(cleanup)
    await client.close()

    return results


# ── official C client sync baseline ──────────────────────────


def bench_c_sync(host: str, port: int, count: int) -> dict | None:
    try:
        import aerospike as aerospike_c  # noqa: F811
    except ImportError:
        return None

    client = aerospike_c.client({"hosts": [(host, port)]}).connect()

    results = {}

    # PUT
    times = []
    for i in range(count):
        key = (NAMESPACE, SET_NAME, f"c_async_{i}")
        t0 = time.perf_counter()
        client.put(key, {"name": f"user_{i}", "age": i, "score": i * 1.1})
        times.append(time.perf_counter() - t0)
    results["put_seq"] = _summarize(times)

    # GET
    times = []
    for i in range(count):
        key = (NAMESPACE, SET_NAME, f"c_async_{i}")
        t0 = time.perf_counter()
        client.get(key)
        times.append(time.perf_counter() - t0)
    results["get_seq"] = _summarize(times)

    # BATCH GET
    keys = [(NAMESPACE, SET_NAME, f"c_async_{i}") for i in range(count)]
    t0 = time.perf_counter()
    client.get_many(keys)
    elapsed = time.perf_counter() - t0
    results["batch_get"] = _bulk_summary(count, elapsed)

    # cleanup
    for i in range(count):
        client.remove((NAMESPACE, SET_NAME, f"c_async_{i}"))
    client.close()

    return results


# ── comparison output ────────────────────────────────────────


def _speedup(target: float, baseline: float) -> str:
    if target <= 0 or baseline <= 0:
        return "N/A"
    ratio = target / baseline
    if ratio >= 1.0:
        return f"{ratio:.2f}x faster"
    return f"{1 / ratio:.2f}x slower"


def print_comparison(async_res: dict, c_res: dict | None, concurrency: int):
    print()
    print("=" * 72)
    print("  Async Benchmark: aerospike-py AsyncClient vs official C client (sync)")
    print(f"  (concurrency={concurrency} for concurrent operations)")
    print("=" * 72)

    if c_res is not None:
        # Throughput comparison
        print(f"\n  Throughput (ops/sec) - higher is better")
        print(f"  {'':─<68}")
        print(
            f"  {'Operation':<14} | "
            f"{'aerospike-py':>14} | "
            f"{'official C':>14} | "
            f"{'Speedup':>16}"
        )
        print(f"  {'':─<68}")

        # Sequential comparisons
        for label, akey, ckey in [
            ("put (seq)", "put_seq", "put_seq"),
            ("get (seq)", "get_seq", "get_seq"),
            ("batch_get", "batch_get", "batch_get"),
        ]:
            a = async_res[akey]["ops_per_sec"]
            c = c_res[ckey]["ops_per_sec"]
            sp = _speedup(a, c)
            print(f"  {label:<14} | {a:>11,.0f}/s | {c:>11,.0f}/s | {sp:>16}")

        # Concurrent (no C equivalent)
        for label, akey in [("put (conc)", "put_conc"), ("get (conc)", "get_conc")]:
            a = async_res[akey]["ops_per_sec"]
            print(
                f"  {label:<14} | {a:>11,.0f}/s | {'(no async)':>14} | "
                f"{'N/A':>16}"
            )

        # Latency comparison (sequential only)
        print(f"\n  Avg Latency (ms) - lower is better")
        print(f"  {'':─<68}")
        print(
            f"  {'Operation':<14} | "
            f"{'aerospike-py':>14} | "
            f"{'official C':>14} | "
            f"{'Speedup':>16}"
        )
        print(f"  {'':─<68}")
        for label, akey, ckey in [
            ("put (seq)", "put_seq", "put_seq"),
            ("get (seq)", "get_seq", "get_seq"),
        ]:
            a = async_res[akey]["avg_ms"]
            c = c_res[ckey]["avg_ms"]
            sp = _speedup(c, a)  # latency: lower is faster → c/a
            print(f"  {label:<14} | {a:>12.3f}ms | {c:>12.3f}ms | {sp:>16}")

        # Async concurrency advantage
        print(f"\n  Concurrency Advantage (asyncio.gather, concurrency={concurrency})")
        print(f"  {'':─<68}")
        print(
            f"  {'Operation':<14} | "
            f"{'concurrent':>14} | "
            f"{'sequential':>14} | "
            f"{'Speedup':>16}"
        )
        print(f"  {'':─<68}")
        for label, conc_key, seq_key in [
            ("put", "put_conc", "put_seq"),
            ("get", "get_conc", "get_seq"),
        ]:
            conc = async_res[conc_key]["ops_per_sec"]
            seq = async_res[seq_key]["ops_per_sec"]
            sp = _speedup(conc, seq)
            print(f"  {label:<14} | {conc:>11,.0f}/s | {seq:>11,.0f}/s | {sp:>16}")

    else:
        print("\n  [!] Official C client not installed.")
        print("      pip install aerospike  to enable comparison.\n")
        print(f"  {'Operation':<14} | {'Throughput':>14} | {'Avg Latency':>14}")
        print(f"  {'':─<48}")
        for op, data in async_res.items():
            thr = f"{data['ops_per_sec']:,.0f}/s"
            lat = f"{data['avg_ms']:.3f}ms"
            print(f"  {op:<14} | {thr:>14} | {lat:>14}")

    print()


# ── main ─────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Async benchmark: aerospike-py vs official C client"
    )
    parser.add_argument("--count", type=int, default=1000)
    parser.add_argument("--concurrency", type=int, default=50)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=3000)
    args = parser.parse_args()

    print(
        f"Async Benchmark: {args.count} ops, concurrency={args.concurrency} "
        f"@ {args.host}:{args.port}\n"
    )

    print("Running aerospike-py AsyncClient ...")
    async_results = asyncio.run(
        bench_async_client(args.host, args.port, args.count, args.concurrency)
    )

    print("Running official C client (sync baseline) ...")
    c_results = bench_c_sync(args.host, args.port, args.count)

    print_comparison(async_results, c_results, args.concurrency)


if __name__ == "__main__":
    main()
