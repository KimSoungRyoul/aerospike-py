"""Memory profiling utilities for aerospike-py."""

from __future__ import annotations

from typing import Any


def get_memory_stats() -> dict[str, int]:
    from aerospike_py._aerospike import _get_memory_stats

    return _get_memory_stats()


def reset_memory_stats() -> None:
    from aerospike_py._aerospike import _reset_memory_stats

    _reset_memory_stats()


class MemoryProfiler:
    def __init__(self):
        self._start: dict[str, int] = {}
        self._end: dict[str, int] = {}

    def __enter__(self) -> MemoryProfiler:
        self._start = get_memory_stats()
        return self

    def __exit__(self, *args: Any) -> None:
        self._end = get_memory_stats()

    @property
    def allocated_bytes(self) -> int:
        return self._end.get("total_allocated_bytes", 0) - self._start.get("total_allocated_bytes", 0)

    @property
    def deallocated_bytes(self) -> int:
        return self._end.get("total_deallocated_bytes", 0) - self._start.get("total_deallocated_bytes", 0)

    @property
    def delta_bytes(self) -> int:
        return self.allocated_bytes - self.deallocated_bytes

    @property
    def allocation_count(self) -> int:
        return self._end.get("allocation_count", 0) - self._start.get("allocation_count", 0)
