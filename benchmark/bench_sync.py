"""Sync benchmark: aerospike-py (Rust) vs aerospike (official C client).

Measures latency and throughput for put/get/batch_get/scan,
then prints a side-by-side comparison with speedup ratios.

Usage:
    python benchmark/bench_sync.py [--count N] [--host HOST] [--port PORT]

Requirements:
    pip install aerospike   # official C client (comparison target)
"""

import argparse
import statistics
import time

NAMESPACE = "test"
SET_NAME = "bench_sync"


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
        "avg_ms": (elapsed / count) * 1000,
        "p50_ms": None,
        "p99_ms": None,
        "ops_per_sec": count / elapsed if elapsed > 0 else 0,
    }


# ── aerospike-py (Rust) ─────────────────────────────────────


def bench_rust(host: str, port: int, count: int) -> dict:
    import aerospike

    client = aerospike.client(
        {"hosts": [(host, port)], "cluster_name": "docker"}
    ).connect()

    results = {}

    # PUT
    times = []
    for i in range(count):
        key = (NAMESPACE, SET_NAME, f"rust_{i}")
        t0 = time.perf_counter()
        client.put(key, {"name": f"user_{i}", "age": i, "score": i * 1.1})
        times.append(time.perf_counter() - t0)
    results["put"] = _summarize(times)

    # GET
    times = []
    for i in range(count):
        key = (NAMESPACE, SET_NAME, f"rust_{i}")
        t0 = time.perf_counter()
        client.get(key)
        times.append(time.perf_counter() - t0)
    results["get"] = _summarize(times)

    # BATCH GET
    keys = [(NAMESPACE, SET_NAME, f"rust_{i}") for i in range(count)]
    t0 = time.perf_counter()
    client.get_many(keys)
    elapsed = time.perf_counter() - t0
    results["batch_get"] = _bulk_summary(count, elapsed)

    # SCAN
    scan = client.scan(NAMESPACE, SET_NAME)
    t0 = time.perf_counter()
    records = scan.results()
    elapsed = time.perf_counter() - t0
    results["scan"] = _bulk_summary(len(records), elapsed)

    # cleanup
    for i in range(count):
        client.remove((NAMESPACE, SET_NAME, f"rust_{i}"))
    client.close()

    return results


# ── aerospike official C client ──────────────────────────────


def bench_c(host: str, port: int, count: int) -> dict | None:
    try:
        import aerospike as aerospike_c  # noqa: F811
    except ImportError:
        return None

    config = {"hosts": [(host, port)]}
    client = aerospike_c.client(config).connect()

    results = {}

    # PUT
    times = []
    for i in range(count):
        key = (NAMESPACE, SET_NAME, f"c_{i}")
        t0 = time.perf_counter()
        client.put(key, {"name": f"user_{i}", "age": i, "score": i * 1.1})
        times.append(time.perf_counter() - t0)
    results["put"] = _summarize(times)

    # GET
    times = []
    for i in range(count):
        key = (NAMESPACE, SET_NAME, f"c_{i}")
        t0 = time.perf_counter()
        client.get(key)
        times.append(time.perf_counter() - t0)
    results["get"] = _summarize(times)

    # BATCH GET
    keys = [(NAMESPACE, SET_NAME, f"c_{i}") for i in range(count)]
    t0 = time.perf_counter()
    client.get_many(keys)
    elapsed = time.perf_counter() - t0
    results["batch_get"] = _bulk_summary(count, elapsed)

    # SCAN
    scan = client.scan(NAMESPACE, SET_NAME)
    t0 = time.perf_counter()
    records = scan.results()
    elapsed = time.perf_counter() - t0
    results["scan"] = _bulk_summary(len(records), elapsed)

    # cleanup
    for i in range(count):
        client.remove((NAMESPACE, SET_NAME, f"c_{i}"))
    client.close()

    return results


# ── comparison output ────────────────────────────────────────


def _speedup(c_val: float, rust_val: float) -> str:
    """Return speedup string like '2.3x faster' or '0.8x slower'."""
    if rust_val <= 0 or c_val <= 0:
        return "N/A"
    ratio = c_val / rust_val
    if ratio >= 1.0:
        return f"{ratio:.2f}x faster"
    return f"{1 / ratio:.2f}x slower"


def print_comparison(rust: dict, c: dict | None):
    ops = ["put", "get", "batch_get", "scan"]

    # Header
    print()
    if c is not None:
        hdr = (
            f"{'Operation':<12} | "
            f"{'aerospike-py':>14} | "
            f"{'official C':>14} | "
            f"{'Speedup':>14}"
        )
        sep = "-" * len(hdr)
        print(sep)
        print("  Sync Benchmark: aerospike-py (Rust) vs official C client")
        print(sep)

        # avg latency table
        print(f"\n  Avg Latency (ms) - lower is better")
        print(f"  {'':─<60}")
        print(f"  {hdr}")
        print(f"  {'':─<60}")
        for op in ops:
            r = rust[op]["avg_ms"]
            cv = c[op]["avg_ms"]
            sp = _speedup(cv, r)  # latency: lower = faster, so c/rust
            print(f"  {op:<12} | {r:>12.3f}ms | {cv:>12.3f}ms | {sp:>14}")

        # throughput table
        print(f"\n  Throughput (ops/sec) - higher is better")
        print(f"  {'':─<60}")
        print(f"  {hdr}")
        print(f"  {'':─<60}")
        for op in ops:
            r = rust[op]["ops_per_sec"]
            cv = c[op]["ops_per_sec"]
            sp = _speedup(r, cv)  # throughput: higher = faster, so rust/c
            print(
                f"  {op:<12} | {r:>11,.0f}/s | {cv:>11,.0f}/s | {sp:>14}"
            )

        # percentile table (only for ops with percentiles)
        pct_ops = [op for op in ops if rust[op].get("p50_ms") is not None]
        if pct_ops:
            print(f"\n  P50 / P99 Latency (ms)")
            print(f"  {'':─<74}")
            phdr = (
                f"{'Operation':<12} | "
                f"{'aerospike-py p50':>16} | "
                f"{'C client p50':>14} | "
                f"{'aerospike-py p99':>16} | "
                f"{'C client p99':>14}"
            )
            print(f"  {phdr}")
            print(f"  {'':─<74}")
            for op in pct_ops:
                rp50 = rust[op]["p50_ms"]
                cp50 = c[op]["p50_ms"]
                rp99 = rust[op]["p99_ms"]
                cp99 = c[op]["p99_ms"]
                print(
                    f"  {op:<12} | "
                    f"{rp50:>14.3f}ms | {cp50:>12.3f}ms | "
                    f"{rp99:>14.3f}ms | {cp99:>12.3f}ms"
                )
    else:
        print("=" * 60)
        print("  [!] Official C client not installed.")
        print("      pip install aerospike  to enable comparison.")
        print("=" * 60)
        print("\n  aerospike-py results (standalone):")
        print(f"  {'Operation':<12} | {'Avg Latency':>14} | {'Throughput':>14}")
        print(f"  {'':─<48}")
        for op in ops:
            r = rust[op]
            print(
                f"  {op:<12} | {r['avg_ms']:>12.3f}ms | {r['ops_per_sec']:>11,.0f}/s"
            )

    print()


# ── main ─────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Sync benchmark: aerospike-py vs official C client"
    )
    parser.add_argument("--count", type=int, default=1000)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=3000)
    args = parser.parse_args()

    print(f"Sync Benchmark: {args.count} ops @ {args.host}:{args.port}\n")

    print("Running aerospike-py (Rust) ...")
    rust_results = bench_rust(args.host, args.port, args.count)

    print("Running official C client ...")
    c_results = bench_c(args.host, args.port, args.count)

    print_comparison(rust_results, c_results)


if __name__ == "__main__":
    main()
