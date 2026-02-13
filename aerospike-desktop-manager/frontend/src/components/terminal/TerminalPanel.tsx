import { useConnectionStore } from "@/stores/connectionStore";
import { useTerminal } from "@/hooks/useTerminal";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Send, Minimize2 } from "lucide-react";
import { useUIStore } from "@/stores/uiStore";

export function TerminalPanel() {
  const { activeConnectionId } = useConnectionStore();
  const { toggleTerminal } = useUIStore();
  const { command, setCommand, history, loading, bottomRef, execute, handleKeyDown } =
    useTerminal(activeConnectionId ?? undefined);

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
          onKeyDown={handleKeyDown}
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
