# aerospike-py

[![Python](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/downloads/)
[![Rust](https://img.shields.io/badge/rust-stable-orange.svg)](https://www.rust-lang.org/)
[![PyO3](https://img.shields.io/badge/PyO3-0.23-green.svg)](https://pyo3.rs/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/KimSoungRyoul/aerospike-py.svg)](https://github.com/KimSoungRyoul/aerospike-py/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/KimSoungRyoul/aerospike-py.svg)](https://github.com/KimSoungRyoul/aerospike-py/issues)

Aerospike Python Client built with PyO3 + Rust. Drop-in replacement for [aerospike-client-python](https://github.com/aerospike/aerospike-client-python) powered by the [Aerospike Rust Client v2](https://github.com/aerospike/aerospike-client-rust).

## Features

- Sync and Async (`AsyncClient`) API
- CRUD, Batch, Query/Scan, UDF, Admin, Index, Truncate
- Full type stubs (`.pyi`) for IDE autocompletion
- 130+ tests (unit + integration + scenario)

## Quickstart

### Prerequisites

- Python 3.13+
- Rust toolchain (rustup)
- Running Aerospike server (or Docker)

### Install (from source)

```bash
git clone https://github.com/<your-org>/aerospike-py.git
cd aerospike-py

python -m venv .venv
source .venv/bin/activate
pip install maturin

maturin develop
```

### Start Aerospike Server (Docker)

```bash
docker run -d --name aerospike \
  -p 3000:3000 -p 3001:3001 -p 3002:3002 \
  -e "NAMESPACE=test" \
  -e "CLUSTER_NAME=docker" \
  aerospike/aerospike-server
```

### Basic Usage (Sync)

```python
import aerospike

# Connect
client = aerospike.client({
    "hosts": [("127.0.0.1", 3000)],
    "cluster_name": "docker",
}).connect()

# Write
key = ("test", "demo", "user1")
client.put(key, {"name": "Alice", "age": 30})

# Read
_, meta, bins = client.get(key)
print(bins)  # {'name': 'Alice', 'age': 30}

# Update
client.increment(key, "age", 1)

# Exists
_, meta = client.exists(key)
print(meta)  # {'gen': 3, 'ttl': ...}

# Batch read
keys = [("test", "demo", f"user{i}") for i in range(1, 4)]
results = client.get_many(keys)

# Operate (atomic multi-op)
ops = [
    {"op": aerospike.OPERATOR_INCR, "bin": "age", "val": 1},
    {"op": aerospike.OPERATOR_READ, "bin": "age", "val": None},
]
_, _, bins = client.operate(key, ops)
print(bins["age"])  # 32

# Query with secondary index
client.index_integer_create("test", "demo", "age", "age_idx")

query = client.query("test", "demo")
query.where(aerospike.predicates.between("age", 25, 35))
records = query.results()

# Scan
scan = client.scan("test", "demo")
all_records = scan.results()

# Delete
client.remove(key)

# Close
client.close()
```

### Basic Usage (Async)

```python
import asyncio
from aerospike import AsyncClient

async def main():
    client = AsyncClient({
        "hosts": [("127.0.0.1", 3000)],
        "cluster_name": "docker",
    })
    await client.connect()

    key = ("test", "demo", "user1")
    await client.put(key, {"name": "Bob", "age": 25})

    _, meta, bins = await client.get(key)
    print(bins)

    # Concurrent operations
    keys = [("test", "demo", f"item_{i}") for i in range(10)]
    tasks = [client.put(k, {"idx": i}) for i, k in enumerate(keys)]
    await asyncio.gather(*tasks)

    results = await client.get_many(keys)

    await client.close()

asyncio.run(main())
```

### Policies and Metadata

```python
# Write with TTL (seconds)
client.put(key, {"val": 1}, meta={"ttl": 300})

# Write with key send policy
client.put(key, {"val": 1}, policy={"key": aerospike.POLICY_KEY_SEND})

# Create only (fail if exists)
client.put(key, bins, policy={"exists": aerospike.POLICY_EXISTS_CREATE_ONLY})

# Optimistic locking with generation check
_, meta, bins = client.get(key)
client.put(key, {"val": bins["val"] + 1},
           meta={"gen": meta["gen"]},
           policy={"gen": aerospike.POLICY_GEN_EQ})
```

### UDF (User Defined Functions)

```python
# Register a Lua UDF
client.udf_put("my_udf.lua")

# Execute on a record
result = client.apply(key, "my_udf", "my_function", [arg1, arg2])

# Remove UDF
client.udf_remove("my_udf")
```

### Admin Operations

```python
# User management (requires security-enabled server)
client.admin_create_user("new_user", "password", ["read-write"])
client.admin_grant_roles("new_user", ["sys-admin"])
client.admin_drop_user("new_user")

# Role management
client.admin_create_role("custom_role", [
    {"code": aerospike.PRIV_READ, "ns": "test", "set": "demo"}
])
client.admin_drop_role("custom_role")
```

## Performance

Benchmark: **5,000 ops x 100 rounds**, warmup=200, async concurrency=50, Aerospike CE (Docker)
> Environment: Apple M4 Pro, 24 GB RAM, macOS 26.2

### Latency (ms) — lower is better

| Operation | aerospike-py (Rust) | official aerospike (C) | aerospike-py async (Rust) | Rust vs C | Async vs C |
| --------- | ------------------: | ---------------------: | ------------------------: | --------: | ---------: |
| put | 0.140 | 0.139 | 0.058 | 1.0x | 2.4x faster |
| get | 0.141 | 0.141 | 0.063 | 1.0x | 2.2x faster |
| batch_get | 0.011 | 0.011 | 0.011 | 1.0x | 1.0x |
| scan | 0.009 | 0.009 | 0.010 | 1.0x | 1.0x |

### Throughput (ops/sec) — higher is better

| Operation | aerospike-py (Rust) | official aerospike (C) | aerospike-py async (Rust) | Rust vs C | Async vs C |
| --------- | ------------------: | ---------------------: | ------------------------: | --------: | ---------: |
| put | 7,143 | 7,214 | 17,284 | 1.0x | 2.4x faster |
| get | 7,087 | 7,112 | 15,783 | 1.0x | 2.2x faster |
| batch_get | 91,049 | 90,984 | 89,717 | 1.0x | 1.0x |
| scan | 106,215 | 106,491 | 101,905 | 1.0x | 1.0x |

### Tail Latency (ms)

| Operation | Rust p50 | Rust p99 | C p50 | C p99 |
| --------- | -------: | -------: | ----: | ----: |
| put | 0.137 | 0.197 | 0.136 | 0.193 |
| get | 0.138 | 0.200 | 0.138 | 0.200 |

> **Summary**: Sync performance is on par with the official C client. With `AsyncClient` + `asyncio.gather`, throughput improves by **2.4x for put and 2.2x for get**.
> Batch/scan are server I/O-bound, so client implementation makes little difference.
>
> Run the benchmark yourself: `bash benchmark/run_all.sh 5000 100`

## Contributing

### Local Development Setup

```bash
# Clone
git clone https://github.com/<your-org>/aerospike-py.git
cd aerospike-py

# Python venv
python -m venv .venv
source .venv/bin/activate

# Install build tools and test dependencies
pip install maturin pytest pytest-asyncio

# Build (debug mode, fast iteration)
maturin develop

# Verify
python -c "import aerospike; print(aerospike.__version__)"
```

### Project Structure

```
aerospike-py/
├── pyproject.toml          # maturin build config
├── Cargo.toml              # Rust workspace root
├── rust/
│   ├── Cargo.toml          # PyO3 crate
│   └── src/
│       ├── lib.rs          # #[pymodule] entry point
│       ├── client.rs       # Sync Client
│       ├── async_client.rs # Async Client
│       ├── query.rs        # Query / Scan
│       ├── operations.rs   # Operation mapping
│       ├── errors.rs       # Error → Exception mapping
│       ├── constants.rs    # 130+ constants
│       ├── runtime.rs      # Global Tokio runtime
│       ├── types/          # Key, Value, Record, Bin, Host converters
│       └── policy/         # Policy dict → Rust struct parsers
├── src/aerospike/
│   ├── __init__.py         # Python package, re-exports, Client wrapper
│   ├── __init__.pyi        # Type stubs
│   ├── exception.py        # Exception hierarchy re-exports
│   ├── predicates.py       # Query predicate helpers
│   └── py.typed            # PEP 561 marker
└── tests/
    ├── unit/               # No server needed
    └── integration/        # Requires Aerospike server
```

### Build Commands

```bash
# Development build (debug, fast)
maturin develop

# Release build (optimized)
maturin develop --release

# Build wheel
maturin build --release
```

### Running Tests

Tests require a running Aerospike server. Start one with Docker:

```bash
docker run -d --name aerospike \
  -p 3000:3000 \
  -e "NAMESPACE=test" \
  -e "CLUSTER_NAME=docker" \
  aerospike/aerospike-server
```

Then run:

```bash
# All tests
pytest tests/ -v

# Unit tests only (no server needed)
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Specific test file
pytest tests/integration/test_scenarios.py -v

# With output
pytest tests/ -v -s
```

### Making Changes

1. **Rust code** (`rust/src/`): Edit, then `maturin develop` to rebuild.
2. **Python code** (`src/aerospike/`): Changes apply immediately (no rebuild needed).
3. **Tests**: Add to `tests/unit/` or `tests/integration/` as appropriate.

### Architecture Notes

- **Sync Client**: Uses a global Tokio runtime (`runtime.rs`). All async Rust calls are wrapped with `py.allow_threads(|| RUNTIME.block_on(...))` to release the GIL.
- **Async Client**: Uses `pyo3_async_runtimes::tokio::future_into_py()` to return Python coroutines directly.
- **Type conversion**: Python types are converted to/from Rust `Value` enum in `types/value.rs`. Keys, records, bins, and policies each have dedicated conversion modules.
- **Error mapping**: Rust `aerospike_core::Error` variants are mapped to the Python exception hierarchy in `errors.rs`.

## License

Apache License 2.0 — see [LICENSE](LICENSE) for details.
