"""Tests for telemetry configuration."""


class TestTelemetryConfig:
    def test_default_disabled(self):
        from aerospike_py.telemetry import TelemetryConfig

        config = TelemetryConfig()
        assert config.enabled is False

    def test_env_enabled(self, monkeypatch):
        monkeypatch.setenv("AEROSPIKE_PY_TELEMETRY_ENABLED", "true")
        from aerospike_py.telemetry import TelemetryConfig

        config = TelemetryConfig()
        assert config.enabled is True

    def test_configure_disabled_noop(self):
        from aerospike_py.telemetry import TelemetryConfig, configure_telemetry

        configure_telemetry(TelemetryConfig(enabled=False))

    def test_shutdown_noop(self):
        from aerospike_py.telemetry import shutdown_telemetry

        shutdown_telemetry()
