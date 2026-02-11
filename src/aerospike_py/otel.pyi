from typing import Any, Callable, Optional

class AerospikeInstrumentor:
    def __init__(
        self,
        tracer_provider: Any = ...,
        request_hook: Optional[Callable[..., None]] = ...,
        response_hook: Optional[Callable[..., None]] = ...,
        error_hook: Optional[Callable[..., None]] = ...,
    ) -> None: ...
    def instrument(self) -> None: ...
    def uninstrument(self) -> None: ...

def setup_otel_metrics(meter_provider: Any = ...) -> None: ...
