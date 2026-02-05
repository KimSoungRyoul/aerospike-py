"""Unified benchmark: aerospike-py vs official aerospike C client.

Compares three clients side-by-side:
  1. aerospike-py (Rust)        - sync Client
  2. official aerospike (C)     - sync client
  3. aerospike-py async (Rust)  - AsyncClient with asyncio.gather

Usage:
    python benchmark/bench_compare.py [--count N] [--concurrency C] [--host HOST] [--port PORT]

Requirements:
    pip install aerospike   # official C client (comparison target)
"""

import argparse
import asyncio
import statistics
import time

NAMESPACE = "test"
SET_NAME = "bench_cmp"

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
        "p50_ms": None,
        "p99_ms": None,
        "ops_per_sec": count / elapsed if elapsed > 0 else 0,
    }


# ── 1) aerospike-py sync (Rust) ─────────────────────────────


def bench_rust_sync(host: str, port: int, count: int) -> dict:
    import aerospike

    client = aerospike.client(
        {"hosts": [(host, port)], "cluster_name": "docker"}
    ).connect()

    results = {}
    prefix = "rs_"

    # PUT
    times = []
    for i in range(count):
        t0 = time.perf_counter()
        client.put((NAMESPACE, SET_NAME, f"{prefix}{i}"), {"n": f"u{i}", "a": i, "s": i * 1.1})
        times.append(time.perf_counter() - t0)
    results["put"] = _summarize(times)

    # GET
    times = []
    for i in range(count):
        t0 = time.perf_counter()
        client.get((NAMESPACE, SET_NAME, f"{prefix}{i}"))
        times.append(time.perf_counter() - t0)
    results["get"] = _summarize(times)

    # BATCH GET
    keys = [(NAMESPACE, SET_NAME, f"{prefix}{i}") for i in range(count)]
    t0 = time.perf_counter()
    client.get_many(keys)
    elapsed = time.perf_counter() - t0
    results["batch_get"] = _bulk_summary(count, elapsed)

    # SCAN
    scan = client.scan(NAMESPACE, SET_NAME)
    t0 = time.perf_counter()
    records = scan.results()
    elapsed = time.perf_counter() - t0
    results["scan"] = _bulk_summary(len(records) if records else 1, elapsed)

    # cleanup
    for i in range(count):
        client.remove((NAMESPACE, SET_NAME, f"{prefix}{i}"))
    client.close()

    return results


# ── 2) official aerospike C client ───────────────────────────


def bench_c_sync(host: str, port: int, count: int) -> dict | None:
    try:
        import aerospike as aerospike_c  # noqa: F811
    except ImportError:
        return None

    client = aerospike_c.client({"hosts": [(host, port)]}).connect()

    results = {}
    prefix = "cc_"

    # PUT
    times = []
    for i in range(count):
        t0 = time.perf_counter()
        client.put((NAMESPACE, SET_NAME, f"{prefix}{i}"), {"n": f"u{i}", "a": i, "s": i * 1.1})
        times.append(time.perf_counter() - t0)
    results["put"] = _summarize(times)

    # GET
    times = []
    for i in range(count):
        t0 = time.perf_counter()
        client.get((NAMESPACE, SET_NAME, f"{prefix}{i}"))
        times.append(time.perf_counter() - t0)
    results["get"] = _summarize(times)

    # BATCH GET
    keys = [(NAMESPACE, SET_NAME, f"{prefix}{i}") for i in range(count)]
    t0 = time.perf_counter()
    client.get_many(keys)
    elapsed = time.perf_counter() - t0
    results["batch_get"] = _bulk_summary(count, elapsed)

    # SCAN
    scan = client.scan(NAMESPACE, SET_NAME)
    t0 = time.perf_counter()
    records = scan.results()
    elapsed = time.perf_counter() - t0
    results["scan"] = _bulk_summary(len(records) if records else 1, elapsed)

    # cleanup
    for i in range(count):
        client.remove((NAMESPACE, SET_NAME, f"{prefix}{i}"))
    client.close()

    return results


# ── 3) aerospike-py async (Rust) ─────────────────────────────


async def bench_rust_async(host: str, port: int, count: int, concurrency: int) -> dict:
    from aerospike import AsyncClient

    client = AsyncClient({"hosts": [(host, port)], "cluster_name": "docker"})
    await client.connect()

    results = {}
    prefix = "ra_"
    sem = asyncio.Semaphore(concurrency)

    # PUT (concurrent)
    t0 = time.perf_counter()

    async def _put(i):
        async with sem:
            await client.put(
                (NAMESPACE, SET_NAME, f"{prefix}{i}"),
                {"n": f"u{i}", "a": i, "s": i * 1.1},
            )

    await asyncio.gather(*[_put(i) for i in range(count)])
    elapsed = time.perf_counter() - t0
    results["put"] = _bulk_summary(count, elapsed)

    # GET (concurrent)
    t0 = time.perf_counter()

    async def _get(i):
        async with sem:
            await client.get((NAMESPACE, SET_NAME, f"{prefix}{i}"))

    await asyncio.gather(*[_get(i) for i in range(count)])
    elapsed = time.perf_counter() - t0
    results["get"] = _bulk_summary(count, elapsed)

    # BATCH GET
    keys = [(NAMESPACE, SET_NAME, f"{prefix}{i}") for i in range(count)]
    t0 = time.perf_counter()
    await client.get_many(keys)
    elapsed = time.perf_counter() - t0
    results["batch_get"] = _bulk_summary(count, elapsed)

    # SCAN
    t0 = time.perf_counter()
    records = await client.scan(NAMESPACE, SET_NAME)
    elapsed = time.perf_counter() - t0
    results["scan"] = _bulk_summary(len(records) if records else 1, elapsed)

    # cleanup
    await client.batch_remove(
        [(NAMESPACE, SET_NAME, f"{prefix}{i}") for i in range(count)]
    )
    await client.close()

    return results


# ── comparison output ────────────────────────────────────────

COL_OP = 12
COL_VAL = 22
COL_SP = 16


def _speedup_latency(target: float, baseline: float) -> str:
    """target vs baseline latency. Lower target = faster."""
    if target <= 0 or baseline <= 0:
        return "-"
    ratio = baseline / target
    if ratio >= 1.0:
        return f"{ratio:.1f}x faster"
    return f"{1 / ratio:.1f}x slower"


def _speedup_throughput(target: float, baseline: float) -> str:
    """target vs baseline throughput. Higher target = faster."""
    if target <= 0 or baseline <= 0:
        return "-"
    ratio = target / baseline
    if ratio >= 1.0:
        return f"{ratio:.1f}x faster"
    return f"{1 / ratio:.1f}x slower"


def _fmt_ms(val: float | None) -> str:
    if val is None:
        return "-"
    return f"{val:.3f}ms"


def _fmt_ops(val: float | None) -> str:
    if val is None:
        return "-"
    return f"{val:,.0f}/s"


def _print_table(
    title: str,
    ops: list[str],
    rust: dict,
    c: dict | None,
    async_r: dict,
    metric: str,
    formatter,
    speedup_fn,
):
    has_c = c is not None

    print(f"\n  {title}")
    w = COL_OP + 2 + COL_VAL * 3 + (COL_SP * 2 if has_c else 0) + 12
    print(f"  {'':─<{w}}")

    # header
    h = f"  {'Operation':<{COL_OP}}"
    h += f" | {'aerospike-py (Rust)':>{COL_VAL}}"
    if has_c:
        h += f" | {'official aerospike (C)':>{COL_VAL}}"
    h += f" | {'aerospike-py async':>{COL_VAL}}"
    if has_c:
        h += f" | {'Rust vs C':>{COL_SP}}"
        h += f" | {'Async vs C':>{COL_SP}}"
    print(h)
    print(f"  {'':─<{w}}")

    for op in ops:
        rv = rust[op].get(metric)
        cv = c[op].get(metric) if has_c else None
        av = async_r[op].get(metric)

        line = f"  {op:<{COL_OP}}"
        line += f" | {formatter(rv):>{COL_VAL}}"
        if has_c:
            line += f" | {formatter(cv):>{COL_VAL}}"
        line += f" | {formatter(av):>{COL_VAL}}"

        if has_c and cv is not None:
            if rv is not None:
                line += f" | {speedup_fn(rv, cv):>{COL_SP}}"
            else:
                line += f" | {'-':>{COL_SP}}"
            if av is not None:
                line += f" | {speedup_fn(av, cv):>{COL_SP}}"
            else:
                line += f" | {'-':>{COL_SP}}"

        print(line)


def print_comparison(
    rust: dict, c: dict | None, async_r: dict, count: int, concurrency: int
):
    ops = ["put", "get", "batch_get", "scan"]

    print()
    print("=" * 90)
    print(f"  aerospike-py Benchmark  ({count:,} ops, async concurrency={concurrency})")
    print("=" * 90)

    if c is None:
        print("\n  [!] official aerospike (C) not installed. pip install aerospike")

    # Latency table
    _print_table(
        "Avg Latency (ms)  —  lower is better",
        ops, rust, c, async_r,
        metric="avg_ms",
        formatter=_fmt_ms,
        speedup_fn=_speedup_latency,
    )

    # Throughput table
    _print_table(
        "Throughput (ops/sec)  —  higher is better",
        ops, rust, c, async_r,
        metric="ops_per_sec",
        formatter=_fmt_ops,
        speedup_fn=_speedup_throughput,
    )

    # P50/P99 (only for per-op measured ones)
    pct_ops = [op for op in ops if rust[op].get("p50_ms") is not None]
    if pct_ops:
        print(f"\n  Tail Latency (ms)")
        w = COL_OP + 2 + 18 * 4 + 10
        print(f"  {'':─<{w}}")
        h = f"  {'Operation':<{COL_OP}}"
        h += f" | {'Rust p50':>16}"
        h += f" | {'Rust p99':>16}"
        if c is not None:
            h += f" | {'C p50':>16}"
            h += f" | {'C p99':>16}"
        print(h)
        print(f"  {'':─<{w}}")
        for op in pct_ops:
            line = f"  {op:<{COL_OP}}"
            line += f" | {_fmt_ms(rust[op]['p50_ms']):>16}"
            line += f" | {_fmt_ms(rust[op]['p99_ms']):>16}"
            if c is not None:
                line += f" | {_fmt_ms(c[op].get('p50_ms')):>16}"
                line += f" | {_fmt_ms(c[op].get('p99_ms')):>16}"
            print(line)

    print()


# ── main ─────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark: aerospike-py (Rust) vs official aerospike (C)"
    )
    parser.add_argument("--count", type=int, default=1000, help="Operations per test")
    parser.add_argument("--concurrency", type=int, default=50, help="Async concurrency")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=3000)
    args = parser.parse_args()

    print(f"Benchmark: {args.count:,} ops @ {args.host}:{args.port}")
    print(f"Async concurrency: {args.concurrency}\n")

    print("[1/3] aerospike-py sync (Rust) ...")
    rust = bench_rust_sync(args.host, args.port, args.count)

    print("[2/3] official aerospike sync (C) ...")
    c = bench_c_sync(args.host, args.port, args.count)
    if c is None:
        print("      -> not installed, skipping")

    print("[3/3] aerospike-py async (Rust) ...")
    async_r = asyncio.run(
        bench_rust_async(args.host, args.port, args.count, args.concurrency)
    )

    print_comparison(rust, c, async_r, args.count, args.concurrency)


if __name__ == "__main__":
    main()
