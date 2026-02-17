"""Unit tests for concurrent operation safety (no Aerospike server required)."""

import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

import aerospike_py
from aerospike_py import exp


def _find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


# ---------------------------------------------------------------------------
# Metrics concurrency
# ---------------------------------------------------------------------------


class TestMetricsConcurrency:
    def test_concurrent_get_metrics(self):
        errors: list = []

        def worker(idx):
            try:
                text = aerospike_py.get_metrics()
                assert isinstance(text, str)
                assert "# HELP" in text
            except Exception as e:
                errors.append((idx, e))

        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = [pool.submit(worker, i) for i in range(4)]
            for f in as_completed(futures):
                f.result()  # re-raise if worker raised

        assert not errors, f"Concurrent get_metrics() errors: {errors}"

    def test_concurrent_start_stop_metrics_server(self):
        errors: list = []

        def worker(idx):
            try:
                port = _find_free_port()
                if idx % 2 == 0:
                    try:
                        aerospike_py.start_metrics_server(port=port)
                    except OSError:
                        pass
                else:
                    aerospike_py.stop_metrics_server()
            except Exception as e:
                errors.append((idx, e))

        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = [pool.submit(worker, i) for i in range(4)]
            for f in as_completed(futures):
                f.result()

        aerospike_py.stop_metrics_server()
        assert not errors, f"Concurrent start/stop errors: {errors}"

    def test_metrics_server_restart_under_load(self):
        port1 = _find_free_port()
        aerospike_py.start_metrics_server(port=port1)
        try:
            text1 = aerospike_py.get_metrics()
            assert isinstance(text1, str)
            assert "# HELP" in text1
        finally:
            aerospike_py.stop_metrics_server()

        port2 = _find_free_port()
        aerospike_py.start_metrics_server(port=port2)
        try:
            errors: list = []

            def reader(idx):
                try:
                    text = aerospike_py.get_metrics()
                    assert isinstance(text, str)
                except Exception as e:
                    errors.append((idx, e))

            with ThreadPoolExecutor(max_workers=4) as pool:
                futures = [pool.submit(reader, i) for i in range(4)]
                for f in as_completed(futures):
                    f.result()

            assert not errors, f"Post-restart concurrent read errors: {errors}"
        finally:
            aerospike_py.stop_metrics_server()


# ---------------------------------------------------------------------------
# Client creation concurrency
# ---------------------------------------------------------------------------


class TestClientCreationConcurrency:
    def test_concurrent_client_creation(self):
        clients: dict = {}
        errors: list = []

        def worker(idx):
            try:
                c = aerospike_py.client({"hosts": [("127.0.0.1", 3000)]})
                assert isinstance(c, aerospike_py.Client)
                assert not c.is_connected()
                clients[idx] = c
            except Exception as e:
                errors.append((idx, e))

        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = [pool.submit(worker, i) for i in range(4)]
            for f in as_completed(futures):
                f.result()

        assert not errors, f"Concurrent client creation errors: {errors}"
        assert len(clients) == 4

    def test_concurrent_async_client_creation(self):
        clients: dict = {}
        errors: list = []

        def worker(idx):
            try:
                c = aerospike_py.AsyncClient({"hosts": [("127.0.0.1", 3000)]})
                clients[idx] = c
            except Exception as e:
                errors.append((idx, e))

        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = [pool.submit(worker, i) for i in range(4)]
            for f in as_completed(futures):
                f.result()

        assert not errors, f"Concurrent async client creation errors: {errors}"
        assert len(clients) == 4


# ---------------------------------------------------------------------------
# Tracing concurrency
# ---------------------------------------------------------------------------


class TestTracingConcurrency:
    def test_concurrent_init_shutdown_tracing(self, monkeypatch):
        monkeypatch.setenv("OTEL_SDK_DISABLED", "true")
        errors: list = []

        def worker(idx):
            try:
                if idx % 2 == 0:
                    aerospike_py.init_tracing()
                else:
                    aerospike_py.shutdown_tracing()
            except Exception as e:
                errors.append((idx, e))

        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = [pool.submit(worker, i) for i in range(4)]
            for f in as_completed(futures):
                f.result()

        aerospike_py.shutdown_tracing()
        assert not errors, f"Concurrent tracing init/shutdown errors: {errors}"

    def test_tracing_with_client_operations(self, monkeypatch):
        monkeypatch.setenv("OTEL_SDK_DISABLED", "true")
        aerospike_py.init_tracing()
        try:
            errors: list = []

            def worker(idx):
                try:
                    c = aerospike_py.client({"hosts": [("127.0.0.1", 3000)]})
                    key = ("test", "demo", f"concurrency_key_{idx}")
                    try:
                        c.put(key, {"val": idx})
                    except aerospike_py.ClientError:
                        pass
                    try:
                        c.get(key)
                    except aerospike_py.ClientError:
                        pass
                except Exception as e:
                    errors.append((idx, e))

            with ThreadPoolExecutor(max_workers=4) as pool:
                futures = [pool.submit(worker, i) for i in range(4)]
                for f in as_completed(futures):
                    f.result()

            assert not errors, f"Tracing + client ops errors: {errors}"
        finally:
            aerospike_py.shutdown_tracing()


# ---------------------------------------------------------------------------
# Expression concurrency
# ---------------------------------------------------------------------------


class TestExpressionConcurrency:
    def test_concurrent_expression_building(self):
        results: dict = {}
        errors: list = []

        def worker(idx):
            try:
                if idx == 0:
                    e = exp.and_(
                        exp.ge(exp.int_bin("age"), exp.int_val(18)),
                        exp.lt(exp.int_bin("age"), exp.int_val(65)),
                    )
                    assert e["__expr__"] == "and"
                elif idx == 1:
                    e = exp.or_(
                        exp.eq(exp.string_bin("status"), exp.string_val("active")),
                        exp.eq(exp.string_bin("status"), exp.string_val("pending")),
                    )
                    assert e["__expr__"] == "or"
                elif idx == 2:
                    e = exp.not_(
                        exp.eq(exp.int_bin("deleted"), exp.int_val(1)),
                    )
                    assert e["__expr__"] == "not"
                else:
                    e = exp.let_(
                        exp.def_("x", exp.int_bin("count")),
                        exp.gt(exp.var("x"), exp.int_val(0)),
                    )
                    assert e["__expr__"] == "let"

                results[idx] = e
            except Exception as e:
                errors.append((idx, e))

        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = [pool.submit(worker, i) for i in range(4)]
            for f in as_completed(futures):
                f.result()

        assert not errors, f"Concurrent expression building errors: {errors}"
        assert len(results) == 4
        for r in results.values():
            assert "__expr__" in r
