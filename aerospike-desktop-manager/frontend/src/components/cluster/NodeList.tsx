import type { NodeInfo } from "@/api/types";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface Props {
  nodes: NodeInfo[];
}

export function NodeList({ nodes }: Props) {
  return (
    <div className="space-y-3">
      {nodes.map((node) => (
        <Card key={node.name} className="transition-all duration-150 hover:border-foreground/20">
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="h-3 w-3 rounded-full bg-green-500" />
                <span className="font-mono font-medium">{node.name}</span>
              </div>
              <Badge variant="outline">{node.edition}</Badge>
            </div>
            <div className="mt-2 flex gap-4 text-sm text-muted-foreground">
              <span>Build: {node.build}</span>
              <span>Namespaces: {node.namespaces.join(", ")}</span>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
