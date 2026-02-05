"""End-to-end async scenario tests."""

import asyncio
import pytest

import aerospike
from aerospike import AsyncClient


def _run(coro):
    """Run async test, skip if server unavailable."""
    try:
        return asyncio.run(coro)
    except Exception as e:
        if "connect" in str(e).lower() or "cluster" in str(e).lower():
            pytest.skip("Aerospike server not available")
        raise


async def _make_client():
    c = AsyncClient({"hosts": [("127.0.0.1", 3000)], "cluster_name": "docker"})
    await c.connect()
    return c


class TestAsyncCRUDWorkflow:
    """Async multi-step CRUD scenarios."""

    def test_full_lifecycle(self):
        async def _test():
            c = await _make_client()
            key = ("test", "async_scen", "lifecycle")
            try:
                await c.put(key, {"name": "Alice", "age": 25})
                _, meta1, bins = await c.get(key)
                assert bins["name"] == "Alice"
                assert bins["age"] == 25
                gen1 = meta1["gen"]

                await c.put(key, {"age": 26})
                _, meta2, bins = await c.get(key)
                assert bins["name"] == "Alice"
                assert bins["age"] == 26
                assert meta2["gen"] == gen1 + 1

                await c.remove(key)
                _, meta = await c.exists(key)
                assert meta is None
            finally:
                try:
                    await c.remove(key)
                except Exception:
                    pass
                await c.close()

        _run(_test())

    def test_increment_sequence(self):
        async def _test():
            c = await _make_client()
            key = ("test", "async_scen", "incr_seq")
            try:
                await c.put(key, {"counter": 0})
                for _ in range(5):
                    await c.increment(key, "counter", 3)

                _, _, bins = await c.get(key)
                assert bins["counter"] == 15
            finally:
                try:
                    await c.remove(key)
                except Exception:
                    pass
                await c.close()

        _run(_test())

    def test_operate_atomic(self):
        async def _test():
            c = await _make_client()
            key = ("test", "async_scen", "operate_atomic")
            try:
                await c.put(key, {"a": 10, "b": "hello"})
                ops = [
                    {"op": aerospike.OPERATOR_INCR, "bin": "a", "val": 5},
                    {"op": aerospike.OPERATOR_READ, "bin": "a", "val": None},
                    {"op": aerospike.OPERATOR_READ, "bin": "b", "val": None},
                ]
                _, _, bins = await c.operate(key, ops)
                assert bins["a"] == 15
                assert bins["b"] == "hello"
            finally:
                try:
                    await c.remove(key)
                except Exception:
                    pass
                await c.close()

        _run(_test())


class TestAsyncBatchWorkflow:
    """Async batch operation scenarios."""

    def test_bulk_write_batch_read(self):
        async def _test():
            c = await _make_client()
            keys = [("test", "async_scen", f"batch_{i}") for i in range(5)]
            try:
                for i, key in enumerate(keys):
                    await c.put(key, {"idx": i})

                results = await c.get_many(keys)
                assert len(results) == 5
                for i, (_, meta, bins) in enumerate(results):
                    assert meta is not None
                    assert bins["idx"] == i
            finally:
                for key in keys:
                    try:
                        await c.remove(key)
                    except Exception:
                        pass
                await c.close()

        _run(_test())

    def test_batch_remove_verify(self):
        async def _test():
            c = await _make_client()
            keys = [("test", "async_scen", f"brem_{i}") for i in range(3)]
            try:
                for key in keys:
                    await c.put(key, {"val": 1})

                await c.batch_remove(keys)

                results = await c.exists_many(keys)
                for _, meta in results:
                    assert meta is None
            finally:
                await c.close()

        _run(_test())


class TestAsyncDataTypes:
    """Async data type edge case scenarios."""

    def test_various_types(self):
        async def _test():
            c = await _make_client()
            key = ("test", "async_scen", "types")
            try:
                data = {
                    "int": 42,
                    "float": 3.14,
                    "str": "hello 한글",
                    "bytes": b"\x00\x01\x02",
                    "list": [1, "two", 3.0],
                    "map": {"nested": {"deep": True}},
                    "bool": False,
                }
                await c.put(key, data)
                _, _, bins = await c.get(key)

                assert bins["int"] == 42
                assert abs(bins["float"] - 3.14) < 0.001
                assert bins["str"] == "hello 한글"
                assert bins["bytes"] == b"\x00\x01\x02"
                assert bins["list"] == [1, "two", 3.0]
                assert bins["map"]["nested"]["deep"] is True
                assert bins["bool"] is False
            finally:
                try:
                    await c.remove(key)
                except Exception:
                    pass
                await c.close()

        _run(_test())

    def test_large_record(self):
        async def _test():
            c = await _make_client()
            key = ("test", "async_scen", "large")
            try:
                large_str = "x" * 50_000
                large_list = list(range(1000))
                await c.put(key, {"str": large_str, "list": large_list})
                _, _, bins = await c.get(key)
                assert len(bins["str"]) == 50_000
                assert len(bins["list"]) == 1000
            finally:
                try:
                    await c.remove(key)
                except Exception:
                    pass
                await c.close()

        _run(_test())


class TestAsyncErrorHandling:
    """Async error handling scenarios."""

    def test_get_nonexistent(self):
        async def _test():
            c = await _make_client()
            try:
                with pytest.raises(aerospike.RecordNotFound):
                    await c.get(("test", "async_scen", "nonexistent_xyz"))
            finally:
                await c.close()

        _run(_test())

    def test_double_close(self):
        async def _test():
            c = await _make_client()
            await c.close()
            await c.close()  # Should not raise

        _run(_test())

    def test_operations_after_close(self):
        async def _test():
            c = await _make_client()
            await c.close()
            with pytest.raises(aerospike.AerospikeError):
                await c.get(("test", "demo", "key"))

        _run(_test())

    def test_connect_bad_host(self):
        async def _test():
            c = AsyncClient({"hosts": [("192.0.2.1", 9999)]})
            with pytest.raises(aerospike.AerospikeError):
                await c.connect()

        _run(_test())


class TestAsyncScanWorkflow:
    """Async scan scenario tests."""

    def test_scan_after_writes(self):
        async def _test():
            c = await _make_client()
            ns = "test"
            set_name = "async_scan_scen"
            keys = [(ns, set_name, f"s_{i}") for i in range(5)]
            try:
                for i, key in enumerate(keys):
                    await c.put(key, {"idx": i, "val": i * 10})

                results = await c.scan(ns, set_name)
                assert len(results) >= 5

                idxs = [bins["idx"] for _, _, bins in results]
                for i in range(5):
                    assert i in idxs
            finally:
                for key in keys:
                    try:
                        await c.remove(key)
                    except Exception:
                        pass
                await c.close()

        _run(_test())


class TestAsyncTruncate:
    """Async truncate scenario tests."""

    def test_truncate_set(self):
        async def _test():
            c = await _make_client()
            ns = "test"
            set_name = "async_trunc"
            keys = [(ns, set_name, f"t_{i}") for i in range(3)]
            try:
                for key in keys:
                    await c.put(key, {"v": 1})

                await c.truncate(ns, set_name)
                # Truncate is async on server side, so just verify no error
            finally:
                await c.close()

        _run(_test())


class TestAsyncUDF:
    """Async UDF scenario tests."""

    def test_apply_udf(self):
        async def _test():
            c = await _make_client()
            key = ("test", "async_scen", "udf_test")
            try:
                # Register UDF
                await c.udf_put("tests/test_udf.lua")

                await c.put(key, {"val": 42})

                # Apply UDF
                result = await c.apply(key, "test_udf", "echo", [100])
                assert result == 100

                result = await c.apply(key, "test_udf", "get_bin", ["val"])
                assert result == 42
            except aerospike.AerospikeError as e:
                if "udf" in str(e).lower():
                    pytest.skip("UDF not available")
                raise
            finally:
                try:
                    await c.remove(key)
                except Exception:
                    pass
                try:
                    await c.udf_remove("test_udf")
                except Exception:
                    pass
                await c.close()

        _run(_test())


class TestAsyncConcurrentOps:
    """Test concurrent async operations."""

    def test_concurrent_puts(self):
        async def _test():
            c = await _make_client()
            keys = [("test", "async_scen", f"conc_{i}") for i in range(10)]
            try:
                # Concurrent puts
                tasks = [c.put(key, {"idx": i}) for i, key in enumerate(keys)]
                await asyncio.gather(*tasks)

                # Verify all written
                results = await c.get_many(keys)
                assert len(results) == 10
                idxs = sorted([bins["idx"] for _, _, bins in results if bins])
                assert idxs == list(range(10))
            finally:
                for key in keys:
                    try:
                        await c.remove(key)
                    except Exception:
                        pass
                await c.close()

        _run(_test())

    def test_concurrent_reads_writes(self):
        async def _test():
            c = await _make_client()
            key = ("test", "async_scen", "conc_rw")
            try:
                await c.put(key, {"counter": 0})

                # Concurrent increments
                tasks = [c.increment(key, "counter", 1) for _ in range(10)]
                await asyncio.gather(*tasks)

                _, _, bins = await c.get(key)
                assert bins["counter"] == 10
            finally:
                try:
                    await c.remove(key)
                except Exception:
                    pass
                await c.close()

        _run(_test())
