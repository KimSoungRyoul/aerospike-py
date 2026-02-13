import { useState, useRef, useEffect } from "react";
import { useParams } from "react-router-dom";
import { formatApiError } from "@/api/client";
import { executeTerminalCommand } from "@/api/metrics";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Send, Eraser } from "lucide-react";
import { EmptyState } from "@/components/common/EmptyState";
import { Terminal } from "lucide-react";

interface HistoryEntry {
  command: string;
  result: string;
  isError: boolean;
  timestamp: number;
}

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
  const [command, setCommand] = useState("");
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [cmdHistory, setCmdHistory] = useState<string[]>([]);
  const [historyIdx, setHistoryIdx] = useState(-1);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history]);

  if (!connId) {
    return (
      <EmptyState
        icon={Terminal}
        title="No Connection Selected"
        description="Select a connection to use the info terminal."
      />
    );
  }

  const execute = async () => {
    if (!command.trim() || loading) return;
    setLoading(true);
    setCmdHistory((h) => [...h, command]);
    setHistoryIdx(-1);
    try {
      const result = await executeTerminalCommand(connId, command);
      const formatted = JSON.stringify(result.parsed, null, 2);
      setHistory((h) => [
        ...h,
        { command, result: formatted, isError: false, timestamp: Date.now() },
      ]);
    } catch (e) {
      setHistory((h) => [
        ...h,
        { command, result: formatApiError(e), isError: true, timestamp: Date.now() },
      ]);
    } finally {
      setCommand("");
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      execute();
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      if (cmdHistory.length === 0) return;
      const newIdx = historyIdx < cmdHistory.length - 1 ? historyIdx + 1 : historyIdx;
      setHistoryIdx(newIdx);
      setCommand(cmdHistory[cmdHistory.length - 1 - newIdx]);
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      if (historyIdx <= 0) {
        setHistoryIdx(-1);
        setCommand("");
      } else {
        const newIdx = historyIdx - 1;
        setHistoryIdx(newIdx);
        setCommand(cmdHistory[cmdHistory.length - 1 - newIdx]);
      }
    }
  };

  return (
    <div className="flex h-full flex-col space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold tracking-tight">Info Terminal</h1>
        <Button
          variant="outline"
          size="sm"
          onClick={() => setHistory([])}
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
                <div key={entry.timestamp}>
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
