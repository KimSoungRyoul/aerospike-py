import api from "./client";
import type { ScanResult, RecordResponse } from "./types";

export async function browseRecords(
  connId: string,
  ns: string,
  set: string,
  page = 1,
  pageSize = 50
): Promise<ScanResult> {
  const { data } = await api.post(`/c/${connId}/records/scan`, {
    namespace: ns,
    set,
    page,
    page_size: pageSize,
  });
  return data;
}

export async function getRecord(
  connId: string,
  ns: string,
  set: string,
  pk: string
): Promise<RecordResponse> {
  const { data } = await api.get(
    `/c/${connId}/records/${ns}/${set}/${pk}`
  );
  return data;
}

export async function createRecord(
  connId: string,
  ns: string,
  set: string,
  key: string | number,
  bins: Record<string, unknown>,
  ttl?: number
): Promise<void> {
  await api.post(`/c/${connId}/records/put`, {
    namespace: ns,
    set,
    key,
    bins,
    ttl,
  });
}

export async function updateRecord(
  connId: string,
  ns: string,
  set: string,
  pk: string,
  bins: Record<string, unknown>,
  ttl?: number
): Promise<void> {
  await api.post(`/c/${connId}/records/put`, {
    namespace: ns,
    set,
    key: pk,
    bins,
    ttl,
  });
}

export async function deleteRecord(
  connId: string,
  ns: string,
  set: string,
  pk: string
): Promise<void> {
  await api.delete(`/c/${connId}/records/${ns}/${set}/${pk}`);
}
