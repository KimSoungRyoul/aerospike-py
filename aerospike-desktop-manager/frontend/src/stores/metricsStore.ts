import { create } from "zustand";

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

export const useMetricsStore = create<MetricsStore>((set, get) => ({
  history: [],
  connected: false,
  error: null,
  ws: null,

  connect: (connId) => {
    const existing = get().ws;
    if (existing) existing.close();

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const ws = new WebSocket(
      `${protocol}//${window.location.host}/api/v1/c/${connId}/metrics/stream`
    );

    ws.onopen = () => set({ connected: true, error: null });
    ws.onclose = () => set({ connected: false, ws: null });
    ws.onerror = () => {
      set({ error: "WebSocket connection failed" });
      ws.close();
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
    const { ws } = get();
    if (ws) ws.close();
    set({ ws: null, connected: false, history: [], error: null });
  },
}));
