"""Regression tests for previously-crashing (panic) scenarios.

Task 5 (key validation), Task 12 (metrics), Task 13 (deprecation), Task 14 (async connect).
"""

import asyncio
import inspect
import socket
import warnings

import pytest

import aerospike_py


def _make_client():
    return aerospike_py.client({"hosts": [("127.0.0.1", 3000)]})


def _find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


class TestKeyValidation:
    @pytest.mark.parametrize(
        "key",
        [
            ("ns", "set", "pk", "extra", "extra2"),
            ("ns", "set", "pk", 1, 2, 3),
            tuple(range(7)),
            ("a",) * 10,
        ],
        ids=["5-elem", "6-elem", "7-elem", "10-elem"],
    )
    def test_key_tuple_too_many_elements_raises(self, key):
        """Key with >4 elements must not silently succeed — error before or after connect check."""
        c = _make_client()
        with pytest.raises((ValueError, TypeError, aerospike_py.ClientError)):
            c.put(key, {"bin": 1})

    def test_key_tuple_5_elements_raises(self):
        c = _make_client()
        with pytest.raises((ValueError, TypeError, aerospike_py.ClientError)):
            c.put(("ns", "set", "pk", "x", "y"), {"b": 1})

    def test_key_tuple_6_elements_raises(self):
        c = _make_client()
        with pytest.raises((ValueError, TypeError, aerospike_py.ClientError)):
            c.put(("ns", "set", "pk", "x", "y", "z"), {"b": 1})

    def test_key_tuple_3_elements_valid(self):
        """3-element key is valid; on unconnected client we get ClientError (not a crash)."""
        c = _make_client()
        with pytest.raises(aerospike_py.ClientError):
            c.put(("test", "demo", "key1"), {"bin": 1})

    def test_key_tuple_too_short_raises(self):
        c = _make_client()
        with pytest.raises((ValueError, TypeError, aerospike_py.ClientError)):
            c.put(("ns",), {"bin": 1})


class TestMetricsThreadSafety:
    def test_double_start_metrics_server_no_crash(self):
        port1 = _find_free_port()
        port2 = _find_free_port()
        try:
            aerospike_py.start_metrics_server(port=port1)
            aerospike_py.start_metrics_server(port=port2)
        finally:
            aerospike_py.stop_metrics_server()

    def test_stop_without_start_no_crash(self):
        aerospike_py.stop_metrics_server()
        aerospike_py.stop_metrics_server()


class TestDeprecationWarnings:
    def test_timeout_error_emits_deprecation(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            _ = aerospike_py.TimeoutError
            deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
            assert len(deprecation_warnings) >= 1
            assert "TimeoutError" in str(deprecation_warnings[0].message)

    def test_index_error_emits_deprecation(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            _ = aerospike_py.IndexError
            deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
            assert len(deprecation_warnings) >= 1
            assert "IndexError" in str(deprecation_warnings[0].message)

    def test_deprecated_timeout_alias_is_correct_class(self):
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            te = aerospike_py.TimeoutError
        assert te is aerospike_py.AerospikeTimeoutError

    def test_deprecated_index_alias_is_correct_class(self):
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            ie = aerospike_py.IndexError
        assert ie is aerospike_py.AerospikeIndexError

    def test_deprecated_aliases_still_work(self):
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            te = aerospike_py.TimeoutError
            ie = aerospike_py.IndexError
        assert issubclass(te, aerospike_py.AerospikeError)
        assert issubclass(ie, aerospike_py.ServerError)


class TestAsyncClientConnectReturnType:
    def test_async_connect_returns_self(self):
        hints = inspect.get_annotations(aerospike_py.AsyncClient.connect)
        return_hint = hints.get("return")
        assert return_hint is not None
        if isinstance(return_hint, str):
            assert "AsyncClient" in return_hint
        else:
            assert return_hint is aerospike_py.AsyncClient or (
                hasattr(return_hint, "__name__") and "AsyncClient" in return_hint.__name__
            )

    def test_async_connect_method_exists_on_wrapper(self):
        assert "connect" in aerospike_py.AsyncClient.__dict__

    def test_async_client_connect_is_coroutine(self):
        assert asyncio.iscoroutinefunction(aerospike_py.AsyncClient.connect)


class TestImportSmokeTests:
    def test_import_no_crash(self):
        import aerospike_py as ap  # noqa: F811

        assert ap is not None
        assert hasattr(ap, "Client")
        assert hasattr(ap, "AsyncClient")

    def test_basic_client_creation(self):
        c = aerospike_py.client({"hosts": [("127.0.0.1", 3000)]})
        assert isinstance(c, aerospike_py.Client)
        assert not c.is_connected()
