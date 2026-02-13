import api from "./client";
import type { ConnectionProfile, ConnectionStatus } from "./types";

export async function listConnections(): Promise<ConnectionStatus[]> {
  const { data } = await api.get("/connections");
  return data;
}

export async function createConnection(
  profile: ConnectionProfile
): Promise<ConnectionStatus> {
  const { data } = await api.post("/connections", profile);
  return data;
}

export async function deleteConnection(id: string): Promise<void> {
  await api.delete(`/connections/${id}`);
}

export async function testConnection(
  profile: ConnectionProfile
): Promise<{ success: boolean; message: string }> {
  const { data } = await api.post("/connections/test", profile);
  return data;
}
