# CRUD Guide

## Keys

Every record is identified by a key tuple: `(namespace, set, primary_key)`.

```python
key = ("test", "demo", "user1")      # string PK
key = ("test", "demo", 12345)         # integer PK
key = ("test", "demo", b"\x01\x02")   # bytes PK
```

## Write (Put)

```python
import aerospike_py as aerospike

client = aerospike.client({"hosts": [("127.0.0.1", 3000)]}).connect()

key = ("test", "demo", "user1")

# Simple write
client.put(key, {"name": "Alice", "age": 30})

# Supported bin value types
client.put(key, {
    "str_bin": "hello",
    "int_bin": 42,
    "float_bin": 3.14,
    "bytes_bin": b"\x00\x01\x02",
    "list_bin": [1, 2, 3],
    "map_bin": {"nested": "dict"},
    "bool_bin": True,
    "none_bin": None,
})
```

### Write with TTL

```python
# TTL in seconds
client.put(key, {"val": 1}, meta={"ttl": 300})

# Never expire
client.put(key, {"val": 1}, meta={"ttl": aerospike.TTL_NEVER_EXPIRE})
```

### Write Policies

```python
# Create only (fails if record exists)
client.put(key, bins, policy={"exists": aerospike.POLICY_EXISTS_CREATE_ONLY})

# Replace only (fails if record doesn't exist)
client.put(key, bins, policy={"exists": aerospike.POLICY_EXISTS_REPLACE_ONLY})

# Send key to server (stored with record)
client.put(key, bins, policy={"key": aerospike.POLICY_KEY_SEND})
```

## Read (Get)

```python
key, meta, bins = client.get(("test", "demo", "user1"))
# key  = ("test", "demo", "user1") or None
# meta = {"gen": 1, "ttl": 2591998}
# bins = {"name": "Alice", "age": 30}
```

### Read Specific Bins (Select)

```python
_, meta, bins = client.select(key, ["name"])
# bins = {"name": "Alice"}
```

## Check Existence

```python
_, meta = client.exists(key)
if meta is not None:
    print(f"Record exists, gen={meta['gen']}")
else:
    print("Record not found")
```

## Update (Increment, Append, Prepend)

```python
# Increment integer bin
client.increment(key, "age", 1)

# Increment float bin
client.increment(key, "score", 0.5)

# Append to string
client.append(key, "name", " Smith")

# Prepend to string
client.prepend(key, "greeting", "Hello, ")
```

## Delete (Remove)

```python
# Simple delete
client.remove(key)

# Delete with generation check
client.remove(key, meta={"gen": 5}, policy={"gen": aerospike.POLICY_GEN_EQ})
```

### Remove Specific Bins

```python
client.remove_bin(key, ["temp_bin", "debug_bin"])
```

## Touch (Reset TTL)

```python
client.touch(key, val=600)  # reset TTL to 600 seconds
```

## Multi-Operation (Operate)

Execute multiple operations atomically on a single record:

```python
ops = [
    {"op": aerospike.OPERATOR_WRITE, "bin": "name", "val": "Bob"},
    {"op": aerospike.OPERATOR_INCR, "bin": "counter", "val": 1},
    {"op": aerospike.OPERATOR_READ, "bin": "counter", "val": None},
]
_, meta, bins = client.operate(key, ops)
print(bins["counter"])
```

### Ordered Results

```python
_, meta, results = client.operate_ordered(key, ops)
# results = [("name", "Bob"), ("counter", 2)]
```

## Optimistic Locking

Use generation-based conflict resolution:

```python
from aerospike_py.exception import RecordGenerationError

# Read current state
_, meta, bins = client.get(key)

try:
    # Update only if generation matches
    client.put(
        key,
        {"val": bins["val"] + 1},
        meta={"gen": meta["gen"]},
        policy={"gen": aerospike.POLICY_GEN_EQ},
    )
except RecordGenerationError:
    print("Record was modified concurrently, retry needed")
```

## Error Handling

```python
from aerospike_py.exception import (
    RecordNotFound,
    RecordExistsError,
    AerospikeError,
)

try:
    _, _, bins = client.get(key)
except RecordNotFound:
    print("Not found")
except AerospikeError as e:
    print(f"Error: {e}")
```
