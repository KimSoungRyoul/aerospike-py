"""Cluster, node, and namespace models."""

from pydantic import BaseModel


class NodeInfo(BaseModel):
    name: str
    build: str = ""
    edition: str = ""
    namespaces: list[str] = []
    statistics: dict[str, str] = {}


class NamespaceStats(BaseModel):
    name: str
    objects: int = 0
    memory_used_bytes: int = 0
    memory_total_bytes: int = 0
    memory_free_pct: float = 0
    device_used_bytes: int = 0
    device_total_bytes: int = 0
    device_free_pct: float = 0
    replication_factor: int = 1
    stop_writes: bool = False
    high_water_disk_pct: float = 0
    high_water_memory_pct: float = 0
    raw: dict[str, str] = {}


class SetInfo(BaseModel):
    name: str
    objects: int = 0
    memory_data_bytes: int = 0
    stop_writes_count: int = 0
    truncate_lut: int = 0
    raw: dict[str, str] = {}


class BinInfo(BaseModel):
    name: str
    type: str = ""


class ClusterOverview(BaseModel):
    nodes: list[NodeInfo] = []
    namespaces: list[str] = []
    node_count: int = 0
    edition: str = ""
    build: str = ""
