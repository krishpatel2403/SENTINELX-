import { useEffect, useState } from "react";
import { alertsApi } from "../services/api";
import { Alert, AlertFilter } from "../types";

const STATUSES = ["new", "investigating", "escalated", "resolved", "false_positive"];
const SEVERITIES = ["critical", "high", "medium", "low"];

export function AlertManagement() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [filter, setFilter] = useState<AlertFilter>({ page: 1, page_size: 25 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = async () => {
    setLoading(true);
    try {
      const data = await alertsApi.list({ ...filter, page, page_size: pageSize });
      setAlerts(data.items);
      setTotal(data.total);
    } catch (err: any) {
      setError(err.message || "Failed to load alerts");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [page, pageSize, filter.status, filter.severity, filter.assigned_to, filter.search]);

  const statusColor = (status: string) => {
    switch (status) {
      case "new": return "badge-high";
      case "investigating": return "badge-medium";
      case "escalated": return "badge-critical";
      case "resolved": return "badge-low";
      case "false_positive": return "badge-unknown";
      default: return "badge-medium";
    }
  };

  const severityColor = (sev: string) => {
    switch (sev) {
      case "critical": return "badge-critical";
      case "high": return "badge-high";
      case "medium": return "badge-medium";
      case "low": return "badge-low";
      default: return "badge-unknown";
    }
  };

  const handleUpdate = async (alert: Alert, field: string, value: any) => {
    try {
      await alertsApi.update(alert.id, { [field]: value });
      await load();
    } catch (err: any) {
      setError(err.message || "Update failed");
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse flex items-center gap-2 text-slate-500">
          <span className="w-4 h-4 rounded-full bg-slate-700"></span>
          Loading alerts…
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-100">Alert Management</h2>
          <p className="text-slate-400 text-sm">
            Triage, assign, and resolve detection alerts.
          </p>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded bg-red-900/20 border border-red-900/30 text-red-400 text-sm">
          {error}
        </div>
      )}

      <div className="card overflow-x-auto">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5 gap-3 p-4">
          <FilterSelect
            label="Status"
            value={filter.status ?? ""}
            onChange={(v) => setFilter({ ...filter, status: v || undefined })}
            options={STATUSES}
          />
          <FilterSelect
            label="Severity"
            value={filter.severity ?? ""}
            onChange={(v) => setFilter({ ...filter, severity: v || undefined })}
            options={SEVERITIES}
          />
          <FilterInput
            label="Search"
            value={filter.search ?? ""}
            onChange={(e) => setFilter({ ...filter, search: e.target.value })}
          />
          <button
            onClick={() => setFilter({ page: 1, page_size: pageSize })}
            className="btn btn-outline"
          >
            Clear filters
          </button>
        </div>
      </div>

      <div className="overflow-x-auto card">
        <table className="data-table">
          <thead>
            <tr>
              <th>Alert ID</th>
              <th>Title</th>
              <th>Severity</th>
              <th>Status</th>
              <th>Assigned To</th>
              <th>Rule</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {alerts.length === 0 ? (
              <tr>
                <td colSpan={8} className="text-center py-8 text-slate-500">
                  No alerts found. Run detection evaluation to generate alerts.
                </td>
              </tr>
            ) : (
              alerts.map((alert) => (
                <tr key={alert.id} className="hover:bg-slate-800/30">
                  <td className="font-mono text-xs text-slate-400 truncate max-w-xs">
                    {alert.alert_id}
                  </td>
                  <td className="text-xs text-slate-200 truncate max-w-md">
                    {alert.title}
                  </td>
                  <td>
                    <span className={`badge ${severityColor(alert.severity)}`}>
                      {alert.severity}
                    </span>
                  </td>
                  <td>
                    <select
                      value={alert.status}
                      onChange={(e) => handleUpdate(alert, "status", e.target.value)}
                      className="input h-8 text-xs bg-transparent border-0 focus:ring-0"
                    >
                      {STATUSES.map((s) => (
                        <option key={s} value={s}>
                          {s.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
                        </option>
                      ))}
                    </select>
                  </td>
                  <td className="text-xs text-slate-300">
                    {alert.assigned_to != null ? "User #" + alert.assigned_to : "—"}
                  </td>
                  <td className="text-xs text-slate-400 font-mono truncate max-w-xs">
                    Rule #{alert.rule_id}
                  </td>
                  <td className="font-mono text-xs text-slate-400">
                    {new Date(alert.created_at).toLocaleString()}
                  </td>
                  <td className="text-xs">
                    <button
                      onClick={() => handleUpdate(alert, "assigned_to", 1)}
                      className="text-blue-400 hover:text-blue-300 underline text-xs"
                    >
                      Assign to me
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between text-sm">
        <div className="text-slate-400">
          Showing {alerts.length} of {total} alerts
        </div>
      </div>
    </div>
  );
}

function FilterSelect({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: string[];
}) {
  return (
    <div className="space-y-1">
      <label className="text-xs font-medium text-slate-400 uppercase">
        {label}
      </label>
      <select
        className="input"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        <option value="">All</option>
        {options.map((o) => (
          <option key={o} value={o}>
            {o.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
          </option>
        ))}
      </select>
    </div>
  );
}

function FilterInput({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}) {
  return (
    <div className="space-y-1">
      <label className="text-xs font-medium text-slate-400 uppercase">
        {label}
      </label>
      <input className="input" type="text" value={value} onChange={onChange} />
    </div>
  );
}
