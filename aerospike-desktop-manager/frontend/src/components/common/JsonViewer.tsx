import { useState } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { Copy, Check } from "lucide-react";

interface Props {
  data: unknown;
}

export function JsonViewer({ data }: Props) {
  const [copied, setCopied] = useState(false);
  const text = JSON.stringify(data, null, 2);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative mt-1 rounded-md border bg-muted/50">
      <Button
        variant="ghost"
        size="icon"
        className="absolute right-2 top-2 h-7 w-7"
        onClick={handleCopy}
        aria-label="Copy JSON"
      >
        {copied ? (
          <Check className="h-3.5 w-3.5 text-green-500" />
        ) : (
          <Copy className="h-3.5 w-3.5" />
        )}
      </Button>
      <ScrollArea className="max-h-96">
        <pre className="p-3 text-xs">
          {renderJson(data)}
        </pre>
      </ScrollArea>
    </div>
  );
}

function renderJson(data: unknown, indent: number = 0): React.ReactNode {
  const pad = "  ".repeat(indent);
  if (data === null) return <span className="text-orange-500">null</span>;
  if (typeof data === "boolean") return <span className="text-orange-500">{String(data)}</span>;
  if (typeof data === "number") return <span className="text-blue-500">{data}</span>;
  if (typeof data === "string") return <span className="text-green-600 dark:text-green-400">"{data}"</span>;

  if (Array.isArray(data)) {
    if (data.length === 0) return "[]";
    return (
      <>
        {"[\n"}
        {data.map((item, i) => (
          <span key={i}>
            {pad}{"  "}{renderJson(item, indent + 1)}
            {i < data.length - 1 ? ",\n" : "\n"}
          </span>
        ))}
        {pad}{"]"}
      </>
    );
  }

  if (typeof data === "object") {
    const entries = Object.entries(data as Record<string, unknown>);
    if (entries.length === 0) return "{}";
    return (
      <>
        {"{\n"}
        {entries.map(([key, val], i) => (
          <span key={key}>
            {pad}{"  "}<span className="text-purple-500 dark:text-purple-400">"{key}"</span>{": "}{renderJson(val, indent + 1)}
            {i < entries.length - 1 ? ",\n" : "\n"}
          </span>
        ))}
        {pad}{"}"}
      </>
    );
  }

  return String(data);
}
