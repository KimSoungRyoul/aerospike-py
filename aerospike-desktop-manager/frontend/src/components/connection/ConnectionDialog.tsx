import { useState } from "react";
import { useConnectionStore } from "@/stores/connectionStore";
import { formatApiError } from "@/api/client";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { CONNECTION_COLORS } from "@/lib/constants";
import { toast } from "sonner";

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function ConnectionDialog({ open, onOpenChange }: Props) {
  const { addConnection } = useConnectionStore();
  const [name, setName] = useState("My Cluster");
  const [host, setHost] = useState("127.0.0.1");
  const [port, setPort] = useState("3000");
  const [clusterName, setClusterName] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [color, setColor] = useState(CONNECTION_COLORS[0]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleConnect = async () => {
    setLoading(true);
    setError("");
    try {
      await addConnection({
        name,
        hosts: [[host, parseInt(port)]],
        cluster_name: clusterName || undefined,
        username: username || undefined,
        password: password || undefined,
        color,
      });
      toast.success("Connected", { description: `Successfully connected to ${name}` });
      onOpenChange(false);
    } catch (e) {
      setError(formatApiError(e));
      toast.error("Connection failed", { description: formatApiError(e) });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>New Connection</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="conn-name">Name</Label>
            <Input id="conn-name" value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <div className="flex gap-3">
            <div className="flex-1 space-y-2">
              <Label htmlFor="conn-host">Host</Label>
              <Input id="conn-host" value={host} onChange={(e) => setHost(e.target.value)} />
            </div>
            <div className="w-24 space-y-2">
              <Label htmlFor="conn-port">Port</Label>
              <Input id="conn-port" value={port} onChange={(e) => setPort(e.target.value)} />
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="conn-cluster">Cluster Name <span className="text-muted-foreground">(optional)</span></Label>
            <Input
              id="conn-cluster"
              value={clusterName}
              onChange={(e) => setClusterName(e.target.value)}
              placeholder="e.g. docker"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="conn-user">Username <span className="text-muted-foreground">(optional)</span></Label>
            <Input id="conn-user" value={username} onChange={(e) => setUsername(e.target.value)} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="conn-pass">Password <span className="text-muted-foreground">(optional)</span></Label>
            <Input
              id="conn-pass"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label>Color</Label>
            <div className="flex gap-1.5" role="radiogroup" aria-label="Connection color">
              {CONNECTION_COLORS.map((c) => (
                <button
                  key={c}
                  role="radio"
                  aria-checked={color === c}
                  aria-label={c}
                  className={`h-6 w-6 rounded-full border-2 transition-all ${
                    color === c ? "border-foreground scale-110" : "border-transparent hover:scale-105"
                  }`}
                  style={{ backgroundColor: c }}
                  onClick={() => setColor(c)}
                />
              ))}
            </div>
          </div>
          {error && <p className="text-sm text-destructive" role="alert">{error}</p>}
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleConnect} disabled={loading}>
            {loading ? "Connecting..." : "Connect"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
