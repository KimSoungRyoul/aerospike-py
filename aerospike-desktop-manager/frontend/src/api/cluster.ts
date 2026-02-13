import api from "./client";
import type {
  ClusterOverview,
  NamespaceStats,
  SetInfo,
} from "./types";

export async function getClusterOverview(
  connId: string
): Promise<ClusterOverview> {
  const { data } = await api.get(`/c/${connId}/cluster`);
  return data;
}

export async function getNamespaces(connId: string): Promise<string[]> {
  const { data } = await api.get(`/c/${connId}/namespaces`);
  return data;
}

export async function getNamespaceDetail(
  connId: string,
  ns: string
): Promise<NamespaceStats> {
  const { data } = await api.get(`/c/${connId}/namespaces/${ns}`);
  return data;
}

export async function getSets(
  connId: string,
  ns: string
): Promise<SetInfo[]> {
  const { data } = await api.get(`/c/${connId}/namespaces/${ns}/sets`);
  return data;
}
