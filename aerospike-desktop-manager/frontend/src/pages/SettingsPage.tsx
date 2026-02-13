import { useUIStore } from "@/stores/uiStore";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { Sun, Moon, Monitor } from "lucide-react";

export function SettingsPage() {
  const { theme, setTheme } = useUIStore();

  return (
    <div className="max-w-2xl space-y-6">
      <h1 className="text-lg font-semibold tracking-tight">Settings</h1>

      <Card>
        <CardHeader>
          <CardTitle>Appearance</CardTitle>
          <CardDescription>Choose how the application looks.</CardDescription>
        </CardHeader>
        <CardContent>
          <ToggleGroup
            type="single"
            value={theme}
            onValueChange={(v) => {
              if (v) setTheme(v as "light" | "dark" | "system");
            }}
          >
            <ToggleGroupItem value="light" aria-label="Light mode">
              <Sun className="mr-1 h-4 w-4" />
              Light
            </ToggleGroupItem>
            <ToggleGroupItem value="dark" aria-label="Dark mode">
              <Moon className="mr-1 h-4 w-4" />
              Dark
            </ToggleGroupItem>
            <ToggleGroupItem value="system" aria-label="System mode">
              <Monitor className="mr-1 h-4 w-4" />
              System
            </ToggleGroupItem>
          </ToggleGroup>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>About</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground space-y-1">
          <p>Aerospike Desktop Manager</p>
          <p>Built with aerospike-py, FastAPI, React, and shadcn/ui</p>
          <p>Aerospike Community Edition support (up to 8 nodes)</p>
        </CardContent>
      </Card>
    </div>
  );
}
