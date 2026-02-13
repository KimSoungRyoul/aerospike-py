"""Truncate router."""

import aerospike_py
from fastapi import APIRouter, Depends

from dependencies import get_client
from models.record import TruncateRequest

router = APIRouter()


@router.post("")
async def truncate_set(
    req: TruncateRequest,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    await client.truncate(req.namespace, req.set, req.nanos)
    return {"ok": True}
