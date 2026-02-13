"""Data import/export router."""

import aerospike_py
from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from dependencies import get_client
from services.import_export import ImportExportService

router = APIRouter()


class ImportRequest(BaseModel):
    data: str
    format: str = "json"


@router.get("/export/{ns}/{set_name}")
async def export_data(
    ns: str,
    set_name: str,
    format: str = Query("json", pattern="^(json|csv)$"),
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    service = ImportExportService(client)

    if format == "csv":
        content = await service.export_csv(ns, set_name)
        return PlainTextResponse(content, media_type="text/csv")
    else:
        content = await service.export_json(ns, set_name)
        return PlainTextResponse(content, media_type="application/json")


@router.post("/import/{ns}/{set_name}")
async def import_data(
    ns: str,
    set_name: str,
    req: ImportRequest,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    service = ImportExportService(client)
    count = await service.import_json(ns, set_name, req.data)
    return {"imported": count}
