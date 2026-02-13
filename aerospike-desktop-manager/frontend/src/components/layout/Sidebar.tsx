import { useEffect, useState, useMemo } from "react";
import { useConnectionStore } from "@/stores/connectionStore";
import { ConnectionTree } from "@/components/connection/ConnectionTree";
import { ConnectionDialog } from "@/components/connection/ConnectionDialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Plus, Search } from "lucide-react";

export function Sidebar() {
  const { connections, fetchConnections } = useConnectionStore();
  const [showDialog, setShowDialog] = useState(false);
  const [search, setSearch] = useState("");

  useEffect(() => {
    fetchConnections();
  }, [fetchConnections]);

  const filtered = useMemo(
    () =>
      connections.filter((c) =>
        c.name.toLowerCase().includes(search.toLowerCase())
      ),
    [connections, search]
  );

  return (
    <div className="flex h-full flex-col">
      <div className="p-2">
        <div className="relative">
          <Search className="absolute left-2 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Filter connections..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="h-8 pl-8 text-xs"
          />
        </div>
      </div>
      <div className="flex items-center justify-between px-3 py-1">
        <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
          Connections
        </span>
        <Badge variant="secondary" className="h-5 px-1.5 text-[10px]">
          {connections.length}
        </Badge>
      </div>
      <ScrollArea className="flex-1 px-2">
        {filtered.map((conn) => (
          <ConnectionTree key={conn.id} connection={conn} />
        ))}
        {filtered.length === 0 && connections.length > 0 && (
          <div className="p-4 text-center text-xs text-muted-foreground">
            No matching connections
          </div>
        )}
        {connections.length === 0 && (
          <div className="p-4 text-center text-xs text-muted-foreground">
            No connections yet
          </div>
        )}
      </ScrollArea>
      <div className="border-t p-2">
        <Button
          variant="outline"
          size="sm"
          className="w-full"
          onClick={() => setShowDialog(true)}
        >
          <Plus className="mr-1 h-4 w-4" /> New Connection
        </Button>
      </div>
      <ConnectionDialog open={showDialog} onOpenChange={setShowDialog} />
    </div>
  );
}
