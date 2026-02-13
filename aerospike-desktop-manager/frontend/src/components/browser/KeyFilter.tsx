import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search } from "lucide-react";

interface Props {
  value: string;
  onChange: (value: string) => void;
  onSearch: () => void;
}

export function KeyFilter({ value, onChange, onSearch }: Props) {
  return (
    <div className="flex gap-2">
      <Input
        placeholder="Filter by primary key..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && onSearch()}
        className="w-64"
      />
      <Button variant="outline" size="icon" onClick={onSearch}>
        <Search className="h-4 w-4" />
      </Button>
    </div>
  );
}
