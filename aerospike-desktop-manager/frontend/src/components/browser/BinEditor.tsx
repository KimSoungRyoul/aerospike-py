import { useState, useId } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { X, Plus } from "lucide-react";

interface Props {
  initialBins?: Record<string, unknown>;
  onSave: (bins: Record<string, unknown>) => void;
  onCancel: () => void;
}

export function BinEditor({ initialBins = {}, onSave, onCancel }: Props) {
  const baseId = useId();
  const [entries, setEntries] = useState<{ id: string; name: string; value: string }[]>(
    Object.entries(initialBins).map(([name, value], i) => ({
      id: `${baseId}-init-${i}`,
      name,
      value: typeof value === "object" ? JSON.stringify(value) : String(value),
    }))
  );
  const [nextId, setNextId] = useState(0);

  const addEntry = () => {
    setEntries([...entries, { id: `${baseId}-new-${nextId}`, name: "", value: "" }]);
    setNextId(nextId + 1);
  };

  const removeEntry = (id: string) =>
    setEntries(entries.filter((e) => e.id !== id));

  const updateEntry = (
    id: string,
    field: "name" | "value",
    val: string
  ) => {
    setEntries(entries.map((e) => (e.id === id ? { ...e, [field]: val } : e)));
  };

  const handleSave = () => {
    const bins: Record<string, unknown> = {};
    for (const { name, value } of entries) {
      if (!name) continue;
      // Try to parse as JSON, fallback to string
      try {
        bins[name] = JSON.parse(value);
      } catch {
        // Try number
        const num = Number(value);
        bins[name] = isNaN(num) ? value : num;
      }
    }
    onSave(bins);
  };

  return (
    <div className="space-y-3">
      {entries.map((entry) => (
        <div key={entry.id} className="flex gap-2">
          <Input
            placeholder="Bin name"
            value={entry.name}
            onChange={(e) => updateEntry(entry.id, "name", e.target.value)}
            className="w-32"
          />
          <Input
            placeholder="Value"
            value={entry.value}
            onChange={(e) => updateEntry(entry.id, "value", e.target.value)}
            className="flex-1"
          />
          <Button
            variant="ghost"
            size="icon"
            className="h-10 w-10"
            onClick={() => removeEntry(entry.id)}
            aria-label={`Remove bin ${entry.name || "entry"}`}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      ))}

      <Button variant="outline" size="sm" onClick={addEntry}>
        <Plus className="mr-1 h-4 w-4" /> Add Bin
      </Button>

      <div className="flex gap-2">
        <Button onClick={handleSave}>Save</Button>
        <Button variant="outline" onClick={onCancel}>
          Cancel
        </Button>
      </div>
    </div>
  );
}
