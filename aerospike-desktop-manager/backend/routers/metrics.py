"""Metrics and monitoring router with WebSocket support."""

import asyncio
import json
import logging

import aerospike_py
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from config import settings
from dependencies import get_client, get_connection_manager
from utils.info_parser import parse_info_list, parse_info_pairs

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/server")
async def get_server_metrics(
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    result = await client.info(["statistics"])
    return parse_info_pairs(result.get("statistics", ""))


@router.get("/namespace/{ns}")
async def get_namespace_metrics(
    ns: str,
    client: aerospike_py.AsyncClient = Depends(get_client),
):
    result = await client.info([f"namespace/{ns}"])
    return parse_info_pairs(result.get(f"namespace/{ns}", ""))


@router.websocket("/stream")
async def metrics_stream(
    websocket: WebSocket,
    conn_id: str,
):
    manager = get_connection_manager()
    await websocket.accept()

    mc = manager.get_managed_connection(conn_id)
    if not mc or not mc.client or not mc.connected:
        await websocket.close(code=4004, reason="Connection not found")
        return

    client = mc.client

    try:
        while True:
            try:
                stats_result = await client.info(["statistics"])
                stats = parse_info_pairs(stats_result.get("statistics", ""))

                ns_result = await client.info(["namespaces"])
                namespaces = parse_info_list(ns_result.get("namespaces", ""))

                async def _fetch_ns(ns: str) -> tuple[str, dict]:
                    ns_info = await client.info([f"namespace/{ns}"])
                    return ns, parse_info_pairs(ns_info.get(f"namespace/{ns}", ""))

                ns_results = await asyncio.gather(*[_fetch_ns(ns) for ns in namespaces])
                ns_stats = dict(ns_results)

                payload = {
                    "type": "metrics",
                    "server": stats,
                    "namespaces": ns_stats,
                    "client_metrics": aerospike_py.get_metrics(),
                }
                await websocket.send_text(json.dumps(payload, default=str))
            except WebSocketDisconnect:
                raise
            except Exception as e:
                logger.warning("Metrics collection error: %s", e)
                await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))

            await asyncio.sleep(settings.metrics_poll_interval)
    except WebSocketDisconnect:
        logger.debug("WebSocket disconnected for conn_id=%s", conn_id)
    except Exception as e:
        logger.error("Unexpected WebSocket error: %s", e)
        await websocket.close(code=1011, reason="Internal server error")
