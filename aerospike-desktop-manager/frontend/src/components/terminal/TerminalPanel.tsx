import { useState, useRef, useEffect } from "react";
import { useConnectionStore } from "@/stores/connectionStore";
import { formatApiError } from "@/api/client";
import { executeTerminalCommand } from "@/api/metrics";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Send, Minimize2 } from "lucide-react";
import { useUIStore } from "@/stores/uiStore";

interface HistoryEntry {
  id: number;
  command: string;
  result: string;
  isError: boolean;
}

let entryCounter = 0;

export function TerminalPanel() {
  const { activeConnectionId } = useConnectionStore();
  const { toggleTerminal } = useUIStore();
  const [command, setCommand] = useState("");
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history]);

  const execute = async () => {
    if (!command.trim() || !activeConnectionId) return;
    setLoading(true);
    try {
      const result = await executeTerminalCommand(activeConnectionId, command);
      const formatted = JSON.stringify(result.parsed, null, 2);
      setHistory((h) => [...h, { id: ++entryCounter, command, result: formatted, isError: false }]);
    } catch (e) {
      setHistory((h) => [
        ...h,
        { id: ++entryCounter, command, result: formatApiError(e), isError: true },
      ]);
    } finally {
      setCommand("");
      setLoading(false);
    }
  };

  return (
    <div className="flex h-64 flex-col">
      <div className="flex items-center justify-between px-4 py-1">
        <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Info Terminal</span>
        <Button variant="ghost" size="icon" className="h-6 w-6" onClick={toggleTerminal} aria-label="Minimize terminal">
          <Minimize2 className="h-3 w-3" />
        </Button>
      </div>
      <Separator />

      <ScrollArea className="flex-1">
        <div className="p-3 font-mono text-xs">
          {history.map((entry, i) => (
            <div key={entry.id}>
              {i > 0 && <Separator className="my-2" />}
              <div className="text-blue-500">$ {entry.command}</div>
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
              Enter an info command (e.g., "namespaces", "node", "statistics")
            </div>
          )}
          <div ref={bottomRef} />
        </div>
      </ScrollArea>

      <Separator />
      <div className="flex gap-2 p-2">
        <Input
          placeholder={
            activeConnectionId
              ? "Enter info command..."
              : "Connect to a cluster first"
          }
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && execute()}
          disabled={!activeConnectionId || loading}
          className="font-mono text-sm"
          aria-label="Terminal command"
        />
        <Button
          size="icon"
          onClick={execute}
          disabled={!activeConnectionId || loading}
          aria-label="Execute command"
        >
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
