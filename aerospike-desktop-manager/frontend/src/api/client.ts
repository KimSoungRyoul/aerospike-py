import axios from "axios";

const api = axios.create({
  baseURL: "/api/v1",
  headers: { "Content-Type": "application/json" },
  timeout: 30000,
});

/** Extract a readable error message from axios errors. */
export function formatApiError(e: unknown): string {
  if (axios.isAxiosError(e)) {
    const detail =
      e.response?.data?.detail || e.response?.data?.error;
    if (typeof detail === "string") return detail;
    if (e.message) return e.message;
  }
  return String(e);
}

export default api;
