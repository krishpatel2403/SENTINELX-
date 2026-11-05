import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";
import { dashboardApi } from "../services/api";
import { DashboardStats } from "../types";

const COLORS = ["#3b82f6", "#22d3ee", "#f59e0b", "#ef4444"];

export function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [eventsOverTime, setEventsOverTime] = useState<Array<{ date: string; count: number }>>(
    [],
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;
    Promise.all([dashboardApi.stats(), dashboardApi.eventsOverTime(7)])
      .then(([s, e]) => {
        if (!mounted) return;
        setStats(s);
        setEventsOverTime(e);
      })
      .catch((err) => {
        if (!mounted) return;
        setError(err.message || "Failed to load dashboard");
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, []);

  const severityData = [
    { name: "Critical", value: stats?.critical_alerts ?? 0, color: COLORS[3] },
    { name: "High", value: stats?.high_alerts ?? 0, color: COLORS[2] },
    { name: "Medium", value: stats?.medium_alerts ?? 0, color: COLORS[1] },
    { name: "Low", value: stats?.low_alerts ?? 0, color: COLORS[0] },
  ];

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse flex items-center gap-2 text-slate-500">
          <span className="w-4 h-4 rounded-full bg-slate-700"></span>
          Loading dashboard…
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="p-4 rounded bg-red-900/20 border border-red-900/30 text-red-400">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-100 mb-2">Dashboard</h2>
        <p className="text-slate-400 text-sm">
          Real-time security statistics from application data.
        </p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Events"
          value={stats?.total_events ?? 0}
          icon="📊"
        />
        <StatCard
          title="Critical Alerts"
          value={stats?.critical_alerts ?? 0}
          icon="🚨"
        />
        <StatCard
          title="High Alerts"
          value={stats?.high_alerts ?? 0}
          icon="⚠️"
        />
        <StatCard
          title="Medium Alerts"
          value={stats?.medium_alerts ?? 0}
          icon="ℹ️"
        />
        <StatCard
          title="Low Alerts"
          value={stats?.low_alerts ?? 0}
          icon="📋"
        />
        <StatCard
          title="Active Incidents"
          value={stats?.active_incidents ?? 0}
          icon="🧩"
        />
        <StatCard
          title="Resolved Incidents"
          value={stats?.resolved_incidents ?? 0}
          icon="✅"
        />
        <StatCard
          title="Auth Failures"
          value={stats?.auth_failures ?? 0}
          icon="🔐"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 card">
          <h3 className="mb-4 text-sm font-semibold text-slate-300 uppercase tracking-wider">
            Security Events Over Time
          </h3>
          <div className="h-64">
            <LineChart data={eventsOverTime}>
              <defs>
                <linearGradient id="colorEvents" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="date" tick={{ fontSize: 12, fill: "#94a3b8" }} />
              <YAxis tick={{ fontSize: 12, fill: "#94a3b8" }} />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="count"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={{ fill: "#3b82f6" }}
                fill="#3b82f6"
                fillOpacity={0.1}
              />
            </LineChart>
          </div>
        </div>

        <div className="card">
          <h3 className="mb-4 text-sm font-semibold text-slate-300 uppercase tracking-wider">
            Alert Severity Distribution
          </h3>
          <div className="h-64">
            <PieChart>
              <Pie
                data={severityData.filter((d) => d.value > 0)}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={90}
                fill="#888"
                label
              >
                {severityData.map((entry, i) => (
                  <Cell key={`cell-${i}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </div>
        </div>
      </div>

      <div className="card">
        <h3 className="mb-4 text-sm font-semibold text-slate-300 uppercase tracking-wider">
          Recent Activity Summary
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <ActivityItem
            label="Total Security Events"
            value={stats?.total_events ?? 0}
            subtitle="Ingested across all sources"
          />
          <ActivityItem
            label="Critical + High"
            value={
              (stats?.critical_alerts ?? 0) + (stats?.high_alerts ?? 0)
            }
            subtitle="Require immediate attention"
          />
          <ActivityItem
            label="Suspicious IPs"
            value={stats?.suspicious_ips ?? 0}
            subtitle="Unique sources flagged"
          />
        </div>
      </div>
    </div>
  );
}

function StatCard({
  title,
  value,
  icon,
}: {
  title: string;
  value: number;
  icon: string;
}) {
  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">
            {title}
          </p>
          <p className="text-3xl font-bold text-slate-100 mt-1">{value}</p>
        </div>
        <div className="w-10 h-10 rounded-lg flex items-center justify-center text-xs font-bold">
          {icon}
        </div>
      </div>
    </div>
  );
}

function ActivityItem({
  label,
  value,
  subtitle,
}: {
  label: string;
  value: number;
  subtitle: string;
}) {
  return (
    <div className="p-4 rounded-lg border border-slate-800 bg-sentinel-navy/30">
      <p className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-1">
        {label}
      </p>
      <p className="text-2xl font-bold text-slate-100">{value}</p>
      <p className="text-xs text-slate-500 mt-1">{subtitle}</p>
    </div>
  );
}
