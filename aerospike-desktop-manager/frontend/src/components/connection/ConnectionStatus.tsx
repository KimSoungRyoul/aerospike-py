import { Badge } from "@/components/ui/badge";

interface Props {
  connected: boolean;
}

export function ConnectionStatusBadge({ connected }: Props) {
  return (
    <Badge variant={connected ? "default" : "secondary"}>
      {connected ? "Connected" : "Disconnected"}
    </Badge>
  );
}
