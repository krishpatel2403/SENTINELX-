import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { AuthProvider } from "./hooks/useAuth";
import { AppProvider } from "./hooks/useApp";
import { MainLayout } from "./layouts/MainLayout";
import { Login } from "./pages/Login";
import { Dashboard } from "./pages/Dashboard";
import { SecurityEvents } from "./pages/SecurityEvents";
import { LogIngestion } from "./pages/LogIngestion";
import { DetectionRules } from "./pages/DetectionRules";
import { AlertManagement } from "./pages/AlertManagement";
import { IncidentManagement } from "./pages/IncidentManagement";
import { ThreatIntelligence } from "./pages/ThreatIntelligence";
import { MitreAttck } from "./pages/MitreAttck";
import { Reports } from "./pages/Reports";
import { UserManagement } from "./pages/UserManagement";
import { Settings } from "./pages/Settings";

function requireAuth(element: React.ReactElement) {
  return element;
}

const router = createBrowserRouter([
  {
    path: "/",
    element: <Login />,
  },
  {
    path: "/app",
    element: (
      <AuthProvider>
        <AppProvider>
          <MainLayout />
        </AppProvider>
      </AuthProvider>
    ),
    children: [
      { index: true, element: <Dashboard /> },
      { path: "dashboard", element: <Dashboard /> },
      { path: "events", element: <SecurityEvents /> },
      { path: "ingestion", element: <LogIngestion /> },
      { path: "rules", element: <DetectionRules /> },
      { path: "alerts", element: <AlertManagement /> },
      { path: "incidents", element: <IncidentManagement /> },
      { path: "intelligence", element: <ThreatIntelligence /> },
      { path: "mitre", element: <MitreAttck /> },
      { path: "reports", element: <Reports /> },
      { path: "users", element: <UserManagement /> },
      { path: "settings", element: <Settings /> },
    ],
  },
]);

export default function App() {
  return <RouterProvider router={router} />;
}
