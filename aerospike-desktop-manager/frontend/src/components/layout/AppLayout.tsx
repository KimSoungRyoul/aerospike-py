import { Link, Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { TabBar } from "./TabBar";
import { useUIStore } from "@/stores/uiStore";
import { useConnectionStore } from "@/stores/connectionStore";
import { TerminalPanel } from "@/components/terminal/TerminalPanel";
import { useKeyboardShortcuts } from "@/hooks/useKeyboardShortcuts";
import { useMediaQuery } from "@/hooks/useMediaQuery";
import { Sheet, SheetContent } from "@/components/ui/sheet";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  Database,
  Sun,
  Moon,
  PanelLeftClose,
  PanelLeft,
  Terminal,
} from "lucide-react";
import { Button } from "@/components/ui/button";

export function AppLayout() {
  const { sidebarOpen, toggleSidebar, terminalOpen, toggleTerminal, theme, setTheme } =
    useUIStore();
  const isMobile = useMediaQuery("(max-width: 768px)");

  useKeyboardShortcuts();

  return (
    <div className="flex h-screen flex-col overflow-hidden">
      {/* Top bar */}
      <header className="flex h-12 items-center justify-between border-b bg-card px-4">
        <Link
          to="/"
          className="flex items-center gap-2 hover:opacity-80 transition-opacity"
          onClick={() => useConnectionStore.getState().setActiveConnection(null)}
        >
          <Database className="h-5 w-5 text-primary" aria-hidden="true" />
          <span className="font-semibold text-sm tracking-tight">Aerospike Desktop Manager</span>
        </Link>
        <div className="flex items-center gap-1">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8"
                onClick={toggleTerminal}
                aria-label="Toggle terminal"
              >
                <Terminal className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom">
              <p>Toggle Terminal <kbd className="ml-1 rounded bg-muted px-1 py-0.5 text-[10px] font-mono">⌘`</kbd></p>
            </TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8"
                onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
                aria-label={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
              >
                {theme === "dark" ? (
                  <Sun className="h-4 w-4" />
                ) : (
                  <Moon className="h-4 w-4" />
                )}
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom">
              <p>{theme === "dark" ? "Light mode" : "Dark mode"}</p>
            </TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8"
                onClick={toggleSidebar}
                aria-label={sidebarOpen ? "Close sidebar" : "Open sidebar"}
              >
                {sidebarOpen ? (
                  <PanelLeftClose className="h-4 w-4" />
                ) : (
                  <PanelLeft className="h-4 w-4" />
                )}
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom">
              <p>Toggle Sidebar <kbd className="ml-1 rounded bg-muted px-1 py-0.5 text-[10px] font-mono">⌘B</kbd></p>
            </TooltipContent>
          </Tooltip>
        </div>
      </header>

      {/* Main area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Desktop sidebar */}
        {!isMobile && (
          <aside
            className={`flex-shrink-0 border-r bg-card transition-all duration-200 overflow-hidden ${
              sidebarOpen ? "w-60" : "w-0 border-r-0"
            }`}
          >
            <div className="w-60">
              <Sidebar />
            </div>
          </aside>
        )}
        {/* Mobile sidebar as sheet */}
        {isMobile && (
          <Sheet open={sidebarOpen} onOpenChange={toggleSidebar}>
            <SheetContent side="left" className="w-60 p-0">
              <Sidebar />
            </SheetContent>
          </Sheet>
        )}
        <main className="flex flex-1 flex-col overflow-hidden">
          <TabBar />
          <div className="flex-1 overflow-auto p-4">
            <div className="animate-in fade-in duration-300">
              <Outlet />
            </div>
          </div>
        </main>
      </div>

      {/* Terminal panel */}
      <div
        className={`border-t bg-card transition-all duration-200 overflow-hidden ${
          terminalOpen ? "h-64" : "h-0 border-t-0"
        }`}
      >
        <TerminalPanel />
      </div>
    </div>
  );
}
