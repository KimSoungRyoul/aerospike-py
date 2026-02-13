"""UDF management router."""

import base64
import os
import tempfile

import aerospike_py
from fastapi import APIRouter, Depends

from dependencies import get_client
from models.udf import UdfExecuteRequest, UdfInfo, UdfUploadRequest
from utils.info_parser import parse_set_info

router = APIRouter()


@router.get("", response_model=list[UdfInfo])
async def list_udfs(
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    result = await client.info(["udf-list"])
    raw = result.get("udf-list", "")
    udfs = []
    for entry in parse_set_info(raw):
        udfs.append(
            UdfInfo(
                filename=entry.get("filename", ""),
                hash=entry.get("hash", ""),
                type=entry.get("type", "LUA"),
            )
        )
    return udfs


@router.post("")
async def upload_udf(
    req: UdfUploadRequest,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    tmp_path = None
    try:
        content = base64.b64decode(req.content)
        with tempfile.NamedTemporaryFile(suffix=".lua", delete=False) as f:
            tmp_path = f.name
            f.write(content)
            f.flush()
        await client.udf_put(tmp_path)
        return {"ok": True}
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.delete("/{module}")
async def delete_udf(
    module: str,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    await client.udf_remove(module)
    return {"ok": True}


@router.post("/apply")
async def apply_udf(
    req: UdfExecuteRequest,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    key = (req.namespace, req.set_name, req.key)
    result = await client.apply(key, req.module, req.function, req.args or None)
    return {"result": result}
