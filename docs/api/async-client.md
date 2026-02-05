# AsyncClient

The `AsyncClient` provides a fully asynchronous API for Aerospike operations using Python's `asyncio`.

## Creating an AsyncClient

```python
import asyncio
from aerospike_py import AsyncClient

async def main():
    client = AsyncClient({
        "hosts": [("127.0.0.1", 3000)],
        "cluster_name": "docker",
    })
    await client.connect()
    # ... operations ...
    await client.close()

asyncio.run(main())
```

## Connection

### `async connect(username=None, password=None)`

Connect to the Aerospike cluster.

```python
await client.connect()
await client.connect("admin", "admin")
```

### `is_connected()`

Returns `True` if connected. This is a synchronous method.

```python
if client.is_connected():
    print("Connected")
```

### `async close()`

Close the connection.

```python
await client.close()
```

### `async get_node_names()`

Returns cluster node names.

```python
nodes = await client.get_node_names()
```

## CRUD Operations

### `async put(key, bins, meta=None, policy=None)`

Write a record.

```python
key = ("test", "demo", "user1")
await client.put(key, {"name": "Alice", "age": 30})
await client.put(key, {"x": 1}, meta={"ttl": 300})
```

### `async get(key, policy=None)`

Read a record. Returns `(key, meta, bins)`.

```python
_, meta, bins = await client.get(key)
```

### `async select(key, bins, policy=None)`

Read specific bins.

```python
_, meta, bins = await client.select(key, ["name"])
```

### `async exists(key, policy=None)`

Check if a record exists. Returns `(key, meta)`.

```python
_, meta = await client.exists(key)
```

### `async remove(key, meta=None, policy=None)`

Delete a record.

```python
await client.remove(key)
```

### `async touch(key, val=0, meta=None, policy=None)`

Reset TTL.

```python
await client.touch(key, val=300)
```

### `async increment(key, bin, offset, meta=None, policy=None)`

Increment a bin value.

```python
await client.increment(key, "counter", 1)
```

## Multi-Operation

### `async operate(key, ops, meta=None, policy=None)`

Execute multiple operations atomically.

```python
ops = [
    {"op": aerospike.OPERATOR_INCR, "bin": "counter", "val": 1},
    {"op": aerospike.OPERATOR_READ, "bin": "counter", "val": None},
]
_, meta, bins = await client.operate(key, ops)
```

## Batch Operations

### `async get_many(keys, policy=None)`

Read multiple records concurrently.

```python
keys = [("test", "demo", f"user{i}") for i in range(10)]
records = await client.get_many(keys)
```

### `async exists_many(keys, policy=None)`

Check existence of multiple records.

```python
results = await client.exists_many(keys)
```

### `async batch_remove(keys, policy=None)`

Delete multiple records.

```python
await client.batch_remove(keys)
```

## Scan

### `async scan(namespace, set_name, policy=None)`

Scan all records in a namespace/set.

```python
records = await client.scan("test", "demo")
for key, meta, bins in records:
    print(bins)
```

## Truncate

### `async truncate(namespace, set_name, nanos=0, policy=None)`

Remove all records in a namespace/set.

```python
await client.truncate("test", "demo")
```

## UDF

### `async udf_put(filename, udf_type=0, policy=None)`

Register a Lua UDF module.

```python
await client.udf_put("my_udf.lua")
```

### `async udf_remove(module, policy=None)`

Remove a UDF module.

```python
await client.udf_remove("my_udf")
```

### `async apply(key, module, function, args=None, policy=None)`

Execute a UDF on a record.

```python
result = await client.apply(key, "my_udf", "my_function", [1, "hello"])
```

## Concurrency Patterns

### Parallel Writes with `asyncio.gather`

```python
keys = [("test", "demo", f"item_{i}") for i in range(100)]
tasks = [client.put(k, {"idx": i}) for i, k in enumerate(keys)]
await asyncio.gather(*tasks)
```

### Parallel Reads

```python
keys = [("test", "demo", f"item_{i}") for i in range(100)]
tasks = [client.get(k) for k in keys]
results = await asyncio.gather(*tasks, return_exceptions=True)
```

### Mixed Operations

```python
async def process_user(client, user_id):
    key = ("test", "users", user_id)
    _, _, bins = await client.get(key)
    bins["visits"] = bins.get("visits", 0) + 1
    await client.put(key, bins)
    return bins

results = await asyncio.gather(*[
    process_user(client, f"user_{i}")
    for i in range(10)
])
```
