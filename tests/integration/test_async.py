"""Integration tests for AsyncClient (requires Aerospike server).

pyo3_async_runtimes requires a running event loop when async methods are called,
so all AsyncClient method calls must happen inside an async context.
We use asyncio.run() for each test to ensure this.
"""

import asyncio

import pytest

import aerospike

CONFIG = {"hosts": [("127.0.0.1", 3000)], "cluster_name": "docker"}


def _run(coro):
    """Run an async test, skipping if server is unavailable."""
    try:
        return asyncio.run(coro)
    except Exception as e:
        if "connect" in str(e).lower() or "cluster" in str(e).lower():
            pytest.skip(f"Aerospike server not available: {e}")
        raise


class TestAsyncConnection:
    def test_is_connected(self):
        async def _test():
            c = aerospike.AsyncClient(CONFIG)
            await c.connect()
            assert c.is_connected()
            await c.close()

        _run(_test())

    def test_close(self):
        async def _test():
            c = aerospike.AsyncClient(CONFIG)
            await c.connect()
            assert c.is_connected()
            await c.close()
            assert not c.is_connected()

        _run(_test())


class TestAsyncCRUD:
    def test_put_and_get(self):
        async def _test():
            c = aerospike.AsyncClient(CONFIG)
            await c.connect()
            key = ("test", "demo", "async_key1")
            await c.put(key, {"name": "async", "val": 42})
            record = await c.get(key)
            _, meta, bins = record
            assert bins["name"] == "async"
            assert bins["val"] == 42
            assert meta["gen"] >= 1
            await c.remove(key)
            await c.close()

        _run(_test())

    def test_exists(self):
        async def _test():
            c = aerospike.AsyncClient(CONFIG)
            await c.connect()
            key = ("test", "demo", "async_exists")
            await c.put(key, {"a": 1})
            result = await c.exists(key)
            k, meta = result
            assert meta is not None

            await c.remove(key)
            result = await c.exists(key)
            k, meta = result
            assert meta is None
            await c.close()

        _run(_test())

    def test_touch_and_increment(self):
        async def _test():
            c = aerospike.AsyncClient(CONFIG)
            await c.connect()
            key = ("test", "demo", "async_touch")
            await c.put(key, {"counter": 10})
            await c.touch(key)
            await c.increment(key, "counter", 5)
            record = await c.get(key)
            _, _, bins = record
            assert bins["counter"] == 15
            await c.remove(key)
            await c.close()

        _run(_test())

    def test_operate(self):
        async def _test():
            c = aerospike.AsyncClient(CONFIG)
            await c.connect()
            key = ("test", "demo", "async_operate")
            await c.put(key, {"a": 1, "b": "hello"})
            ops = [
                {"op": aerospike.OPERATOR_INCR, "bin": "a", "val": 10},
                {"op": aerospike.OPERATOR_READ, "bin": "a", "val": None},
            ]
            record = await c.operate(key, ops)
            _, _, bins = record
            val = bins["a"]
            if isinstance(val, list):
                assert val[-1] == 11
            else:
                assert val == 11
            await c.remove(key)
            await c.close()

        _run(_test())


class TestAsyncBatch:
    def test_get_many(self):
        async def _test():
            c = aerospike.AsyncClient(CONFIG)
            await c.connect()
            keys = [
                ("test", "demo", "async_batch_1"),
                ("test", "demo", "async_batch_2"),
            ]
            await c.put(keys[0], {"v": 1})
            await c.put(keys[1], {"v": 2})
            results = await c.get_many(keys)
            assert len(results) == 2
            for _, meta, bins in results:
                assert meta is not None
                assert "v" in bins
            await c.batch_remove(keys)
            await c.close()

        _run(_test())

    def test_exists_many(self):
        async def _test():
            c = aerospike.AsyncClient(CONFIG)
            await c.connect()
            keys = [
                ("test", "demo", "async_em_1"),
                ("test", "demo", "async_em_missing"),
            ]
            await c.put(keys[0], {"v": 1})
            results = await c.exists_many(keys)
            assert len(results) == 2
            _, meta0 = results[0]
            _, meta1 = results[1]
            assert meta0 is not None
            assert meta1 is None
            await c.remove(keys[0])
            await c.close()

        _run(_test())


class TestAsyncScan:
    def test_scan(self):
        async def _test():
            c = aerospike.AsyncClient(CONFIG)
            await c.connect()
            key = ("test", "demo", "async_scan_1")
            await c.put(key, {"s": "data"})
            results = await c.scan("test", "demo")
            assert len(results) >= 1
            await c.remove(key)
            await c.close()

        _run(_test())
