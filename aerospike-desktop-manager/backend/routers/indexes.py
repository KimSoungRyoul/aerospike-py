"""Secondary index management router."""

import aerospike_py
from fastapi import APIRouter, Depends, HTTPException

from dependencies import get_client
from models.index import CreateIndexRequest, IndexInfo
from utils.info_parser import parse_sindex_info

router = APIRouter()


@router.get("/{ns}", response_model=list[IndexInfo])
async def list_indexes(
    ns: str,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    result = await client.info([f"sindex/{ns}"])
    raw_indexes = parse_sindex_info(result.get(f"sindex/{ns}", ""))
    indexes = []
    for idx in raw_indexes:
        indexes.append(
            IndexInfo(
                name=idx.get("indexname", ""),
                namespace=idx.get("ns", ns),
                set_name=idx.get("set", ""),
                bin_name=idx.get("bin", ""),
                index_type=idx.get("type", ""),
                state=idx.get("state", ""),
                raw=idx,
            )
        )
    return indexes


@router.post("/{ns}")
async def create_index(
    ns: str,
    req: CreateIndexRequest,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    type_map = {
        "numeric": client.index_integer_create,
        "integer": client.index_integer_create,
        "string": client.index_string_create,
        "geo2dsphere": client.index_geo2dsphere_create,
        "geo": client.index_geo2dsphere_create,
    }
    create_fn = type_map.get(req.index_type.lower())
    if not create_fn:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported index type: {req.index_type}. Use: numeric, string, geo2dsphere",
        )
    await create_fn(ns, req.set_name, req.bin_name, req.index_name)
    return {"ok": True}


@router.delete("/{ns}/{index_name}")
async def delete_index(
    ns: str,
    index_name: str,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    await client.index_remove(ns, index_name)
    return {"ok": True}
