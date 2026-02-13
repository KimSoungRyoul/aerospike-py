"""Batch operations router."""

import aerospike_py
from fastapi import APIRouter, Depends

from dependencies import get_client
from models.record import BatchOperateRequest, BatchReadRequest, BatchRemoveRequest
from utils.serialization import format_bins, serialize_key

router = APIRouter()


def _key_specs_to_tuples(key_specs):
    return [(ks.namespace, ks.set, ks.key) for ks in key_specs]


@router.post("/read")
async def batch_read(
    req: BatchReadRequest,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    keys = _key_specs_to_tuples(req.keys)
    result = await client.batch_read(keys, req.bins)
    records = []
    for br in result.batch_records:
        if br.record:
            key, meta, bins = br.record
            records.append({"key": serialize_key(key), "meta": meta, "bins": format_bins(bins), "result": br.result})
        else:
            records.append({"key": serialize_key(br.key), "meta": None, "bins": None, "result": br.result})
    return {"records": records}


@router.post("/operate")
async def batch_operate(
    req: BatchOperateRequest,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    keys = _key_specs_to_tuples(req.keys)
    results = await client.batch_operate(keys, req.ops)
    records = []
    for rec in results:
        key, meta, bins = rec
        records.append({"key": serialize_key(key), "meta": meta, "bins": format_bins(bins)})
    return {"records": records}


@router.post("/remove")
async def batch_remove(
    req: BatchRemoveRequest,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    keys = _key_specs_to_tuples(req.keys)
    results = await client.batch_remove(keys)
    records = []
    for rec in results:
        key, meta, bins = rec
        records.append({"key": serialize_key(key), "meta": meta, "bins": format_bins(bins)})
    return {"records": records}
