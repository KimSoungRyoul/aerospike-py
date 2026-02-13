"""Connection management router."""

import logging

from fastapi import APIRouter, Depends

from dependencies import get_connection_manager
from exceptions import ConnectionNotFoundError
from models.connection import ConnectionProfile, ConnectionStatus, ConnectionTestResult
from services.connection_manager import ConnectionManager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=list[ConnectionStatus])
async def list_connections(
    manager: ConnectionManager = Depends(get_connection_manager),
):
    return manager.list_connections()


@router.post("", response_model=ConnectionStatus)
async def create_connection(
    profile: ConnectionProfile,
    manager: ConnectionManager = Depends(get_connection_manager),
):
    conn_id = await manager.connect(profile)
    statuses = manager.list_connections()
    return next(s for s in statuses if s.id == conn_id)


# Static paths MUST be registered before parameterized paths
@router.post("/test", response_model=ConnectionTestResult)
async def test_new_connection(
    profile: ConnectionProfile,
    manager: ConnectionManager = Depends(get_connection_manager),
):
    return await manager.test_connection(profile)


@router.get("/export/all")
async def export_connections(
    manager: ConnectionManager = Depends(get_connection_manager),
):
    return manager.export_profiles()


@router.post("/import/bulk")
async def import_connections(
    profiles: list[dict],
    manager: ConnectionManager = Depends(get_connection_manager),
):
    ids = await manager.import_profiles(profiles)
    return {"imported": len(ids), "ids": ids}


# Parameterized paths below
@router.get("/{conn_id}", response_model=ConnectionStatus)
async def get_connection(
    conn_id: str,
    manager: ConnectionManager = Depends(get_connection_manager),
):
    statuses = manager.list_connections()
    for s in statuses:
        if s.id == conn_id:
            return s
    raise ConnectionNotFoundError(f"Connection '{conn_id}' not found")


@router.put("/{conn_id}", response_model=ConnectionStatus)
async def update_connection(
    conn_id: str,
    profile: ConnectionProfile,
    manager: ConnectionManager = Depends(get_connection_manager),
):
    await manager.update_profile(conn_id, profile)
    statuses = manager.list_connections()
    return next(s for s in statuses if s.id == conn_id)


@router.delete("/{conn_id}")
async def delete_connection(
    conn_id: str,
    manager: ConnectionManager = Depends(get_connection_manager),
):
    await manager.remove(conn_id)
    return {"ok": True}


@router.post("/{conn_id}/test", response_model=ConnectionTestResult)
async def test_existing_connection(
    conn_id: str,
    manager: ConnectionManager = Depends(get_connection_manager),
):
    profile = manager.get_profile(conn_id)
    return await manager.test_connection(profile)
