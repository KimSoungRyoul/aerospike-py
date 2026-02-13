"""FastAPI dependency injection."""

import aerospike_py
from fastapi import Depends

from exceptions import ConnectionNotActiveError, ConnectionNotFoundError
from services.connection_manager import ConnectionManager

_connection_manager: ConnectionManager | None = None


def get_connection_manager() -> ConnectionManager:
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = ConnectionManager()
    return _connection_manager


def get_client(
    conn_id: str,
    manager: ConnectionManager = Depends(get_connection_manager),
) -> aerospike_py.AsyncClient:
    """Resolve connection ID to an active AsyncClient."""
    mc = manager.get_managed_connection(conn_id)
    if not mc:
        raise ConnectionNotFoundError(f"Connection '{conn_id}' not found")
    if not mc.client or not mc.connected:
        raise ConnectionNotActiveError(f"Connection '{conn_id}' is not active")
    return mc.client
