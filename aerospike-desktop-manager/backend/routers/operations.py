"""Record operations router — touch, append, prepend, increment, remove_bin, operate."""

import aerospike_py
from fastapi import APIRouter, Depends

from dependencies import get_client
from models.record import (
    AppendRequest,
    IncrementRequest,
    OperateRequest,
    PrependRequest,
    RecordResponse,
    RemoveBinRequest,
    TouchRequest,
)
from utils.constants import SEND_KEY_POLICY
from utils.serialization import format_bins, serialize_key

router = APIRouter()


@router.post("/touch")
async def touch_record(
    req: TouchRequest,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    key = (req.namespace, req.set, req.key)
    await client.touch(key, req.val, policy=SEND_KEY_POLICY)
    return {"ok": True}


@router.post("/append")
async def append_record(
    req: AppendRequest,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    key = (req.namespace, req.set, req.key)
    await client.append(key, req.bin, req.val, policy=SEND_KEY_POLICY)
    return {"ok": True}


@router.post("/prepend")
async def prepend_record(
    req: PrependRequest,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    key = (req.namespace, req.set, req.key)
    await client.prepend(key, req.bin, req.val, policy=SEND_KEY_POLICY)
    return {"ok": True}


@router.post("/increment")
async def increment_record(
    req: IncrementRequest,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    key = (req.namespace, req.set, req.key)
    await client.increment(key, req.bin, req.offset, policy=SEND_KEY_POLICY)
    return {"ok": True}


@router.post("/remove-bin")
async def remove_bin(
    req: RemoveBinRequest,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    key = (req.namespace, req.set, req.key)
    await client.remove_bin(key, req.bin_names, policy=SEND_KEY_POLICY)
    return {"ok": True}


@router.post("/operate", response_model=RecordResponse)
async def operate_record(
    req: OperateRequest,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    key = (req.namespace, req.set, req.key)
    rec_key, meta, bins = await client.operate(key, req.ops, policy=SEND_KEY_POLICY)
    return RecordResponse(key=serialize_key(rec_key), meta=meta, bins=format_bins(bins))


@router.post("/operate-ordered")
async def operate_ordered_record(
    req: OperateRequest,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    key = (req.namespace, req.set, req.key)
    rec_key, meta, ordered_bins = await client.operate_ordered(key, req.ops, policy=SEND_KEY_POLICY)
    return {"key": serialize_key(rec_key), "meta": meta, "bins": ordered_bins}
