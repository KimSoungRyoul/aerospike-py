"""OpenTelemetry integration for aerospike-py. Requires: pip install aerospike-py[otel]"""

from __future__ import annotations

import contextlib
from typing import Any, Callable, Optional

RequestHook = Callable[..., None]
ResponseHook = Callable[..., None]
ErrorHook = Callable[..., None]


class AerospikeInstrumentor:
    def __init__(
        self,
        tracer_provider: Optional[Any] = None,
        request_hook: Optional[RequestHook] = None,
        response_hook: Optional[ResponseHook] = None,
        error_hook: Optional[ErrorHook] = None,
    ):
        self._tracer_provider = tracer_provider
        self._request_hook = request_hook
        self._response_hook = response_hook
        self._error_hook = error_hook

    def instrument(self) -> None:
        try:
            from aerospike_py._aerospike import _set_span_callback

            _set_span_callback(self._on_span)
        except (ImportError, AttributeError):
            pass

    def uninstrument(self) -> None:
        try:
            from aerospike_py._aerospike import _set_span_callback

            _set_span_callback(None)
        except (ImportError, AttributeError):
            pass

    def _on_span(self, span_data: dict) -> None:  # type: ignore[type-arg]
        try:
            from opentelemetry import trace  # type: ignore[import-not-found]
            from opentelemetry.trace import StatusCode  # type: ignore[import-not-found]
        except ImportError:
            return
        tracer = trace.get_tracer("aerospike_py", tracer_provider=self._tracer_provider)
        attributes = span_data.get("attributes", {})
        op_name = span_data.get("operation", "UNKNOWN")
        flat_attrs: dict[str, Any] = {}
        for k, v in attributes.items():
            flat_attrs[k] = ", ".join(str(x) for x in v) if isinstance(v, list) else v
        with tracer.start_as_current_span(f"aerospike.{op_name.lower()}", attributes=flat_attrs) as span:
            if self._request_hook:
                with contextlib.suppress(Exception):
                    self._request_hook(span, op_name, flat_attrs)
            error = span_data.get("error")
            if error:
                span.set_status(StatusCode.ERROR, error)
                span.set_attribute("exception.message", error)
                if self._error_hook:
                    with contextlib.suppress(Exception):
                        self._error_hook(span, op_name, error)
            elif self._response_hook:
                with contextlib.suppress(Exception):
                    self._response_hook(span, op_name, span_data)


def setup_otel_metrics(meter_provider: Optional[Any] = None) -> None:
    try:
        from opentelemetry import metrics  # type: ignore[import-not-found]
    except ImportError:
        return
    meter = metrics.get_meter("aerospike_py", meter_provider=meter_provider)
    meter.create_histogram(
        name="aerospike.client.operation.duration",
        unit="us",
        description="Duration of Aerospike operations in microseconds",
    )
    meter.create_counter(name="aerospike.client.operation.count", description="Total number of Aerospike operations")
    meter.create_counter(
        name="aerospike.client.operation.errors", description="Total number of failed Aerospike operations"
    )
