import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useConnectionStore } from "@/stores/connectionStore";
import { EmptyState } from "@/components/common/EmptyState";
import { ConnectionStatusBadge } from "@/components/connection/ConnectionStatus";
import { ConnectionDialog } from "@/components/connection/ConnectionDialog";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
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
import { Button } from "@/components/ui/button";
import { Plug, MoreHorizontal, Eye, Server, Trash2 } from "lucide-react";
import { toast } from "sonner";

export function ConnectionsPage() {
  const { connections, removeConnection, setActiveConnection } = useConnectionStore();
  const navigate = useNavigate();
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);
  const [showDialog, setShowDialog] = useState(false);

  if (connections.length === 0) {
    return (
      <>
        <EmptyState
          icon={Plug}
          title="Welcome to Aerospike Desktop Manager"
          description="Connect to an Aerospike cluster to browse data, manage indexes, and monitor performance."
          action={{ label: "New Connection", onClick: () => setShowDialog(true) }}
        />
        <ConnectionDialog open={showDialog} onOpenChange={setShowDialog} />
      </>
    );
  }

  const handleDelete = async (id: string) => {
    const conn = connections.find((c) => c.id === id);
    await removeConnection(id);
    toast.success("Connection removed", { description: conn?.name ?? id });
    setDeleteTarget(null);
  };

  return (
    <div className="space-y-6">
      <h1 className="text-lg font-semibold tracking-tight">Connections</h1>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {connections.map((conn) => (
          <Card
            key={conn.id}
            className="group cursor-pointer transition-all duration-200 hover:border-foreground/25 hover:shadow-md"
            onClick={() => {
              setActiveConnection(conn.id);
              navigate(`/browser/${conn.id}`);
            }}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <div className="flex items-center gap-2">
                <div
                  className="h-3 w-3 rounded-full"
                  style={{ backgroundColor: conn.color }}
                />
                <span className="font-medium">{conn.name}</span>
                <ConnectionStatusBadge connected={conn.connected} />
              </div>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" onClick={(e) => e.stopPropagation()}>
                  <DropdownMenuItem
                    onClick={(e) => {
                      e.stopPropagation();
                      setActiveConnection(conn.id);
                      navigate(`/browser/${conn.id}`);
                    }}
                  >
                    <Eye className="mr-2 h-4 w-4" />
                    Open Browser
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onClick={(e) => {
                      e.stopPropagation();
                      setActiveConnection(conn.id);
                      navigate(`/cluster/${conn.id}`);
                    }}
                  >
                    <Server className="mr-2 h-4 w-4" />
                    View Cluster
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    className="text-destructive focus:text-destructive"
                    onClick={(e) => {
                      e.stopPropagation();
                      setDeleteTarget(conn.id);
                    }}
                  >
                    <Trash2 className="mr-2 h-4 w-4" />
                    Delete
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground space-y-1">
              {conn.cluster_name && (
                <div className="flex items-center gap-1.5">
                  <Server className="h-3.5 w-3.5" />
                  <span>{conn.cluster_name}</span>
                </div>
              )}
              <div className="flex items-center gap-3 text-xs">
                <span>{conn.node_count} {conn.node_count === 1 ? 'node' : 'nodes'}</span>
                <span className="text-muted-foreground/50">&middot;</span>
                <span>{conn.namespaces.length} {conn.namespaces.length === 1 ? 'ns' : 'namespaces'}</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <AlertDialog open={!!deleteTarget} onOpenChange={() => setDeleteTarget(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Connection</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this connection? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => deleteTarget && handleDelete(deleteTarget)}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
