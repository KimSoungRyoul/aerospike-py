"""Centralized exception handling for aerospike-py errors."""

import logging

import aerospike_py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class ConnectionNotFoundError(Exception):
    """Connection ID does not exist."""


class ConnectionNotActiveError(Exception):
    """Connection exists but is not active."""


def register_exception_handlers(app: FastAPI) -> None:
    """Register aerospike-py exception → HTTP status code mappings."""

    @app.exception_handler(ConnectionNotFoundError)
    async def _connection_not_found(request: Request, exc: ConnectionNotFoundError):
        return JSONResponse(status_code=404, content={"error": "ConnectionNotFound", "detail": str(exc)})

    @app.exception_handler(ConnectionNotActiveError)
    async def _connection_not_active(request: Request, exc: ConnectionNotActiveError):
        return JSONResponse(status_code=409, content={"error": "ConnectionNotActive", "detail": str(exc)})

    @app.exception_handler(aerospike_py.RecordNotFound)
    async def _record_not_found(request: Request, exc: aerospike_py.RecordNotFound):
        return JSONResponse(status_code=404, content={"error": "RecordNotFound", "detail": str(exc)})

    @app.exception_handler(aerospike_py.RecordExistsError)
    async def _record_exists(request: Request, exc: aerospike_py.RecordExistsError):
        return JSONResponse(status_code=409, content={"error": "RecordExistsError", "detail": str(exc)})

    @app.exception_handler(aerospike_py.RecordGenerationError)
    async def _record_generation(request: Request, exc: aerospike_py.RecordGenerationError):
        return JSONResponse(status_code=409, content={"error": "RecordGenerationError", "detail": str(exc)})

    @app.exception_handler(aerospike_py.InvalidArgError)
    async def _invalid_arg(request: Request, exc: aerospike_py.InvalidArgError):
        return JSONResponse(status_code=400, content={"error": "InvalidArgError", "detail": str(exc)})

    @app.exception_handler(aerospike_py.AerospikeTimeoutError)
    async def _timeout(request: Request, exc: aerospike_py.AerospikeTimeoutError):
        return JSONResponse(status_code=504, content={"error": "AerospikeTimeoutError", "detail": str(exc)})

    @app.exception_handler(aerospike_py.ClusterError)
    async def _cluster(request: Request, exc: aerospike_py.ClusterError):
        return JSONResponse(status_code=503, content={"error": "ClusterError", "detail": str(exc)})

    @app.exception_handler(aerospike_py.AdminError)
    async def _admin(request: Request, exc: aerospike_py.AdminError):
        return JSONResponse(status_code=403, content={"error": "AdminError", "detail": str(exc)})

    @app.exception_handler(aerospike_py.AerospikeIndexError)
    async def _index(request: Request, exc: aerospike_py.AerospikeIndexError):
        return JSONResponse(status_code=400, content={"error": "AerospikeIndexError", "detail": str(exc)})

    @app.exception_handler(aerospike_py.UDFError)
    async def _udf(request: Request, exc: aerospike_py.UDFError):
        return JSONResponse(status_code=400, content={"error": "UDFError", "detail": str(exc)})

    @app.exception_handler(aerospike_py.ClientError)
    async def _client(request: Request, exc: aerospike_py.ClientError):
        return JSONResponse(status_code=400, content={"error": "ClientError", "detail": str(exc)})

    @app.exception_handler(aerospike_py.ServerError)
    async def _server(request: Request, exc: aerospike_py.ServerError):
        return JSONResponse(status_code=502, content={"error": "ServerError", "detail": str(exc)})

    @app.exception_handler(aerospike_py.AerospikeError)
    async def _aerospike_catch_all(request: Request, exc: aerospike_py.AerospikeError):
        logger.error("Unhandled AerospikeError: %s", exc)
        return JSONResponse(status_code=500, content={"error": "AerospikeError", "detail": str(exc)})
