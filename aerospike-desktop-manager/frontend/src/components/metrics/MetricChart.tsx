import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface MetricSnapshot {
  timestamp: number;
  server: Record<string, string>;
  namespaces: Record<string, Record<string, string>>;
}

interface Props {
  title: string;
  history: MetricSnapshot[];
  keys: string[];
  labels: string[];
  colors: string[];
}

export function MetricChart({ title, history, keys, labels, colors }: Props) {
  const data = history.map((snap) => {
    const point: Record<string, number | string> = {
      time: new Date(snap.timestamp).toLocaleTimeString(),
    };
    keys.forEach((key, i) => {
      point[labels[i]] = Number(snap.server[key] || 0);
    });
    return point;
  });

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis dataKey="time" tick={{ fontSize: 10 }} />
            <YAxis tick={{ fontSize: 10 }} />
            <Tooltip />
            <Legend />
            {labels.map((label, i) => (
              <Line
                key={label}
                type="monotone"
                dataKey={label}
                stroke={colors[i]}
                strokeWidth={2}
                dot={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
