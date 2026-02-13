import { create } from "zustand";
import type { ConnectionStatus } from "@/api/types";
import { formatApiError } from "@/api/client";
import * as connectionsApi from "@/api/connections";

interface ConnectionStore {
  connections: ConnectionStatus[];
  activeConnectionId: string | null;
  loading: boolean;
  error: string | null;

  fetchConnections: () => Promise<void>;
  addConnection: (profile: Parameters<typeof connectionsApi.createConnection>[0]) => Promise<ConnectionStatus>;
  removeConnection: (id: string) => Promise<void>;
  setActiveConnection: (id: string | null) => void;
  clearError: () => void;
}

export const useConnectionStore = create<ConnectionStore>((set) => ({
  connections: [],
  activeConnectionId: null,
  loading: false,
  error: null,

  fetchConnections: async () => {
    set({ loading: true, error: null });
    try {
      const connections = await connectionsApi.listConnections();
      set({ connections, loading: false });
    } catch (e) {
      set({ error: formatApiError(e), loading: false });
    }
  },

  addConnection: async (profile) => {
    set({ error: null });
    try {
      const conn = await connectionsApi.createConnection(profile);
      set((state) => ({
        connections: [...state.connections, conn],
        activeConnectionId: conn.id,
      }));
      return conn;
    } catch (e) {
      const msg = formatApiError(e);
      set({ error: msg });
      throw new Error(msg);
    }
  },

  removeConnection: async (id) => {
    set({ error: null });
    try {
      await connectionsApi.deleteConnection(id);
      set((state) => ({
        connections: state.connections.filter((c) => c.id !== id),
        activeConnectionId:
          state.activeConnectionId === id ? null : state.activeConnectionId,
      }));
    } catch (e) {
      set({ error: formatApiError(e) });
    }
  },

  setActiveConnection: (id) => set({ activeConnectionId: id }),
  clearError: () => set({ error: null }),
}));
