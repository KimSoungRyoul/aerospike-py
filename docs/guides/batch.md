# Batch Guide

Batch operations allow reading, writing, and deleting multiple records in a single network call.

## Batch Read (get_many)

Read multiple records at once:

```python
keys = [("test", "demo", f"user_{i}") for i in range(10)]
records = client.get_many(keys)

for key, meta, bins in records:
    if bins is not None:
        print(f"{key}: {bins}")
    else:
        print(f"{key}: not found")
```

## Batch Exists (exists_many)

Check existence of multiple records:

```python
keys = [("test", "demo", f"user_{i}") for i in range(10)]
results = client.exists_many(keys)

for key, meta in results:
    if meta is not None:
        print(f"{key}: exists (gen={meta['gen']})")
    else:
        print(f"{key}: not found")
```

## Batch Select (select_many)

Read specific bins from multiple records:

```python
keys = [("test", "demo", f"user_{i}") for i in range(10)]
records = client.select_many(keys, ["name", "email"])

for _, _, bins in records:
    if bins:
        print(bins)
```

## Batch Operate (batch_operate)

Execute operations on multiple records:

```python
keys = [("test", "demo", f"counter_{i}") for i in range(10)]
ops = [
    {"op": aerospike.OPERATOR_INCR, "bin": "views", "val": 1},
    {"op": aerospike.OPERATOR_READ, "bin": "views", "val": None},
]
results = client.batch_operate(keys, ops)

for _, _, bins in results:
    if bins:
        print(f"views: {bins['views']}")
```

## Batch Remove (batch_remove)

Delete multiple records:

```python
keys = [("test", "demo", f"temp_{i}") for i in range(100)]
results = client.batch_remove(keys)
```

## Async Batch Operations

```python
import asyncio
from aerospike import AsyncClient

async def main():
    client = AsyncClient({
        "hosts": [("127.0.0.1", 3000)],
        "cluster_name": "docker",
    })
    await client.connect()

    keys = [("test", "demo", f"user_{i}") for i in range(10)]

    # Batch read
    records = await client.get_many(keys)

    # Batch exists
    results = await client.exists_many(keys)

    # Batch remove
    await client.batch_remove(keys)

    await client.close()

asyncio.run(main())
```

## Best Practices

- **Batch size**: Keep batch sizes reasonable (100-5000 keys). Very large batches may timeout.
- **Timeouts**: Set appropriate timeouts for large batch operations via policy.
- **Error handling**: Individual records in a batch can fail independently. Check each result for `None` bins.
- **Async advantage**: `AsyncClient.get_many` is particularly efficient as it leverages async I/O.
