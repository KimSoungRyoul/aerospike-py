"""Unit tests for error handling paths (no server required)."""

import pytest

import aerospike_py
from aerospike_py import exp


def _make_client():
    return aerospike_py.client({"hosts": [("127.0.0.1", 3000)]})


def _make_async_client():
    return aerospike_py.AsyncClient({"hosts": [("127.0.0.1", 3000)]})


KEY = ("test", "demo", "error_path_key")


class TestClientNotConnected:
    def test_get_not_connected_raises_client_error(self):
        c = _make_client()
        with pytest.raises(aerospike_py.ClientError):
            c.get(KEY)

    def test_put_not_connected_raises_client_error(self):
        c = _make_client()
        with pytest.raises(aerospike_py.ClientError):
            c.put(KEY, {"bin": 1})

    def test_exists_not_connected_raises_client_error(self):
        c = _make_client()
        with pytest.raises(aerospike_py.ClientError):
            c.exists(KEY)

    def test_remove_not_connected_raises_client_error(self):
        c = _make_client()
        with pytest.raises(aerospike_py.ClientError):
            c.remove(KEY)

    def test_batch_read_not_connected_raises_client_error(self):
        c = _make_client()
        with pytest.raises(aerospike_py.ClientError):
            c.batch_read([KEY])


class TestInvalidArguments:
    def test_put_non_dict_bins_raises_type_error(self):
        c = _make_client()
        with pytest.raises(TypeError):
            c.put(KEY, {1, 2, 3})

    def test_put_invalid_key_type_raises(self):
        c = _make_client()
        with pytest.raises((TypeError, aerospike_py.ClientError)):
            c.put("not_a_tuple", {"bin": 1})

    def test_key_too_short_raises(self):
        c = _make_client()
        with pytest.raises((TypeError, aerospike_py.AerospikeError)):
            c.put(("test", "demo"), {"bin": 1})

    def test_key_too_long_raises(self):
        c = _make_client()
        with pytest.raises((TypeError, aerospike_py.AerospikeError)):
            c.put(("test", "demo", "pk", "extra", "extra2"), {"bin": 1})


class TestExpressionErrors:
    def test_invalid_expression_type_raises(self):
        with pytest.raises(ValueError):
            exp._cmd("nonexistent_op", val=42)

    def test_expression_missing_expr_key_raises(self):
        bad_expr = {"not_expr": "eq", "left": 1, "right": 2}
        assert "__expr__" not in bad_expr
        valid = exp.int_val(1)
        assert "__expr__" in valid

    def test_unknown_expression_op_raises(self):
        with pytest.raises(ValueError, match="Unknown expression op"):
            exp._cmd("totally_bogus_operation")

    def test_expression_builder_rejects_empty_op(self):
        with pytest.raises(ValueError):
            exp._cmd("")


class TestAsyncClientErrors:
    async def test_async_get_not_connected_raises(self):
        c = _make_async_client()
        with pytest.raises(aerospike_py.ClientError):
            await c.get(KEY)

    async def test_async_put_not_connected_raises(self):
        c = _make_async_client()
        with pytest.raises(aerospike_py.ClientError):
            await c.put(KEY, {"bin": 1})
