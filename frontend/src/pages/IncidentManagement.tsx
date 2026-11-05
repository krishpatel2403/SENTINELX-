import { useEffect, useState } from "react";
import { incidentsApi } from "../services/api";
import { Incident, IncidentFilter, IncidentNoteCreate } from "../types";

const STATUSES = ["detection", "triage", "investigation", "containment", "recovery", "closure"];
const SEVERITIES = ["critical", "high", "medium", "low"];

export function IncidentManagement() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [filter, setFilter] = useState<IncidentFilter>({ page: 1, page_size: 25 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = async () => {
    setLoading(true);
    try {
      const data = await incidentsApi.list({ ...filter, page, page_size: pageSize });
      setIncidents(data.items);
      setTotal(data.total);
    } catch (err: any) {
      setError(err.message || "Failed to load incidents");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [page, pageSize, filter.status, filter.severity, filter.assigned_to, filter.search]);

  const statusColor = (status: string) => {
    switch (status) {
      case "detection": return "badge-medium";
      case "triage": return "badge-medium";
      case "investigation": return "badge-high";
      case "containment": return "badge-critical";
      case "recovery": return "badge-low";
      case "closure": return "badge-low";
      default: return "badge-medium";
    }
  };

  const handleUpdate = async (incident: Incident, field: string, value: any) => {
    try {
      await incidentsApi.update(incident.id, { [field]: value });
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
          Loading incidents…
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-100">Incident Response</h2>
          <p className="text-slate-400 text-sm">
            Manage the incident lifecycle: Detection → Triage → Investigation → Containment → Recovery → Closure.
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
              <th>Incident ID</th>
              <th>Title</th>
              <th>Severity</th>
              <th>Status</th>
              <th>Assigned To</th>
              <th>Alerts</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {incidents.length === 0 ? (
              <tr>
                <td colSpan={8} className="text-center py-8 text-slate-500">
                  No incidents found.
                </td>
              </tr>
            ) : (
              incidents.map((inc) => (
                <tr key={inc.id} className="hover:bg-slate-800/30">
                  <td className="font-mono text-xs text-slate-400 truncate max-w-xs">
                    {inc.incident_id}
                  </td>
                  <td className="text-xs text-slate-200 truncate max-w-md">
                    {inc.title}
                  </td>
                  <td>
                    <span className={`badge ${statusColor(inc.severity)}`}>
                      {inc.severity}
                    </span>
                  </td>
                  <td>
                    <select
                      value={inc.status}
                      onChange={(e) => handleUpdate(inc, "status", e.target.value)}
                      className="input h-8 text-xs bg-transparent border-0 focus:ring-0"
                    >
                      {STATUSES.map((s) => (
                        <option key={s} value={s}>
                          {s.charAt(0).toUpperCase() + s.slice(1)}
                        </option>
                      ))}
                    </select>
                  </td>
                  <td className="text-xs text-slate-300">
                    {inc.assigned_to != null ? "User #" + inc.assigned_to : "—"}
                  </td>
                  <td className="text-xs text-slate-300 font-mono">
                    {inc.alerts.length}
                  </td>
                  <td className="font-mono text-xs text-slate-400">
                    {new Date(inc.created_at).toLocaleString()}
                  </td>
                  <td className="text-xs">
                    <button
                      onClick={() => handleUpdate(inc, "assigned_to", 1)}
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
          Showing {incidents.length} of {total} incidents
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
            {o.charAt(0).toUpperCase() + o.slice(1)}
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
