import { useState, useRef, useEffect, useCallback } from "react";
import { formatApiError } from "@/api/client";
import { executeTerminalCommand } from "@/api/metrics";

export interface HistoryEntry {
  id: number;
  command: string;
  result: string;
  isError: boolean;
  timestamp: number;
}

let entryCounter = 0;

export function useTerminal(connId: string | undefined) {
  const [command, setCommand] = useState("");
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [cmdHistory, setCmdHistory] = useState<string[]>([]);
  const [historyIdx, setHistoryIdx] = useState(-1);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history]);

  const execute = useCallback(async () => {
    if (!command.trim() || !connId || loading) return;
    setLoading(true);
    setCmdHistory((h) => [...h, command]);
    setHistoryIdx(-1);
    try {
      const result = await executeTerminalCommand(connId, command);
      const formatted = JSON.stringify(result.parsed, null, 2);
      setHistory((h) => [
        ...h,
        { id: ++entryCounter, command, result: formatted, isError: false, timestamp: Date.now() },
      ]);
    } catch (e) {
      setHistory((h) => [
        ...h,
        { id: ++entryCounter, command, result: formatApiError(e), isError: true, timestamp: Date.now() },
      ]);
    } finally {
      setCommand("");
      setLoading(false);
    }
  }, [command, connId, loading]);

  const clear = useCallback(() => setHistory([]), []);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
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
    },
    [execute, cmdHistory, historyIdx]
  );

  return {
    command,
    setCommand,
    history,
    loading,
    bottomRef,
    execute,
    clear,
    handleKeyDown,
  };
}
