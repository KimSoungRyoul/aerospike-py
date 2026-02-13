import api from "./client";
import type { IndexInfo } from "./types";

export async function listIndexes(
  connId: string,
  ns: string
): Promise<IndexInfo[]> {
  const { data } = await api.get(`/c/${connId}/indexes/${ns}`);
  return data;
}

export async function createIndex(
  connId: string,
  ns: string,
  setName: string,
  binName: string,
  indexName: string,
  indexType: string
): Promise<void> {
  await api.post(`/c/${connId}/indexes/${ns}`, {
    set_name: setName,
    bin_name: binName,
    index_name: indexName,
    index_type: indexType,
  });
}

export async function deleteIndex(
  connId: string,
  ns: string,
  indexName: string
): Promise<void> {
  await api.delete(`/c/${connId}/indexes/${ns}/${indexName}`);
}
