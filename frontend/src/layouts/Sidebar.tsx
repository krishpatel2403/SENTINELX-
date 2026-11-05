import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Shield,
  Upload,
  Settings,
  AlertTriangle,
  Puzzle,
  Search,
  Users,
  FileText,
  MapPin,
  LogOut,
} from "lucide-react";
import { useAuth } from "../hooks/useAuth";

type LucideIcon = React.ComponentType<
  React.ComponentProps<typeof LayoutDashboard> & { className?: string }
>;

const ICONS: Record<string, LucideIcon> = {
  Dashboard: LayoutDashboard,
  Events: Shield,
  Ingestion: Upload,
  Rules: Settings,
  Alerts: AlertTriangle,
  Incidents: Puzzle,
  Intelligence: Search,
  Mitre: MapPin,
  Reports: FileText,
  Users: Users,
  Settings: Settings,
};

const MENU = [
  { path: "/dashboard", label: "Dashboard", key: "Dashboard" },
  { path: "/events", label: "Security Events", key: "Events" },
  { path: "/ingestion", label: "Log Ingestion", key: "Ingestion" },
  { path: "/rules", label: "Detection Rules", key: "Rules" },
  { path: "/alerts", label: "Alert Management", key: "Alerts" },
  { path: "/incidents", label: "Incident Response", key: "Incidents" },
  { path: "/intelligence", label: "Threat Intel", key: "Intelligence" },
  { path: "/mitre", label: "MITRE ATT&CK", key: "Mitre" },
  { path: "/reports", label: "Reports", key: "Reports" },
  { path: "/users", label: "User Management", key: "Users" },
  { path: "/settings", label: "Settings", key: "Settings" },
];

export function Sidebar() {
  const { user, logout, isAuthenticated } = useAuth();

  return (
    <aside className="fixed inset-y-0 left-0 z-50 w-64 border-r border-slate-800 bg-sentinel-navy/60 backdrop-blur">
      <div className="flex items-center gap-2 px-5 py-6">
        <div className="w-8 h-8 rounded bg-blue-600 flex items-center justify-center">
          <span className="text-white font-bold text-xs">S</span>
        </div>
        <span className="font-bold text-xl tracking-tight text-slate-100">
          SENTINELX
        </span>
      </div>
      <nav className="mt-4 px-3 space-y-1">
        {MENU.map((item) => {
          const Icon = ICONS[item.key];
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }: { isActive: boolean }) =>
                "sidebar-link " + (isActive ? "active" : "")
              }
              end={item.path === "/"}
            >
              <Icon size={18} className="w-5" />
              {item.label}
            </NavLink>
          );
        })}
      </nav>
      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-800">
        <div className="px-3 py-2 text-xs text-slate-500 truncate">
          {user?.username} ({user?.role})
        </div>
        <button
          onClick={logout}
          className="w-full btn btn-danger mt-2"
          disabled={!isAuthenticated}
        >
          <LogOut size={16} className="mr-2" /> Sign out
        </button>
      </div>
    </aside>
  );
}

export function TopBar() {
  return (
    <header className="sticky top-0 z-40 flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-sentinel-deep/80 backdrop-blur">
      <h1 className="text-lg font-semibold text-slate-100">Security Operations</h1>
      <div className="flex items-center gap-3">
        <input
          type="text"
          placeholder="Search events, alerts, incidents…"
          className="input w-64"
        />
      </div>
    </header>
  );
}
