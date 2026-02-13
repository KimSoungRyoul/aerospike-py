import { create } from "zustand";

type Theme = "light" | "dark" | "system";

interface UIStore {
  theme: Theme;
  sidebarOpen: boolean;
  terminalOpen: boolean;

  setTheme: (theme: Theme) => void;
  toggleSidebar: () => void;
  toggleTerminal: () => void;
}

export const useUIStore = create<UIStore>((set) => ({
  theme: "system",
  sidebarOpen: true,
  terminalOpen: false,

  setTheme: (theme) => {
    set({ theme });
    const root = document.documentElement;
    root.classList.remove("light", "dark");
    if (theme === "system") {
      const systemDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      root.classList.add(systemDark ? "dark" : "light");
    } else {
      root.classList.add(theme);
    }
  },

  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  toggleTerminal: () => set((s) => ({ terminalOpen: !s.terminalOpen })),
}));
