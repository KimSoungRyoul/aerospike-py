"""Async benchmark: aerospike-py AsyncClient with asyncio.gather concurrency.

Usage:
    python benchmark/bench_async.py [--count N] [--concurrency C] [--host HOST] [--port PORT]
"""

import argparse
import asyncio
import time


NAMESPACE = "test"
SET_NAME = "bench_async"


async def bench_async(host: str, port: int, count: int, concurrency: int) -> dict:
    """Benchmark AsyncClient with varying concurrency."""
    from aerospike import AsyncClient

    client = AsyncClient({"hosts": [(host, port)], "cluster_name": "docker"})
    await client.connect()

    results = {}

    # -- Sequential PUT --
    times = []
    for i in range(count):
        key = (NAMESPACE, SET_NAME, f"async_{i}")
        start = time.perf_counter()
        await client.put(key, {"name": f"user_{i}", "age": i, "score": i * 1.1})
        times.append(time.perf_counter() - start)
    results["put_sequential"] = _summarize(times)

    # -- Concurrent PUT (asyncio.gather) --
    start = time.perf_counter()
    sem = asyncio.Semaphore(concurrency)

    async def _put(i):
        async with sem:
            key = (NAMESPACE, SET_NAME, f"async_conc_{i}")
            await client.put(key, {"name": f"user_{i}", "age": i})

    await asyncio.gather(*[_put(i) for i in range(count)])
    elapsed = time.perf_counter() - start
    results["put_concurrent"] = {
        "count": count,
        "concurrency": concurrency,
        "total_ms": elapsed * 1000,
        "ops_per_sec": count / elapsed if elapsed > 0 else 0,
    }

    # -- Sequential GET --
    times = []
    for i in range(count):
        key = (NAMESPACE, SET_NAME, f"async_{i}")
        start = time.perf_counter()
        await client.get(key)
        times.append(time.perf_counter() - start)
    results["get_sequential"] = _summarize(times)

    # -- Concurrent GET (asyncio.gather) --
    start = time.perf_counter()

    async def _get(i):
        async with sem:
            key = (NAMESPACE, SET_NAME, f"async_{i}")
            await client.get(key)

    await asyncio.gather(*[_get(i) for i in range(count)])
    elapsed = time.perf_counter() - start
    results["get_concurrent"] = {
        "count": count,
        "concurrency": concurrency,
        "total_ms": elapsed * 1000,
        "ops_per_sec": count / elapsed if elapsed > 0 else 0,
    }

    # -- Batch GET --
    keys = [(NAMESPACE, SET_NAME, f"async_{i}") for i in range(count)]
    start = time.perf_counter()
    await client.get_many(keys)
    elapsed = time.perf_counter() - start
    results["batch_get"] = {
        "total_ms": elapsed * 1000,
        "ops_per_sec": count / elapsed if elapsed > 0 else 0,
    }

    # -- Scan --
    start = time.perf_counter()
    records = await client.scan(NAMESPACE, SET_NAME)
    elapsed = time.perf_counter() - start
    results["scan"] = {
        "total_ms": elapsed * 1000,
        "records": len(records),
        "ops_per_sec": len(records) / elapsed if elapsed > 0 else 0,
    }

    # Cleanup
    cleanup_keys = [(NAMESPACE, SET_NAME, f"async_{i}") for i in range(count)]
    cleanup_keys += [(NAMESPACE, SET_NAME, f"async_conc_{i}") for i in range(count)]
    await client.batch_remove(cleanup_keys)
    await client.close()

    return results


def _summarize(times: list[float]) -> dict:
    import statistics

    ms = [t * 1000 for t in times]
    total = sum(times)
    return {
        "count": len(times),
        "total_ms": total * 1000,
        "avg_ms": statistics.mean(ms),
        "p50_ms": statistics.median(ms),
        "p99_ms": sorted(ms)[int(len(ms) * 0.99)] if len(ms) >= 100 else max(ms),
        "ops_per_sec": len(times) / total if total > 0 else 0,
    }


def print_results(results: dict):
    print(f"\n{'=' * 60}")
    print(f"  aerospike-py AsyncClient")
    print(f"{'=' * 60}")
    for op, data in results.items():
        print(f"\n  [{op}]")
        for k, v in data.items():
            if isinstance(v, float):
                print(f"    {k:>15s}: {v:>12.2f}")
            else:
                print(f"    {k:>15s}: {v:>12}")


def main():
    parser = argparse.ArgumentParser(description="Async benchmark")
    parser.add_argument("--count", type=int, default=1000, help="Number of operations")
    parser.add_argument(
        "--concurrency", type=int, default=50, help="Max concurrent tasks"
    )
    parser.add_argument("--host", default="127.0.0.1", help="Aerospike host")
    parser.add_argument("--port", type=int, default=3000, help="Aerospike port")
    args = parser.parse_args()

    print(
        f"Async Benchmark: {args.count} ops, concurrency={args.concurrency} "
        f"@ {args.host}:{args.port}"
    )

    results = asyncio.run(
        bench_async(args.host, args.port, args.count, args.concurrency)
    )
    print_results(results)


if __name__ == "__main__":
    main()
