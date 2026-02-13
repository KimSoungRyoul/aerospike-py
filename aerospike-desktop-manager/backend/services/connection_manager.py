"""Multi-cluster connection manager."""

import uuid
from dataclasses import dataclass

import aerospike_py

from exceptions import ConnectionNotFoundError
from models.connection import ConnectionProfile, ConnectionStatus, ConnectionTestResult


@dataclass
class ManagedConnection:
    profile: ConnectionProfile
    client: aerospike_py.AsyncClient | None = None
    connected: bool = False


class ConnectionManager:
    def __init__(self):
        self._connections: dict[str, ManagedConnection] = {}

    async def connect(self, profile: ConnectionProfile) -> str:
        if not profile.id:
            profile.id = uuid.uuid4().hex[:12]

        config = {"hosts": profile.hosts}
        if profile.cluster_name:
            config["cluster_name"] = profile.cluster_name

        client = aerospike_py.AsyncClient(config)
        await client.connect(profile.username, profile.password)

        self._connections[profile.id] = ManagedConnection(
            profile=profile,
            client=client,
            connected=True,
        )
        return profile.id

    async def disconnect(self, conn_id: str) -> None:
        mc = self._connections.get(conn_id)
        if mc and mc.client:
            await mc.client.close()
            mc.connected = False
            mc.client = None

    async def remove(self, conn_id: str) -> None:
        await self.disconnect(conn_id)
        self._connections.pop(conn_id, None)

    def get_profile(self, conn_id: str) -> ConnectionProfile:
        mc = self._connections.get(conn_id)
        if not mc:
            raise ConnectionNotFoundError(f"Connection '{conn_id}' not found")
        return mc.profile

    def list_connections(self) -> list[ConnectionStatus]:
        results = []
        for conn_id, mc in self._connections.items():
            results.append(
                ConnectionStatus(
                    id=conn_id,
                    name=mc.profile.name,
                    connected=mc.connected,
                    cluster_name=mc.profile.cluster_name,
                    color=mc.profile.color,
                )
            )
        return results

    async def test_connection(self, profile: ConnectionProfile) -> ConnectionTestResult:
        config = {"hosts": profile.hosts}
        if profile.cluster_name:
            config["cluster_name"] = profile.cluster_name

        client = aerospike_py.AsyncClient(config)
        try:
            await client.connect(profile.username, profile.password)
            node_names = await client.get_node_names()
            info = await client.info(["namespaces"])
            ns_list = info.get("namespaces", "").split(";")
            ns_list = [ns for ns in ns_list if ns]
            await client.close()
            return ConnectionTestResult(
                success=True,
                message=f"Connected to {len(node_names)} node(s)",
                node_count=len(node_names),
                namespaces=ns_list,
            )
        except Exception as e:
            try:
                await client.close()
            except Exception:
                pass
            return ConnectionTestResult(success=False, message=str(e))

    async def update_profile(self, conn_id: str, profile: ConnectionProfile) -> None:
        mc = self._connections.get(conn_id)
        if not mc:
            raise ConnectionNotFoundError(f"Connection '{conn_id}' not found")
        profile.id = conn_id
        mc.profile = profile

    def export_profiles(self) -> list[dict]:
        return [mc.profile.model_dump(exclude={"password"}) for mc in self._connections.values()]

    async def import_profiles(self, profiles: list[dict]) -> list[str]:
        ids = []
        for p in profiles:
            profile = ConnectionProfile(**p)
            conn_id = await self.connect(profile)
            ids.append(conn_id)
        return ids

    async def close_all(self) -> None:
        for conn_id in list(self._connections.keys()):
            await self.disconnect(conn_id)
        self._connections.clear()
