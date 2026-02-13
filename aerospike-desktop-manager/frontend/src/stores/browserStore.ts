import { create } from "zustand";
import type { ScanResult, SetInfo } from "@/api/types";
import { formatApiError } from "@/api/client";
import * as clusterApi from "@/api/cluster";
import * as recordsApi from "@/api/records";

interface BrowserStore {
  namespaces: string[];
  sets: SetInfo[];
  selectedNs: string | null;
  selectedSet: string | null;
  browseResult: ScanResult | null;
  page: number;
  pageSize: number;
  loading: boolean;
  error: string | null;

  fetchNamespaces: (connId: string) => Promise<void>;
  fetchSets: (connId: string, ns: string) => Promise<void>;
  fetchRecords: (connId: string, ns: string, set: string) => Promise<void>;
  setPage: (page: number) => void;
  setSelectedNs: (ns: string | null) => void;
  setSelectedSet: (set: string | null) => void;
  clearError: () => void;
}

export const useBrowserStore = create<BrowserStore>((set, get) => ({
  namespaces: [],
  sets: [],
  selectedNs: null,
  selectedSet: null,
  browseResult: null,
  page: 1,
  pageSize: 50,
  loading: false,
  error: null,

  fetchNamespaces: async (connId) => {
    set({ loading: true, error: null });
    try {
      const namespaces = await clusterApi.getNamespaces(connId);
      set({ namespaces, loading: false });
    } catch (e) {
      set({ error: formatApiError(e), loading: false });
    }
  },

  fetchSets: async (connId, ns) => {
    set({ loading: true, selectedNs: ns, error: null });
    try {
      const sets = await clusterApi.getSets(connId, ns);
      set({ sets, loading: false });
    } catch (e) {
      set({ error: formatApiError(e), loading: false });
    }
  },

  fetchRecords: async (connId, ns, setName) => {
    set({ loading: true, selectedSet: setName, error: null });
    try {
      const { page, pageSize } = get();
      const browseResult = await recordsApi.browseRecords(
        connId,
        ns,
        setName,
        page,
        pageSize
      );
      set({ browseResult, loading: false });
    } catch (e) {
      set({ error: formatApiError(e), loading: false });
    }
  },

  setPage: (page) => set({ page }),
  setSelectedNs: (ns) => set({ selectedNs: ns, selectedSet: null, sets: [], browseResult: null }),
  setSelectedSet: (setName) => set({ selectedSet: setName, browseResult: null }),
  clearError: () => set({ error: null }),
}));
