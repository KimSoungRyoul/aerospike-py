import { Card, CardContent } from "@/components/ui/card";
import { formatNumber } from "@/lib/formatters";

interface Props {
  stats: Record<string, string>;
}

const STAT_KEYS = [
  { key: "stat_read_reqs", label: "Read Requests" },
  { key: "stat_write_reqs", label: "Write Requests" },
  { key: "stat_read_success", label: "Read Success" },
  { key: "stat_write_success", label: "Write Success" },
  { key: "client_connections", label: "Client Connections" },
  { key: "uptime", label: "Uptime (s)" },
];

export function OperationStats({ stats }: Props) {
  return (
    <div className="grid gap-3 sm:grid-cols-3 lg:grid-cols-6">
      {STAT_KEYS.map(({ key, label }) => (
        <Card key={key}>
          <CardContent className="pt-4">
            <div className="text-xs text-muted-foreground">{label}</div>
            <div className="mt-1 text-lg font-bold">
              {stats[key] ? formatNumber(Number(stats[key])) : "N/A"}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
