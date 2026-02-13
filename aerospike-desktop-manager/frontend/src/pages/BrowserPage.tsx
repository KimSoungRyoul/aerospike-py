import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useBrowserStore } from "@/stores/browserStore";
import { formatApiError } from "@/api/client";
import { RecordTable } from "@/components/browser/RecordTable";
import { RecordDetail } from "@/components/browser/RecordDetail";
import { BinEditor } from "@/components/browser/BinEditor";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Plus, ChevronLeft, ChevronRight } from "lucide-react";
import { EmptyState } from "@/components/common/EmptyState";
import { TableSkeleton } from "@/components/common/TableSkeleton";
import { Database } from "lucide-react";
import * as recordsApi from "@/api/records";
import type { RecordResponse } from "@/api/types";
import { toast } from "sonner";

const PAGE_SIZES = ["25", "50", "100"];

export function BrowserPage() {
  const { connId, ns, set } = useParams<{
    connId: string;
    ns?: string;
    set?: string;
  }>();
  const {
    browseResult,
    page,
    pageSize,
    setPage,
    fetchRecords,
    loading,
    error: storeError,
  } = useBrowserStore();

  const [selectedRecord, setSelectedRecord] = useState<RecordResponse | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  useEffect(() => {
    if (connId && ns && set) {
      fetchRecords(connId, ns, set);
    }
  }, [connId, ns, set, page, fetchRecords]);

  if (!ns || !set) {
    return (
      <EmptyState
        icon={Database}
        title="Select a Set"
        description="Choose a namespace and set from the sidebar to browse records."
      />
    );
  }

  const error = actionError || storeError;

  const handleDelete = async (record: RecordResponse) => {
    if (!connId || !record.key) return;
    setActionError(null);
    try {
      const pk = String(record.key[2]);
      await recordsApi.deleteRecord(connId, ns, set, pk);
      toast.success("Record deleted");
      fetchRecords(connId, ns, set);
    } catch (e) {
      const msg = formatApiError(e);
      setActionError(msg);
      toast.error("Delete failed", { description: msg });
    }
  };

  const handleCreate = async (bins: Record<string, unknown>) => {
    if (!connId) return;
    setActionError(null);
    try {
      const pk = `key_${Date.now()}`;
      await recordsApi.createRecord(connId, ns, set, pk, bins);
      setShowCreate(false);
      toast.success("Record created");
      fetchRecords(connId, ns, set);
    } catch (e) {
      const msg = formatApiError(e);
      setActionError(msg);
      toast.error("Create failed", { description: msg });
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold tracking-tight">
          {ns} / {set}
          {browseResult && (
            <span className="ml-2 text-sm font-normal text-muted-foreground">
              ({browseResult.total_scanned} records)
            </span>
          )}
        </h2>
        <Button size="sm" onClick={() => setShowCreate(true)}>
          <Plus className="mr-1 h-4 w-4" /> New Record
        </Button>
      </div>

      {error && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive">
          {error}
        </div>
      )}

      <Dialog open={showCreate} onOpenChange={setShowCreate}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create Record</DialogTitle>
          </DialogHeader>
          <BinEditor
            onSave={handleCreate}
            onCancel={() => setShowCreate(false)}
          />
        </DialogContent>
      </Dialog>

      {loading ? (
        <TableSkeleton columns={5} rows={8} />
      ) : browseResult ? (
        <>
          <RecordTable
            records={browseResult.records}
            onView={setSelectedRecord}
            onDelete={handleDelete}
          />

          {/* Pagination */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">
                Page {browseResult.page}
              </span>
              <Select
                value={String(pageSize)}
                onValueChange={(v) => {
                  useBrowserStore.setState({ pageSize: Number(v), page: 1 });
                  if (connId) fetchRecords(connId, ns, set);
                }}
              >
                <SelectTrigger className="h-8 w-[80px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {PAGE_SIZES.map((s) => (
                    <SelectItem key={s} value={s}>
                      {s} / page
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                disabled={page <= 1}
                onClick={() => setPage(page - 1)}
              >
                <ChevronLeft className="h-4 w-4" /> Prev
              </Button>
              <Button
                variant="outline"
                size="sm"
                disabled={!browseResult.has_more}
                onClick={() => setPage(page + 1)}
              >
                Next <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </>
      ) : null}

      {selectedRecord && (
        <RecordDetail
          record={selectedRecord}
          onClose={() => setSelectedRecord(null)}
        />
      )}
    </div>
  );
}
