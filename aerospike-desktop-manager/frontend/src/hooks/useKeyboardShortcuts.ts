import { useEffect } from "react";
import { useUIStore } from "@/stores/uiStore";

export function useKeyboardShortcuts() {
  const { toggleSidebar, toggleTerminal } = useUIStore();

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      // Ctrl+B or Cmd+B = toggle sidebar
      if ((e.ctrlKey || e.metaKey) && e.key === "b") {
        e.preventDefault();
        toggleSidebar();
      }
      // Ctrl+` or Cmd+` = toggle terminal
      if ((e.ctrlKey || e.metaKey) && e.key === "`") {
        e.preventDefault();
        toggleTerminal();
      }
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [toggleSidebar, toggleTerminal]);
}
