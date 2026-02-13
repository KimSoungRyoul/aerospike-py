export interface ConnectionProfile {
  id?: string;
  name: string;
  hosts: [string, number][];
  cluster_name?: string;
  username?: string;
  password?: string;
  color?: string;
}

export interface ConnectionStatus {
  id: string;
  name: string;
  connected: boolean;
  cluster_name: string;
  node_count: number;
  namespaces: string[];
  color: string;
}

export interface ClusterOverview {
  nodes: NodeInfo[];
  namespaces: string[];
  node_count: number;
  edition: string;
  build: string;
}

export interface NodeInfo {
  name: string;
  build: string;
  edition: string;
  namespaces: string[];
  statistics: Record<string, string>;
}

export interface NamespaceStats {
  name: string;
  objects: number;
  memory_used_bytes: number;
  memory_total_bytes: number;
  memory_free_pct: number;
  device_used_bytes: number;
  device_total_bytes: number;
  device_free_pct: number;
  replication_factor: number;
  stop_writes: boolean;
  high_water_disk_pct: number;
  high_water_memory_pct: number;
  raw: Record<string, string>;
}

export interface SetInfo {
  name: string;
  objects: number;
  memory_data_bytes: number;
  stop_writes_count: number;
  truncate_lut: number;
}

export interface RecordResponse {
  key: [string, string, string | number | null, string | null] | null;
  meta: { gen: number; ttl: number } | null;
  bins: Record<string, { value: unknown; type: string }> | null;
}

export interface ScanResult {
  records: RecordResponse[];
  total_scanned: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

/** @deprecated Use ScanResult instead */
export type BrowseResult = ScanResult;

export interface IndexInfo {
  name: string;
  namespace: string;
  set_name: string;
  bin_name: string;
  index_type: string;
  state: string;
}

export interface UdfInfo {
  filename: string;
  hash: string;
  type: string;
}
