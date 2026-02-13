import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import type { ConnectionStatus, SetInfo } from "@/api/types";
import { useConnectionStore } from "@/stores/connectionStore";
import * as clusterApi from "@/api/cluster";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuTrigger,
  ContextMenuSeparator,
} from "@/components/ui/context-menu";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Skeleton } from "@/components/ui/skeleton";
import {
  ChevronDown,
  ChevronRight,
  Database,
  Table2,
  Trash2,
  Eye,
  Server,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface Props {
  connection: ConnectionStatus;
}

interface NamespaceNode {
  name: string;
  sets: SetInfo[];
  expanded: boolean;
}

export function ConnectionTree({ connection }: Props) {
  const navigate = useNavigate();
  const { activeConnectionId, setActiveConnection, removeConnection } = useConnectionStore();
  const [expanded, setExpanded] = useState(false);
  const [namespaces, setNamespaces] = useState<NamespaceNode[]>([]);
  const [loading, setLoading] = useState(false);
  const [showDeleteAlert, setShowDeleteAlert] = useState(false);
  const mountedRef = useRef(true);

  useEffect(() => {
    return () => { mountedRef.current = false; };
  }, []);

  const toggle = async () => {
    if (!expanded && namespaces.length === 0) {
      setLoading(true);
      try {
        const nsList = await clusterApi.getNamespaces(connection.id);
        setNamespaces(nsList.map((ns) => ({ name: ns, sets: [], expanded: false })));
      } catch {
        // ignore
      } finally {
        setLoading(false);
      }
    }
    setExpanded(!expanded);
    setActiveConnection(connection.id);
  };

  const toggleNs = async (nsName: string) => {
    setNamespaces((prev) =>
      prev.map((ns) => {
        if (ns.name !== nsName) return ns;
        if (!ns.expanded && ns.sets.length === 0) {
          clusterApi.getSets(connection.id, nsName).then((sets) => {
            if (!mountedRef.current) return;
            setNamespaces((p) =>
              p.map((n) => (n.name === nsName ? { ...n, sets } : n))
            );
          });
        }
        return { ...ns, expanded: !ns.expanded };
      })
    );
  };

  const handleDelete = () => {
    removeConnection(connection.id);
    setShowDeleteAlert(false);
  };

  const isActive = connection.id === activeConnectionId;

  return (
    <>
      <div className="mb-0.5">
        <ContextMenu>
          <ContextMenuTrigger asChild>
            <div className={cn(
              "group flex items-center gap-1 rounded-md px-2 py-1 transition-colors",
              isActive ? "bg-accent border-l-2 border-l-primary" : "hover:bg-accent"
            )}>
              <button onClick={toggle} className="flex flex-1 items-center gap-1.5 text-sm">
                {expanded ? (
                  <ChevronDown className="h-3 w-3 shrink-0" />
                ) : (
                  <ChevronRight className="h-3 w-3 shrink-0" />
                )}
                <div
                  className="h-2.5 w-2.5 rounded-full shrink-0"
                  style={{ backgroundColor: connection.color }}
                />
                <span className="truncate font-medium">{connection.name}</span>
              </button>
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
                onClick={(e) => {
                  e.stopPropagation();
                  setShowDeleteAlert(true);
                }}
              >
                <Trash2 className="h-3 w-3 text-muted-foreground" />
              </Button>
            </div>
          </ContextMenuTrigger>
          <ContextMenuContent>
            <ContextMenuItem onClick={() => {
              setActiveConnection(connection.id);
              navigate(`/browser/${connection.id}`);
            }}>
              <Eye className="mr-2 h-4 w-4" />
              Open Browser
            </ContextMenuItem>
            <ContextMenuItem onClick={() => {
              setActiveConnection(connection.id);
              navigate(`/cluster/${connection.id}`);
            }}>
              <Server className="mr-2 h-4 w-4" />
              View Cluster
            </ContextMenuItem>
            <ContextMenuSeparator />
            <ContextMenuItem
              className="text-destructive focus:text-destructive"
              onClick={() => setShowDeleteAlert(true)}
            >
              <Trash2 className="mr-2 h-4 w-4" />
              Delete Connection
            </ContextMenuItem>
          </ContextMenuContent>
        </ContextMenu>

        <Collapsible open={expanded}>
          <CollapsibleContent>
            <div className="ml-4">
              {loading && (
                <div className="space-y-1 px-2 py-1">
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-4 w-20" />
                </div>
              )}
              {namespaces.map((ns) => (
                <Collapsible key={ns.name} open={ns.expanded}>
                  <CollapsibleTrigger asChild>
                    <button
                      onClick={() => toggleNs(ns.name)}
                      className="flex w-full items-center gap-1.5 rounded-md px-2 py-1 text-sm hover:bg-accent transition-colors"
                    >
                      {ns.expanded ? (
                        <ChevronDown className="h-3 w-3 shrink-0" />
                      ) : (
                        <ChevronRight className="h-3 w-3 shrink-0" />
                      )}
                      <Database className="h-3 w-3 text-blue-500 shrink-0" />
                      <span>{ns.name}</span>
                    </button>
                  </CollapsibleTrigger>
                  <CollapsibleContent>
                    <div className="ml-4">
                      {ns.sets.length === 0 && (
                        <div className="px-2 py-1 text-xs text-muted-foreground">
                          No sets
                        </div>
                      )}
                      {ns.sets.map((set) => (
                        <button
                          key={set.name}
                          onClick={() => {
                            setActiveConnection(connection.id);
                            navigate(
                              `/browser/${connection.id}/${ns.name}/${set.name}`
                            );
                          }}
                          className="flex w-full items-center gap-1.5 rounded-md px-2 py-1 text-sm hover:bg-accent transition-colors"
                        >
                          <Table2 className="h-3 w-3 text-green-500 shrink-0" />
                          <span>{set.name}</span>
                          <span className="ml-auto text-xs text-muted-foreground">
                            {set.objects}
                          </span>
                        </button>
                      ))}
                    </div>
                  </CollapsibleContent>
                </Collapsible>
              ))}
            </div>
          </CollapsibleContent>
        </Collapsible>
      </div>

      <AlertDialog open={showDeleteAlert} onOpenChange={setShowDeleteAlert}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Connection</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{connection.name}"? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
