import type { NamespaceStats } from "@/api/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { formatBytes, formatNumber, formatPercent } from "@/lib/formatters";

interface Props {
  stats: NamespaceStats;
}

export function NamespaceView({ stats }: Props) {
  const memoryUsedPct = stats.memory_total_bytes > 0
    ? (stats.memory_used_bytes / stats.memory_total_bytes) * 100
    : 0;
  const deviceUsedPct = stats.device_total_bytes > 0
    ? (stats.device_used_bytes / stats.device_total_bytes) * 100
    : 0;

  return (
    <Card className="transition-all duration-150 hover:border-foreground/20">
      <CardHeader>
        <CardTitle>{stats.name}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard label="Objects" value={formatNumber(stats.objects)} />
          <div className="space-y-2 rounded-md border p-3">
            <div className="text-xs text-muted-foreground">Memory Used</div>
            <div className="text-lg font-bold">
              {formatBytes(stats.memory_used_bytes)}
              <span className="text-sm font-normal text-muted-foreground">
                {" "}/ {formatBytes(stats.memory_total_bytes)}
              </span>
            </div>
            <Progress value={memoryUsedPct} className="h-1.5" />
          </div>
          <StatCard
            label="Memory Free"
            value={formatPercent(stats.memory_free_pct)}
          />
          <div className="space-y-2 rounded-md border p-3">
            <div className="text-xs text-muted-foreground">Device Used</div>
            <div className="text-lg font-bold">
              {formatBytes(stats.device_used_bytes)}
              <span className="text-sm font-normal text-muted-foreground">
                {" "}/ {formatBytes(stats.device_total_bytes)}
              </span>
            </div>
            <Progress value={deviceUsedPct} className="h-1.5" />
          </div>
          <StatCard label="Replication Factor" value={String(stats.replication_factor)} />
          <StatCard
            label="Stop Writes"
            value={stats.stop_writes ? "YES" : "No"}
            alert={stats.stop_writes}
          />
          <StatCard
            label="HW Disk %"
            value={formatPercent(stats.high_water_disk_pct)}
          />
          <StatCard
            label="HW Memory %"
            value={formatPercent(stats.high_water_memory_pct)}
          />
        </div>
      </CardContent>
    </Card>
  );
}

function StatCard({
  label,
  value,
  alert,
}: {
  label: string;
  value: string;
  alert?: boolean;
}) {
  return (
    <div className="rounded-md border p-3">
      <div className="text-xs text-muted-foreground">{label}</div>
      <div className={`mt-1 text-lg font-bold ${alert ? "text-destructive" : ""}`}>
        {value}
      </div>
    </div>
  );
}
