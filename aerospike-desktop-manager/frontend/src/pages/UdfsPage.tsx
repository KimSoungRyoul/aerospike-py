import { useEffect, useState, useRef } from "react";
import { useParams } from "react-router-dom";
import type { UdfInfo } from "@/api/types";
import { formatApiError } from "@/api/client";
import * as udfsApi from "@/api/udfs";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
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
import { Trash2, Upload } from "lucide-react";
import { toast } from "sonner";

export function UdfsPage() {
  const { connId } = useParams<{ connId: string }>();
  const [udfs, setUdfs] = useState<UdfInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const fetchUdfs = async () => {
    if (!connId) return;
    setLoading(true);
    setError(null);
    try {
      const list = await udfsApi.listUdfs(connId);
      setUdfs(list);
    } catch (e) {
      setError(formatApiError(e));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUdfs();
  }, [connId]);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !connId) return;

    setUploading(true);
    setError(null);
    try {
      const content = await file.text();
      await udfsApi.uploadUdf(connId, file.name, content);
      toast.success("UDF uploaded", { description: file.name });
      await fetchUdfs();
    } catch (err) {
      const msg = formatApiError(err);
      setError(msg);
      toast.error("Upload failed", { description: msg });
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  const handleDelete = async (module: string) => {
    if (!connId) return;
    setError(null);
    try {
      await udfsApi.deleteUdf(connId, module);
      toast.success("UDF deleted", { description: module });
      await fetchUdfs();
    } catch (e) {
      const msg = formatApiError(e);
      setError(msg);
      toast.error("Delete failed", { description: msg });
    }
    setDeleteTarget(null);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold tracking-tight">UDF Modules</h1>
        <Button size="sm" onClick={() => fileRef.current?.click()} disabled={uploading}>
          <Upload className="mr-1 h-4 w-4" />
          {uploading ? "Uploading..." : "Upload UDF"}
        </Button>
        <input
          ref={fileRef}
          type="file"
          accept=".lua"
          className="hidden"
          onChange={handleUpload}
        />
      </div>

      {error && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive">
          {error}
        </div>
      )}

      {loading ? (
        <TableSkeleton columns={4} rows={3} />
      ) : udfs.length === 0 ? (
        <div className="py-8 text-center text-muted-foreground">
          No UDF modules registered
        </div>
      ) : (
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Filename</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Hash</TableHead>
                <TableHead className="w-12"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {udfs.map((udf) => (
                <TableRow key={udf.filename}>
                  <TableCell className="font-medium">{udf.filename}</TableCell>
                  <TableCell>
                    <Badge variant="secondary">{udf.type}</Badge>
                  </TableCell>
                  <TableCell className="max-w-[200px] truncate font-mono text-xs">
                    {udf.hash}
                  </TableCell>
                  <TableCell>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 text-destructive"
                      onClick={() => setDeleteTarget(udf.filename)}
                      aria-label={`Delete UDF ${udf.filename}`}
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

      <AlertDialog open={!!deleteTarget} onOpenChange={() => setDeleteTarget(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete UDF Module</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{deleteTarget}"? This action cannot be undone.
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
