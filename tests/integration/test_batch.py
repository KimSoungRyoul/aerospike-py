"""Integration tests for batch operations (requires Aerospike server)."""

import pytest

import aerospike


@pytest.fixture(scope="module")
def client():
    """Create and connect a client for the test module."""
    try:
        c = aerospike.client({"hosts": [("127.0.0.1", 3000)], "cluster_name": "docker"}).connect()
    except Exception:
        pytest.skip("Aerospike server not available")
    yield c
    c.close()


@pytest.fixture(autouse=True)
def cleanup(client):
    """Clean up test keys after each test."""
    keys = []
    yield keys
    for key in keys:
        try:
            client.remove(key)
        except Exception:
            pass


class TestGetMany:
    def test_get_many(self, client, cleanup):
        keys = [
            ("test", "demo", "batch_get_1"),
            ("test", "demo", "batch_get_2"),
            ("test", "demo", "batch_get_3"),
        ]
        for k in keys:
            cleanup.append(k)

        client.put(keys[0], {"a": 1})
        client.put(keys[1], {"a": 2})
        client.put(keys[2], {"a": 3})

        results = client.get_many(keys)
        assert len(results) == 3
        for key_tuple, meta, bins in results:
            assert meta is not None
            assert meta["gen"] >= 1
            assert "a" in bins

    def test_get_many_with_missing(self, client, cleanup):
        keys = [
            ("test", "demo", "batch_get_exists"),
            ("test", "demo", "batch_get_missing"),
        ]
        cleanup.append(keys[0])

        client.put(keys[0], {"val": 1})

        results = client.get_many(keys)
        assert len(results) == 2
        # First key exists
        _, meta0, bins0 = results[0]
        assert meta0 is not None
        assert bins0["val"] == 1
        # Second key missing
        _, meta1, bins1 = results[1]
        assert meta1 is None
        assert bins1 is None


class TestExistsMany:
    def test_exists_many(self, client, cleanup):
        keys = [
            ("test", "demo", "batch_exists_1"),
            ("test", "demo", "batch_exists_2"),
            ("test", "demo", "batch_exists_missing"),
        ]
        cleanup.append(keys[0])
        cleanup.append(keys[1])

        client.put(keys[0], {"val": 1})
        client.put(keys[1], {"val": 2})

        results = client.exists_many(keys)
        assert len(results) == 3
        _, meta0 = results[0]
        assert meta0 is not None
        _, meta1 = results[1]
        assert meta1 is not None
        _, meta2 = results[2]
        assert meta2 is None


class TestSelectMany:
    def test_select_many(self, client, cleanup):
        keys = [
            ("test", "demo", "batch_select_1"),
            ("test", "demo", "batch_select_2"),
        ]
        for k in keys:
            cleanup.append(k)

        client.put(keys[0], {"a": 1, "b": 2, "c": 3})
        client.put(keys[1], {"a": 10, "b": 20, "c": 30})

        results = client.select_many(keys, ["a", "c"])
        assert len(results) == 2
        for _, meta, bins in results:
            assert meta is not None
            assert "a" in bins
            assert "c" in bins


class TestBatchOperate:
    def test_batch_operate(self, client, cleanup):
        keys = [
            ("test", "demo", "batch_op_1"),
            ("test", "demo", "batch_op_2"),
        ]
        for k in keys:
            cleanup.append(k)

        client.put(keys[0], {"counter": 10})
        client.put(keys[1], {"counter": 20})

        ops = [
            {"op": aerospike.OPERATOR_INCR, "bin": "counter", "val": 5},
            {"op": aerospike.OPERATOR_READ, "bin": "counter", "val": None},
        ]
        results = client.batch_operate(keys, ops)
        assert len(results) == 2
        _, _, bins0 = results[0]
        _, _, bins1 = results[1]
        # Batch operate returns multi-op results as list per bin
        counter0 = bins0["counter"]
        counter1 = bins1["counter"]
        if isinstance(counter0, list):
            assert counter0[-1] == 15
            assert counter1[-1] == 25
        else:
            assert counter0 == 15
            assert counter1 == 25


class TestBatchRemove:
    def test_batch_remove(self, client):
        keys = [
            ("test", "demo", "batch_rm_1"),
            ("test", "demo", "batch_rm_2"),
        ]

        client.put(keys[0], {"val": 1})
        client.put(keys[1], {"val": 2})

        client.batch_remove(keys)

        for k in keys:
            _, meta = client.exists(k)
            assert meta is None
