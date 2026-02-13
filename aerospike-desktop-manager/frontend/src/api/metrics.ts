import api from "./client";

export async function getServerMetrics(
  connId: string
): Promise<Record<string, string>> {
  const { data } = await api.get(`/c/${connId}/metrics/server`);
  return data;
}

export async function getNamespaceMetrics(
  connId: string,
  ns: string
): Promise<Record<string, string>> {
  const { data } = await api.get(
    `/c/${connId}/metrics/namespace/${ns}`
  );
  return data;
}

export async function executeTerminalCommand(
  connId: string,
  command: string,
  nodeName?: string
): Promise<{ raw: Record<string, string>; parsed: Record<string, unknown> }> {
  const { data } = await api.post(
    `/c/${connId}/info`,
    { command, node_name: nodeName }
  );
  return data;
}
