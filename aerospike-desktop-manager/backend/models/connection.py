"""Connection profile and status models."""

from pydantic import BaseModel, Field


class ConnectionProfile(BaseModel):
    id: str = ""
    name: str = Field(..., description="Display name (e.g. 'Production Cluster')")
    hosts: list[tuple[str, int]] = Field(..., description="List of (host, port) tuples")
    cluster_name: str = ""
    username: str | None = None
    password: str | None = None
    color: str = "#3b82f6"  # Default blue


class ConnectionStatus(BaseModel):
    id: str
    name: str
    connected: bool
    cluster_name: str = ""
    node_count: int = 0
    namespaces: list[str] = []
    color: str = "#3b82f6"


class ConnectionTestResult(BaseModel):
    success: bool
    message: str
    node_count: int = 0
    namespaces: list[str] = []
