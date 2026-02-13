"""Record, scan, batch, and operation models."""

from typing import Any

from pydantic import BaseModel, Field

# ── Shared key model ──────────────────────────────────────────


class KeySpec(BaseModel):
    namespace: str
    set: str
    key: str | int


# ── Responses ─────────────────────────────────────────────────


class RecordResponse(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    key: Any = None  # (ns, set, pk, digest) 4-tuple from aerospike
    meta: dict[str, Any] | None = None
    bins: dict[str, Any] | None = None


class ScanResult(BaseModel):
    records: list[RecordResponse] = []
    total_scanned: int = 0
    page: int = 1
    page_size: int = 50
    has_more: bool = False


class ExistsResponse(BaseModel):
    exists: bool
    key: Any = None
    meta: dict[str, Any] | None = None


# ── Record CRUD requests ─────────────────────────────────────


class PutRequest(BaseModel):
    namespace: str
    set: str
    key: str | int
    bins: dict[str, Any]
    ttl: int | None = None


class GetRequest(BaseModel):
    namespace: str
    set: str
    key: str | int


class SelectRequest(BaseModel):
    namespace: str
    set: str
    key: str | int
    bins: list[str]


class ExistsRequest(BaseModel):
    namespace: str
    set: str
    key: str | int


class RemoveRequest(BaseModel):
    namespace: str
    set: str
    key: str | int


class ScanRequest(BaseModel):
    namespace: str
    set: str
    page: int = Field(1, gt=0)
    page_size: int = Field(50, gt=0, le=10000)


# ── Operations requests ──────────────────────────────────────


class TouchRequest(BaseModel):
    namespace: str
    set: str
    key: str | int
    val: int = 0


class AppendRequest(BaseModel):
    namespace: str
    set: str
    key: str | int
    bin: str
    val: Any


class PrependRequest(BaseModel):
    namespace: str
    set: str
    key: str | int
    bin: str
    val: Any


class IncrementRequest(BaseModel):
    namespace: str
    set: str
    key: str | int
    bin: str
    offset: int | float


class RemoveBinRequest(BaseModel):
    namespace: str
    set: str
    key: str | int
    bin_names: list[str]


class OperateRequest(BaseModel):
    namespace: str
    set: str
    key: str | int
    ops: list[dict[str, Any]]


# ── Batch requests ────────────────────────────────────────────


class BatchReadRequest(BaseModel):
    keys: list[KeySpec]
    bins: list[str] | None = None


class BatchOperateRequest(BaseModel):
    keys: list[KeySpec]
    ops: list[dict[str, Any]]


class BatchRemoveRequest(BaseModel):
    keys: list[KeySpec]


# ── Truncate request ──────────────────────────────────────────


class TruncateRequest(BaseModel):
    namespace: str
    set: str
    nanos: int = 0


# ── Legacy aliases for backward compatibility during transition ──

BrowseResult = ScanResult
RecordCreateRequest = PutRequest
RecordUpdateRequest = PutRequest
