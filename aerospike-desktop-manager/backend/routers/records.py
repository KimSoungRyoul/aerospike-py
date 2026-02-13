"""Record CRUD and scan router — thin wrapper over AsyncClient."""

import aerospike_py
from fastapi import APIRouter, Depends

from dependencies import get_client
from models.record import (
    ExistsRequest,
    ExistsResponse,
    GetRequest,
    PutRequest,
    RecordResponse,
    RemoveRequest,
    ScanRequest,
    ScanResult,
    SelectRequest,
)
from utils.key_helpers import parse_pk
from utils.serialization import format_bins, serialize_key

router = APIRouter()

# Desktop Manager always stores the original PK so it can be displayed on read/scan.
SEND_KEY_POLICY = {"key": aerospike_py.POLICY_KEY_SEND}


@router.post("/put")
async def put_record(
    req: PutRequest,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    key = (req.namespace, req.set, req.key)
    meta = {"ttl": req.ttl} if req.ttl else None
    await client.put(key, req.bins, meta, SEND_KEY_POLICY)
    return {"ok": True}


@router.post("/get", response_model=RecordResponse)
async def get_record_by_body(
    req: GetRequest,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    key = (req.namespace, req.set, req.key)
    rec_key, meta, bins = await client.get(key)
    return RecordResponse(key=serialize_key(rec_key), meta=meta, bins=format_bins(bins))


@router.post("/select", response_model=RecordResponse)
async def select_record(
    req: SelectRequest,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    key = (req.namespace, req.set, req.key)
    rec_key, meta, bins = await client.select(key, req.bins)
    return RecordResponse(key=serialize_key(rec_key), meta=meta, bins=format_bins(bins))


@router.post("/exists", response_model=ExistsResponse)
async def exists_record(
    req: ExistsRequest,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    key = (req.namespace, req.set, req.key)
    rec_key, meta = await client.exists(key)
    return ExistsResponse(exists=meta is not None, key=serialize_key(rec_key), meta=meta)


@router.post("/remove")
async def remove_record(
    req: RemoveRequest,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    key = (req.namespace, req.set, req.key)
    await client.remove(key)
    return {"ok": True}


@router.post("/scan", response_model=ScanResult)
async def scan_records(
    req: ScanRequest,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    records = await client.scan(req.namespace, req.set)

    total = len(records)
    start = (req.page - 1) * req.page_size
    end = start + req.page_size
    page_records = records[start:end]

    result_records = []
    for rec in page_records:
        key, meta, bins = rec
        result_records.append(RecordResponse(key=serialize_key(key), meta=meta, bins=format_bins(bins)))

    return ScanResult(
        records=result_records,
        total_scanned=total,
        page=req.page,
        page_size=req.page_size,
        has_more=end < total,
    )


# ── RESTful convenience aliases ───────────────────────────────


@router.get("/{ns}/{set_name}/{pk}", response_model=RecordResponse)
async def get_record_rest(
    ns: str,
    set_name: str,
    pk: str,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    key = (ns, set_name, parse_pk(pk))
    rec_key, meta, bins = await client.get(key)
    return RecordResponse(key=serialize_key(rec_key), meta=meta, bins=format_bins(bins))


@router.delete("/{ns}/{set_name}/{pk}")
async def delete_record_rest(
    ns: str,
    set_name: str,
    pk: str,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    key = (ns, set_name, parse_pk(pk))
    await client.remove(key)
    return {"ok": True}
