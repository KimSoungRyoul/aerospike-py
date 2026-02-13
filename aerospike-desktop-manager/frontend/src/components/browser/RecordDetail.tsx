import type { RecordResponse } from "@/api/types";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { JsonViewer } from "@/components/common/JsonViewer";

interface Props {
  record: RecordResponse;
  onClose: () => void;
}

export function RecordDetail({ record, onClose }: Props) {
  return (
    <Dialog open onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Record Detail</DialogTitle>
        </DialogHeader>
        <Tabs defaultValue="bins" className="w-full">
          <TabsList className="w-full">
            <TabsTrigger value="key" className="flex-1">Key</TabsTrigger>
            <TabsTrigger value="metadata" className="flex-1">Metadata</TabsTrigger>
            <TabsTrigger value="bins" className="flex-1">Bins</TabsTrigger>
          </TabsList>
          <TabsContent value="key">
            <ScrollArea className="max-h-[60vh]">
              <pre className="rounded-md bg-muted p-3 text-xs">
                {record.key ? JSON.stringify(record.key, null, 2) : "null"}
              </pre>
            </ScrollArea>
          </TabsContent>
          <TabsContent value="metadata">
            <ScrollArea className="max-h-[60vh]">
              <pre className="rounded-md bg-muted p-3 text-xs">
                {record.meta ? JSON.stringify(record.meta, null, 2) : "null"}
              </pre>
            </ScrollArea>
          </TabsContent>
          <TabsContent value="bins">
            <ScrollArea className="max-h-[60vh]">
              {record.bins ? (
                <JsonViewer data={record.bins} />
              ) : (
                <pre className="rounded-md bg-muted p-3 text-xs">null</pre>
              )}
            </ScrollArea>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
