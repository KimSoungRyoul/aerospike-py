"""Synchronous benchmark: aerospike-py (Rust) vs aerospike (C client).

Usage:
    python benchmark/bench_sync.py [--count N] [--host HOST] [--port PORT]
"""

import argparse
import statistics
import time

NAMESPACE = "test"
SET_NAME = "bench"


def bench_aerospike_py(host: str, port: int, count: int) -> dict:
    """Benchmark aerospike-py (this project, Rust-based)."""
    import aerospike

    client = aerospike.client(
        {"hosts": [(host, port)], "cluster_name": "docker"}
    ).connect()

    results = {}

    # -- PUT --
    times = []
    for i in range(count):
        key = (NAMESPACE, SET_NAME, f"rust_{i}")
        start = time.perf_counter()
        client.put(key, {"name": f"user_{i}", "age": i, "score": i * 1.1})
        times.append(time.perf_counter() - start)
    results["put"] = _summarize(times)

    # -- GET --
    times = []
    for i in range(count):
        key = (NAMESPACE, SET_NAME, f"rust_{i}")
        start = time.perf_counter()
        client.get(key)
        times.append(time.perf_counter() - start)
    results["get"] = _summarize(times)

    # -- BATCH GET --
    keys = [(NAMESPACE, SET_NAME, f"rust_{i}") for i in range(count)]
    start = time.perf_counter()
    client.get_many(keys)
    elapsed = time.perf_counter() - start
    results["batch_get"] = {
        "total_ms": elapsed * 1000,
        "ops_per_sec": count / elapsed,
    }

    # -- SCAN --
    scan = client.scan(NAMESPACE, SET_NAME)
    start = time.perf_counter()
    records = scan.results()
    elapsed = time.perf_counter() - start
    results["scan"] = {
        "total_ms": elapsed * 1000,
        "records": len(records),
        "ops_per_sec": len(records) / elapsed if elapsed > 0 else 0,
    }

    # Cleanup
    for i in range(count):
        client.remove((NAMESPACE, SET_NAME, f"rust_{i}"))
    client.close()

    return results


def bench_aerospike_c(host: str, port: int, count: int) -> dict | None:
    """Benchmark aerospike (C client from PyPI)."""
    try:
        import aerospike as aerospike_c
    except ImportError:
        print("[SKIP] aerospike (C client) not installed. pip install aerospike")
        return None

    config = {"hosts": [(host, port)]}
    client = aerospike_c.client(config).connect()

    results = {}

    # -- PUT --
    times = []
    for i in range(count):
        key = (NAMESPACE, SET_NAME, f"c_{i}")
        start = time.perf_counter()
        client.put(key, {"name": f"user_{i}", "age": i, "score": i * 1.1})
        times.append(time.perf_counter() - start)
    results["put"] = _summarize(times)

    # -- GET --
    times = []
    for i in range(count):
        key = (NAMESPACE, SET_NAME, f"c_{i}")
        start = time.perf_counter()
        client.get(key)
        times.append(time.perf_counter() - start)
    results["get"] = _summarize(times)

    # -- BATCH GET --
    keys = [(NAMESPACE, SET_NAME, f"c_{i}") for i in range(count)]
    start = time.perf_counter()
    client.get_many(keys)
    elapsed = time.perf_counter() - start
    results["batch_get"] = {
        "total_ms": elapsed * 1000,
        "ops_per_sec": count / elapsed,
    }

    # -- SCAN --
    scan = client.scan(NAMESPACE, SET_NAME)
    start = time.perf_counter()
    records = scan.results()
    elapsed = time.perf_counter() - start
    results["scan"] = {
        "total_ms": elapsed * 1000,
        "records": len(records),
        "ops_per_sec": len(records) / elapsed if elapsed > 0 else 0,
    }

    # Cleanup
    for i in range(count):
        client.remove((NAMESPACE, SET_NAME, f"c_{i}"))
    client.close()

    return results


def _summarize(times: list[float]) -> dict:
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


def print_results(name: str, results: dict):
    print(f"\n{'=' * 60}")
    print(f"  {name}")
    print(f"{'=' * 60}")
    for op, data in results.items():
        print(f"\n  [{op}]")
        for k, v in data.items():
            if isinstance(v, float):
                print(f"    {k:>15s}: {v:>12.2f}")
            else:
                print(f"    {k:>15s}: {v:>12}")


def main():
    parser = argparse.ArgumentParser(description="Sync benchmark")
    parser.add_argument("--count", type=int, default=1000, help="Number of operations")
    parser.add_argument("--host", default="127.0.0.1", help="Aerospike host")
    parser.add_argument("--port", type=int, default=3000, help="Aerospike port")
    args = parser.parse_args()

    print(f"Benchmark: {args.count} operations @ {args.host}:{args.port}")

    rust_results = bench_aerospike_py(args.host, args.port, args.count)
    print_results("aerospike-py (Rust/PyO3)", rust_results)

    c_results = bench_aerospike_c(args.host, args.port, args.count)
    if c_results:
        print_results("aerospike (C client)", c_results)


if __name__ == "__main__":
    main()
