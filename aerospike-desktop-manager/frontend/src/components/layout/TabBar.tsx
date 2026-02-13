import { useLocation, useNavigate } from "react-router-dom";
import { useConnectionStore } from "@/stores/connectionStore";
import { cn } from "@/lib/utils";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  Database,
  Server,
  Activity,
  ListTree,
  Code2,
  Terminal,
} from "lucide-react";

const tabs = [
  { path: "browser", label: "Browser", icon: Database },
  { path: "cluster", label: "Cluster", icon: Server },
  { path: "metrics", label: "Metrics", icon: Activity },
  { path: "indexes", label: "Indexes", icon: ListTree },
  { path: "udfs", label: "UDFs", icon: Code2 },
  { path: "terminal", label: "Terminal", icon: Terminal },
];

export function TabBar() {
  const { activeConnectionId, connections } = useConnectionStore();
  const location = useLocation();
  const navigate = useNavigate();

  if (!activeConnectionId) {
    return (
      <nav className="flex items-center border-b bg-card px-4 py-2">
        <span className="text-sm text-muted-foreground">Select a connection to get started</span>
      </nav>
    );
  }

  const activeConnection = connections.find((c) => c.id === activeConnectionId);
  const currentTab = tabs.find((t) =>
    location.pathname.startsWith(`/${t.path}`)
  );

  return (
    <nav className="flex border-b bg-card" role="tablist" aria-label="Main navigation">
      {activeConnection && (
        <div className="flex items-center gap-1.5 border-r px-3 py-2">
          <div className="h-2 w-2 rounded-full" style={{ backgroundColor: activeConnection.color }} />
          <span className="text-xs font-medium truncate max-w-[120px]">{activeConnection.name}</span>
        </div>
      )}
      {tabs.map((tab) => {
        const Icon = tab.icon;
        const isActive = currentTab?.path === tab.path;
        return (
          <Tooltip key={tab.path}>
            <TooltipTrigger asChild>
              <button
                role="tab"
                aria-selected={isActive}
                onClick={() =>
                  navigate(`/${tab.path}/${activeConnectionId}`)
                }
                className={cn(
                  "relative flex items-center gap-1.5 px-4 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "text-foreground"
                    : "text-muted-foreground hover:text-foreground"
                )}
              >
                <Icon className="h-4 w-4" aria-hidden="true" />
                {tab.label}
                {isActive && (
                  <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-foreground" />
                )}
              </button>
            </TooltipTrigger>
            <TooltipContent side="bottom">
              <p>{tab.label}</p>
            </TooltipContent>
          </Tooltip>
        );
      })}
    </nav>
  );
}
