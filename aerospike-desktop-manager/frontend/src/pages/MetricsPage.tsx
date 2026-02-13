import { useParams } from "react-router-dom";
import { MetricsDashboard } from "@/components/metrics/MetricsDashboard";
import { EmptyState } from "@/components/common/EmptyState";
import { Activity } from "lucide-react";

export function MetricsPage() {
  const { connId } = useParams<{ connId: string }>();

  if (!connId) {
    return (
      <EmptyState
        icon={Activity}
        title="No Connection Selected"
        description="Select a connection to view real-time metrics."
      />
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-lg font-semibold tracking-tight">Metrics Dashboard</h1>
      <MetricsDashboard connId={connId} />
    </div>
  );
}
