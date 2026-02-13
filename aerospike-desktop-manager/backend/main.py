"""FastAPI application entry point."""

import logging
import os
from contextlib import asynccontextmanager

import aerospike_py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import settings
from dependencies import get_connection_manager
from exceptions import register_exception_handlers
from routers import (
    admin,
    batch,
    cluster,
    connections,
    import_export,
    indexes,
    metrics,
    namespaces,
    operations,
    records,
    terminal,
    truncate,
    udfs,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    manager = get_connection_manager()
    await manager.close_all()


app = FastAPI(
    title=settings.app_title,
    version="0.2.0",
    lifespan=lifespan,
)

# Exception handlers
register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global routes (connection-independent) ────────────────────


@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok"}


@app.get("/api/v1/metrics/client")
async def get_client_metrics():
    """Return aerospike-py OTel Prometheus metrics (global, no connection needed)."""
    metrics_text = aerospike_py.get_metrics()
    return {"metrics": metrics_text}


# ── API routers ───────────────────────────────────────────────

app.include_router(connections.router, prefix="/api/v1/connections", tags=["connections"])
app.include_router(cluster.router, prefix="/api/v1/c/{conn_id}/cluster", tags=["cluster"])
app.include_router(namespaces.router, prefix="/api/v1/c/{conn_id}/namespaces", tags=["namespaces"])
app.include_router(records.router, prefix="/api/v1/c/{conn_id}/records", tags=["records"])
app.include_router(operations.router, prefix="/api/v1/c/{conn_id}/records", tags=["operations"])
app.include_router(batch.router, prefix="/api/v1/c/{conn_id}/batch", tags=["batch"])
app.include_router(indexes.router, prefix="/api/v1/c/{conn_id}/indexes", tags=["indexes"])
app.include_router(truncate.router, prefix="/api/v1/c/{conn_id}/truncate", tags=["truncate"])
app.include_router(udfs.router, prefix="/api/v1/c/{conn_id}/udfs", tags=["udfs"])
app.include_router(admin.router, prefix="/api/v1/c/{conn_id}/admin", tags=["admin"])
app.include_router(metrics.router, prefix="/api/v1/c/{conn_id}/metrics", tags=["metrics"])
app.include_router(terminal.router, prefix="/api/v1/c/{conn_id}/info", tags=["info"])
app.include_router(import_export.router, prefix="/api/v1/c/{conn_id}/data", tags=["data"])

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")

# Serve frontend static files in production
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
