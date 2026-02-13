import { Routes, Route } from "react-router-dom";
import { ErrorBoundary } from "./components/common/ErrorBoundary";
import { AppLayout } from "./components/layout/AppLayout";
import { ConnectionsPage } from "./pages/ConnectionsPage";
import { BrowserPage } from "./pages/BrowserPage";
import { ClusterPage } from "./pages/ClusterPage";
import { MetricsPage } from "./pages/MetricsPage";
import { IndexesPage } from "./pages/IndexesPage";
import { UdfsPage } from "./pages/UdfsPage";
import { TerminalPage } from "./pages/TerminalPage";
import { SettingsPage } from "./pages/SettingsPage";

export default function App() {
  return (
    <ErrorBoundary>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<ConnectionsPage />} />
          <Route path="/browser/:connId" element={<BrowserPage />} />
          <Route path="/browser/:connId/:ns" element={<BrowserPage />} />
          <Route path="/browser/:connId/:ns/:set" element={<BrowserPage />} />
          <Route path="/cluster/:connId" element={<ClusterPage />} />
          <Route path="/metrics/:connId" element={<MetricsPage />} />
          <Route path="/indexes/:connId" element={<IndexesPage />} />
          <Route path="/udfs/:connId" element={<UdfsPage />} />
          <Route path="/terminal/:connId" element={<TerminalPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>
      </Routes>
    </ErrorBoundary>
  );
}
