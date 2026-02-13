import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import type { ClusterOverview, NamespaceStats } from "@/api/types";
import { formatApiError } from "@/api/client";
import * as clusterApi from "@/api/cluster";
import { ClusterOverviewCard } from "@/components/cluster/ClusterOverview";
import { NodeList } from "@/components/cluster/NodeList";
import { NamespaceView } from "@/components/cluster/NamespaceView";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { PageSkeleton } from "@/components/common/PageSkeleton";
import { ErrorState } from "@/components/common/ErrorState";

export function ClusterPage() {
  const { connId } = useParams<{ connId: string }>();
  const [overview, setOverview] = useState<ClusterOverview | null>(null);
  const [nsDetails, setNsDetails] = useState<NamespaceStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    if (!connId) return;
    setLoading(true);
    setError(null);
    try {
      const ov = await clusterApi.getClusterOverview(connId);
      setOverview(ov);
      const details = await Promise.all(
        ov.namespaces.map((ns) => clusterApi.getNamespaceDetail(connId, ns))
      );
      setNsDetails(details);
    } catch (e) {
      setError(formatApiError(e));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [connId]);

  if (loading) return <PageSkeleton />;
  if (error) return <ErrorState message={error} onRetry={fetchData} />;
  if (!overview) return null;

  return (
    <div className="space-y-6">
      <h1 className="text-lg font-semibold tracking-tight">Cluster Overview</h1>
      <ClusterOverviewCard overview={overview} />
      <Tabs defaultValue="nodes">
        <TabsList>
          <TabsTrigger value="nodes">Nodes</TabsTrigger>
          <TabsTrigger value="namespaces">Namespaces</TabsTrigger>
        </TabsList>
        <TabsContent value="nodes" className="space-y-4 pt-4">
          <NodeList nodes={overview.nodes} />
        </TabsContent>
        <TabsContent value="namespaces" className="space-y-4 pt-4">
          {nsDetails.map((ns) => (
            <NamespaceView key={ns.name} stats={ns} />
          ))}
        </TabsContent>
      </Tabs>
    </div>
  );
}
