import { useEffect, useState } from "react";
import { eventsApi } from "../services/api";
import { SecurityEvent, SecurityEventFilter } from "../types";

const SEVERITIES = ["critical", "high", "medium", "low"];

export function SecurityEvents() {
  const [events, setEvents] = useState<SecurityEvent[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [filter, setFilter] = useState<SecurityEventFilter>({
    page: 1,
    page_size: 25,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = async () => {
    setLoading(true);
    try {
      const data = await eventsApi.list({ ...filter, page, page_size: pageSize });
      setEvents(data.items);
      setTotal(data.total);
    } catch (err: any) {
      setError(err.message || "Failed to load events");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [page, pageSize, filter.source, filter.severity, filter.event_type, filter.username, filter.source_ip, filter.start_time, filter.end_time, filter.search]);

  const severityColor = (sev: string) => {
    switch (sev) {
      case "critical": return "badge-critical";
      case "high": return "badge-high";
      case "medium": return "badge-medium";
      case "low": return "badge-low";
      default: return "badge-unknown";
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse flex items-center gap-2 text-slate-500">
          <span className="w-4 h-4 rounded-full bg-slate-700"></span>
          Loading events…
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-100">Security Events</h2>
          <p className="text-slate-400 text-sm">
            Normalized security events from ingested logs.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setFilter({ ...filter, source: "", severity: "", event_type: "", username: "", source_ip: "", start_time: "", end_time: "", search: "" })}
            className="btn btn-outline"
          >
            Clear filters
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded bg-red-900/20 border border-red-900/30 text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* Filters */}
      <div className="card overflow-x-auto">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6 gap-3 p-4">
          <FilterField
            label="Source"
            value={filter.source ?? ""}
            onChange={(e) => setFilter({ ...filter, source: e.target.value })}
            options={["linux_auth", "syslog", "windows_event", "json", "csv"]}
          />
          <FilterField
            label="Severity"
            value={filter.severity ?? ""}
            onChange={(e) => setFilter({ ...filter, severity: e.target.value })}
            options={SEVERITIES}
          />
          <FilterField
            label="Event Type"
            value={filter.event_type ?? ""}
            onChange={(e) => setFilter({ ...filter, event_type: e.target.value })}
          />
          <FilterField
            label="Username"
            value={filter.username ?? ""}
            onChange={(e) => setFilter({ ...filter, username: e.target.value })}
          />
          <FilterField
            label="Source IP"
            value={filter.source_ip ?? ""}
            onChange={(e) => setFilter({ ...filter, source_ip: e.target.value })}
          />
          <FilterField
            label="Search"
            value={filter.search ?? ""}
            onChange={(e) => setFilter({ ...filter, search: e.target.value })}
          />
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto card">
        <table className="data-table">
          <thead>
            <tr>
              <th>Event ID</th>
              <th>Timestamp</th>
              <th>Source</th>
              <th>Hostname</th>
              <th>Username</th>
              <th>Source IP</th>
              <th>Type</th>
              <th>Severity</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            {events.length === 0 ? (
              <tr>
                <td colSpan={9} className="text-center py-8 text-slate-500">
                  No events found. Import logs via Log Ingestion.
                </td>
              </tr>
            ) : (
              events.map((ev) => (
                <tr key={ev.id} className="hover:bg-slate-800/30">
                  <td className="font-mono text-xs text-slate-400 truncate max-w-xs">
                    {ev.event_id}
                  </td>
                  <td className="font-mono text-xs text-slate-300">
                    {ev.timestamp}
                  </td>
                  <td className="text-xs text-slate-400 capitalize">{ev.source}</td>
                  <td className="text-xs text-slate-300">{ev.hostname || "—"}</td>
                  <td className="text-xs text-slate-300">{ev.username || "—"}</td>
                  <td className="font-mono text-xs text-slate-300">{ev.source_ip || "—"}</td>
                  <td className="text-xs text-slate-300 capitalize">{ev.event_type}</td>
                  <td>
                    <span className={`badge ${severityColor(ev.severity)}`}>
                      {ev.severity}
                    </span>
                  </td>
                  <td className="text-xs text-slate-200 truncate max-w-xs">
                    {ev.description}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between text-sm">
        <div className="text-slate-400">
          Showing {events.length} of {total} events
        </div>
        <div className="flex items-center gap-2">
          <button
            disabled={page === 1 || loading}
            onClick={() => setPage(page - 1)}
            className="btn btn-outline"
          >
            Prev
          </button>
          <span className="px-2 text-slate-300">Page {page}</span>
          <button
            disabled={(page - 1) * pageSize + events.length >= total || loading}
            onClick={() => setPage(page + 1)}
            className="btn btn-outline"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}

function FilterField({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void;
  options?: string[];
}) {
  return (
    <div className="space-y-1">
      <label className="text-xs font-medium text-slate-400 uppercase">
        {label}
      </label>
      {options ? (
        <select
          className="input"
          value={value}
          onChange={onChange as any}
        >
          <option value="">All</option>
          {options.map((o) => (
            <option key={o} value={o}>
              {o}
            </option>
          ))}
        </select>
      ) : (
        <input className="input" type="text" value={value} onChange={onChange} />
      )}
    </div>
  );
}
