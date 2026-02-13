import { useEffect } from "react";
import { useMetricsStore } from "@/stores/metricsStore";
import { MetricChart } from "./MetricChart";
import { OperationStats } from "./OperationStats";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatBytes, formatNumber, formatPercent } from "@/lib/formatters";

interface Props {
  connId: string;
}

export function MetricsDashboard({ connId }: Props) {
  const { history, connected, connect, disconnect } = useMetricsStore();

  useEffect(() => {
    connect(connId);
    return () => disconnect();
  }, [connId, connect, disconnect]);

  const latest = history[history.length - 1];

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Badge variant={connected ? "default" : "secondary"}>
          {connected ? "Live" : "Disconnected"}
        </Badge>
        <span className="text-sm text-muted-foreground">
          {history.length} data points
        </span>
      </div>

      {latest && (
        <>
          <OperationStats stats={latest.server} />

          <div className="grid gap-4 md:grid-cols-2">
            <MetricChart
              title="Read/Write TPS"
              history={history}
              keys={["stat_read_reqs", "stat_write_reqs"]}
              labels={["Reads", "Writes"]}
              colors={["hsl(var(--chart-1))", "hsl(var(--chart-2))"]}
            />
            <MetricChart
              title="Client Connections"
              history={history}
              keys={["client_connections"]}
              labels={["Connections"]}
              colors={["hsl(var(--chart-4))"]}
            />
          </div>

          {Object.entries(latest.namespaces).map(([ns, nsStats]) => (
            <Card key={ns}>
              <CardHeader>
                <CardTitle className="text-base">{ns}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-2 text-sm sm:grid-cols-3">
                  <div>
                    <span className="text-muted-foreground">Objects: </span>
                    <span className="font-medium">
                      {nsStats.objects ? formatNumber(Number(nsStats.objects)) : "N/A"}
                    </span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Memory Used: </span>
                    <span className="font-medium">
                      {nsStats.memory_used_bytes ? formatBytes(Number(nsStats.memory_used_bytes)) : "N/A"}
                    </span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Memory Free: </span>
                    <span className="font-medium">
                      {nsStats.memory_free_pct ? formatPercent(Number(nsStats.memory_free_pct)) : "N/A"}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </>
      )}
    </div>
  );
}
