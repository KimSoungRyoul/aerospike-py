"""Telemetry configuration for aerospike-py."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any, Optional

logger = logging.getLogger("aerospike_py")

_LOG_LEVEL_MAP = {"off": -1, "error": 0, "warn": 1, "info": 2, "debug": 3, "trace": 4}
_PY_LOG_LEVEL_MAP = {-1: 60, 0: logging.ERROR, 1: logging.WARNING, 2: logging.INFO, 3: logging.DEBUG, 4: logging.DEBUG}


@dataclass
class TelemetryConfig:
    enabled: Optional[bool] = None
    log_level: str = "warn"
    tracing_enabled: bool = True
    metrics_enabled: bool = True
    tracer_provider: Any = None
    meter_provider: Any = None
    request_hook: Any = None
    response_hook: Any = None
    error_hook: Any = None

    def __post_init__(self):
        if self.enabled is None:
            self.enabled = os.getenv("AEROSPIKE_PY_TELEMETRY_ENABLED", "false").lower() in ("true", "1", "yes")
        env_log = os.getenv("AEROSPIKE_PY_LOG_LEVEL")
        if env_log:
            self.log_level = env_log.lower()
        env_metrics = os.getenv("AEROSPIKE_PY_METRICS_ENABLED")
        if env_metrics is not None:
            self.metrics_enabled = env_metrics.lower() in ("true", "1", "yes")
        env_tracing = os.getenv("AEROSPIKE_PY_TRACING_ENABLED")
        if env_tracing is not None:
            self.tracing_enabled = env_tracing.lower() in ("true", "1", "yes")


_instrumentor = None


def configure_telemetry(config: TelemetryConfig | None = None) -> None:
    global _instrumentor
    if config is None:
        config = TelemetryConfig()
    if not config.enabled:
        return

    rust_level = _LOG_LEVEL_MAP.get(config.log_level.lower(), 1)
    try:
        from aerospike_py._aerospike import _init_telemetry

        _init_telemetry(rust_level)
    except (ImportError, AttributeError):
        pass

    py_level = _PY_LOG_LEVEL_MAP.get(rust_level, logging.WARNING)
    logger.setLevel(py_level)

    if config.tracing_enabled:
        try:
            from aerospike_py.otel import AerospikeInstrumentor

            _instrumentor = AerospikeInstrumentor(
                tracer_provider=config.tracer_provider,
                request_hook=config.request_hook,
                response_hook=config.response_hook,
                error_hook=config.error_hook,
            )
            _instrumentor.instrument()
        except ImportError:
            pass

    if config.metrics_enabled:
        try:
            from aerospike_py.otel import setup_otel_metrics

            setup_otel_metrics(meter_provider=config.meter_provider)
        except ImportError:
            pass


def shutdown_telemetry() -> None:
    global _instrumentor
    if _instrumentor is not None:
        _instrumentor.uninstrument()
        _instrumentor = None
