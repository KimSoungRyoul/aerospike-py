import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import type { IndexInfo } from "@/api/types";
import { formatApiError } from "@/api/client";
import * as indexesApi from "@/api/indexes";
import * as clusterApi from "@/api/cluster";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
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
import { TableSkeleton } from "@/components/common/TableSkeleton";
import { Plus, Trash2 } from "lucide-react";
import { toast } from "sonner";

export function IndexesPage() {
  const { connId } = useParams<{ connId: string }>();
  const [namespaces, setNamespaces] = useState<string[]>([]);
  const [selectedNs, setSelectedNs] = useState<string>("");
  const [indexes, setIndexes] = useState<IndexInfo[]>([]);
  const [showCreate, setShowCreate] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    setName: "",
    binName: "",
    indexName: "",
    indexType: "numeric",
  });

  useEffect(() => {
    if (!connId) return;
    clusterApi.getNamespaces(connId).then((ns) => {
      setNamespaces(ns);
      if (ns.length > 0) setSelectedNs(ns[0]);
    }).catch((e) => setError(formatApiError(e)));
  }, [connId]);

  useEffect(() => {
    if (!connId || !selectedNs) return;
    setLoading(true);
    indexesApi.listIndexes(connId, selectedNs)
      .then(setIndexes)
      .catch((e) => setError(formatApiError(e)))
      .finally(() => setLoading(false));
  }, [connId, selectedNs]);

  const handleCreate = async () => {
    if (!connId || !selectedNs) return;
    setLoading(true);
    setError(null);
    try {
      await indexesApi.createIndex(
        connId,
        selectedNs,
        form.setName,
        form.binName,
        form.indexName,
        form.indexType
      );
      setShowCreate(false);
      toast.success("Index created", { description: form.indexName });
      const updated = await indexesApi.listIndexes(connId, selectedNs);
      setIndexes(updated);
    } catch (e) {
      const msg = formatApiError(e);
      setError(msg);
      toast.error("Failed to create index", { description: msg });
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (name: string) => {
    if (!connId || !selectedNs) return;
    setError(null);
    try {
      await indexesApi.deleteIndex(connId, selectedNs, name);
      toast.success("Index deleted", { description: name });
      const updated = await indexesApi.listIndexes(connId, selectedNs);
      setIndexes(updated);
    } catch (e) {
      const msg = formatApiError(e);
      setError(msg);
      toast.error("Failed to delete index", { description: msg });
    }
    setDeleteTarget(null);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold tracking-tight">Secondary Indexes</h1>
        <Button size="sm" onClick={() => setShowCreate(true)}>
          <Plus className="mr-1 h-4 w-4" /> Create Index
        </Button>
      </div>

      {error && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive">
          {error}
        </div>
      )}

      <div className="flex items-center gap-2">
        <span className="text-sm font-medium text-muted-foreground">Namespace:</span>
        <Select value={selectedNs} onValueChange={setSelectedNs}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Select namespace" />
          </SelectTrigger>
          <SelectContent>
            {namespaces.map((ns) => (
              <SelectItem key={ns} value={ns}>
                {ns}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {loading && indexes.length === 0 ? (
        <TableSkeleton columns={5} rows={3} />
      ) : indexes.length === 0 ? (
        <div className="py-8 text-center text-muted-foreground">No indexes found</div>
      ) : (
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Set</TableHead>
                <TableHead>Bin</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>State</TableHead>
                <TableHead className="w-12"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {indexes.map((idx) => (
                <TableRow key={idx.name}>
                  <TableCell className="font-medium">{idx.name}</TableCell>
                  <TableCell>{idx.set_name || "*"}</TableCell>
                  <TableCell>{idx.bin_name}</TableCell>
                  <TableCell>
                    <Badge variant="secondary">{idx.index_type}</Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant={idx.state === "RW" ? "default" : "secondary"}>
                      {idx.state}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 text-destructive"
                      onClick={() => setDeleteTarget(idx.name)}
                      aria-label={`Delete index ${idx.name}`}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      <Dialog open={showCreate} onOpenChange={setShowCreate}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create Index on {selectedNs}</DialogTitle>
          </DialogHeader>
          <div className="grid gap-4">
            <div className="space-y-2">
              <Label>Set Name</Label>
              <Input placeholder="Set name" value={form.setName} onChange={(e) => setForm({ ...form, setName: e.target.value })} />
            </div>
            <div className="space-y-2">
              <Label>Bin Name</Label>
              <Input placeholder="Bin name" value={form.binName} onChange={(e) => setForm({ ...form, binName: e.target.value })} />
            </div>
            <div className="space-y-2">
              <Label>Index Name</Label>
              <Input placeholder="Index name" value={form.indexName} onChange={(e) => setForm({ ...form, indexName: e.target.value })} />
            </div>
            <div className="space-y-2">
              <Label>Index Type</Label>
              <Select value={form.indexType} onValueChange={(v) => setForm({ ...form, indexType: v })}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="numeric">Numeric</SelectItem>
                  <SelectItem value="string">String</SelectItem>
                  <SelectItem value="geo2dsphere">Geo2DSphere</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCreate(false)}>Cancel</Button>
            <Button onClick={handleCreate} disabled={loading}>
              {loading ? "Creating..." : "Create"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <AlertDialog open={!!deleteTarget} onOpenChange={() => setDeleteTarget(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Index</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete the index "{deleteTarget}"? This action cannot be undone.
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
