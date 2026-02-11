"""Structured logging for aerospike-py.

Bridges Rust-side tracing logs to Python's standard logging module.

Usage:
    import logging
    from aerospike_py.logging import set_log_level

    logging.basicConfig(level=logging.DEBUG)
    set_log_level(3)  # LOG_LEVEL_DEBUG
"""

from __future__ import annotations

import logging

logger = logging.getLogger("aerospike_py")

_LEVEL_TO_PY = {
    0: logging.ERROR,
    1: logging.WARNING,
    2: logging.INFO,
    3: logging.DEBUG,
    4: logging.DEBUG,
}


def set_log_level(level: int) -> None:
    """Set logging level for aerospike-py.

    Args:
        level: One of LOG_LEVEL_OFF(-1), LOG_LEVEL_ERROR(0), LOG_LEVEL_WARN(1),
               LOG_LEVEL_INFO(2), LOG_LEVEL_DEBUG(3), LOG_LEVEL_TRACE(4)
    """
    try:
        from aerospike_py._aerospike import _init_telemetry

        _init_telemetry(level)
    except (ImportError, AttributeError):
        pass

    py_level = _LEVEL_TO_PY.get(level, logging.WARNING)
    logger.setLevel(py_level)


def flush_logs() -> None:
    """Drain buffered log messages from Rust side to Python logging."""
    try:
        from aerospike_py._aerospike import _flush_logs

        for record in _flush_logs():
            py_level = _LEVEL_TO_PY.get(record["level"], logging.DEBUG)
            logger.log(py_level, "[%s] %s", record["target"], record["message"])
    except (ImportError, AttributeError):
        pass
