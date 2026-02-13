import { useParams } from "react-router-dom";
import { useTerminal } from "@/hooks/useTerminal";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Send, Eraser, Terminal } from "lucide-react";
import { EmptyState } from "@/components/common/EmptyState";

const EXAMPLE_COMMANDS = [
  "namespaces",
  "node",
  "build",
  "edition",
  "statistics",
  "sets/test",
  "bins/test",
  "sindex/test",
  "get-config:context=namespace;id=test",
];

export function TerminalPage() {
  const { connId } = useParams<{ connId: string }>();
  const { command, setCommand, history, loading, bottomRef, execute, clear, handleKeyDown } =
    useTerminal(connId);

  if (!connId) {
    return (
      <EmptyState
        icon={Terminal}
        title="No Connection Selected"
        description="Select a connection to use the info terminal."
      />
    );
  }

  return (
    <div className="flex h-full flex-col space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold tracking-tight">Info Terminal</h1>
        <Button
          variant="outline"
          size="sm"
          onClick={clear}
          disabled={history.length === 0}
        >
          <Eraser className="mr-1 h-4 w-4" /> Clear
        </Button>
      </div>

      <div className="flex flex-wrap gap-1">
        {EXAMPLE_COMMANDS.map((cmd) => (
          <Badge
            key={cmd}
            variant="outline"
            className="cursor-pointer hover:bg-accent transition-colors"
            onClick={() => setCommand(cmd)}
          >
            {cmd}
          </Badge>
        ))}
      </div>

      <Card className="flex-1 min-h-[300px]">
        <CardContent className="h-full p-0">
          <ScrollArea className="h-full">
            <div className="p-4 font-mono text-xs">
              {history.map((entry, i) => (
                <div key={entry.id}>
                  {i > 0 && <Separator className="my-3" />}
                  <div className="text-blue-500">
                    <span className="text-muted-foreground">
                      [{new Date(entry.timestamp).toLocaleTimeString()}]
                    </span>{" "}
                    $ {entry.command}
                  </div>
                  <pre
                    className={`mt-1 whitespace-pre-wrap ${
                      entry.isError ? "text-destructive" : "text-foreground"
                    }`}
                  >
                    {entry.result}
                  </pre>
                </div>
              ))}
              {history.length === 0 && (
                <div className="text-muted-foreground">
                  Enter an Aerospike info command above. Examples: "namespaces",
                  "node", "statistics"
                </div>
              )}
              <div ref={bottomRef} />
            </div>
          </ScrollArea>
        </CardContent>
      </Card>

      <div className="flex gap-2">
        <Input
          placeholder="Enter info command..."
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
          className="font-mono text-sm"
        />
        <Button onClick={execute} disabled={loading}>
          <Send className="mr-1 h-4 w-4" /> Execute
        </Button>
      </div>
    </div>
  );
}
