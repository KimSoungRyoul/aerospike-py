import { create } from "zustand";

const MAX_RECONNECT_ATTEMPTS = 5;
const BASE_RECONNECT_DELAY = 1000;

interface MetricSnapshot {
  timestamp: number;
  server: Record<string, string>;
  namespaces: Record<string, Record<string, string>>;
}

interface MetricsStore {
  history: MetricSnapshot[];
  connected: boolean;
  error: string | null;
  ws: WebSocket | null;

  connect: (connId: string) => void;
  disconnect: () => void;
}

export const useMetricsStore = create<MetricsStore>((set, get) => {
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  let reconnectAttempts = 0;
  let currentConnId: string | null = null;

  const clearReconnectTimer = () => {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }
  };

  const scheduleReconnect = () => {
    if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
      set({ error: `Reconnection failed after ${MAX_RECONNECT_ATTEMPTS} attempts` });
      return;
    }
    const delay = BASE_RECONNECT_DELAY * Math.pow(2, reconnectAttempts);
    reconnectAttempts++;
    reconnectTimer = setTimeout(() => {
      if (currentConnId) {
        get().connect(currentConnId);
      }
    }, delay);
  };

  return {
    history: [],
    connected: false,
    error: null,
    ws: null,

    connect: (connId) => {
      const existing = get().ws;
      if (existing) existing.close();
      clearReconnectTimer();

      currentConnId = connId;

      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const ws = new WebSocket(
        `${protocol}//${window.location.host}/api/v1/c/${connId}/metrics/stream`
      );

      ws.onopen = () => {
        reconnectAttempts = 0;
        set({ connected: true, error: null });
      };
      ws.onclose = (event) => {
        set({ connected: false, ws: null });
        // Only auto-reconnect for unexpected closures (not user-initiated disconnect)
        if (currentConnId && event.code !== 1000) {
          scheduleReconnect();
        }
      };
      ws.onerror = () => {
        set({ error: "WebSocket connection failed" });
      };
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === "error") {
            set({ error: data.message });
            return;
          }
          if (data.type === "metrics") {
            set((state) => ({
              error: null,
              history: [
                ...state.history.slice(-59),
                {
                  timestamp: Date.now(),
                  server: data.server,
                  namespaces: data.namespaces,
                },
              ],
            }));
          }
        } catch {
          // ignore parse errors
        }
      };

      set({ ws });
    },

    disconnect: () => {
      currentConnId = null;
      clearReconnectTimer();
      reconnectAttempts = 0;
      const { ws } = get();
      if (ws) ws.close(1000, "User disconnected");
      set({ ws: null, connected: false, history: [], error: null });
    },
  };
});
