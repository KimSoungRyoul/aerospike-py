import api from "./client";
import type { UdfInfo } from "./types";

export async function listUdfs(connId: string): Promise<UdfInfo[]> {
  const { data } = await api.get(`/c/${connId}/udfs`);
  return data;
}

export async function uploadUdf(
  connId: string,
  filename: string,
  content: string
): Promise<void> {
  await api.post(`/c/${connId}/udfs`, { filename, content });
}

export async function deleteUdf(
  connId: string,
  module: string
): Promise<void> {
  await api.delete(`/c/${connId}/udfs/${module}`);
}

export async function applyUdf(
  connId: string,
  namespace: string,
  setName: string,
  key: string | number,
  module: string,
  fn: string,
  args: unknown[] = []
): Promise<unknown> {
  const { data } = await api.post(`/c/${connId}/udfs/apply`, {
    namespace,
    set_name: setName,
    key,
    module,
    function: fn,
    args,
  });
  return data.result;
}
