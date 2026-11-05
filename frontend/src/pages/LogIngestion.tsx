import { useState } from "react";
import { ingestionApi } from "../services/api";

export function LogIngestion() {
  const [file, setFile] = useState<File | null>(null);
  const [source, setSource] = useState<string>("");
  const [sources, setSources] = useState<Array<{ id: string; label: string }>>(
    [],
  );
  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const loadSources = async () => {
    try {
      const data = await ingestionApi.sources();
      setSources(data.sources);
    } catch {
      // sources optional
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFile(e.target.files?.[0] ?? null);
    setReport(null);
    setError("");
    setSuccess("");
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    setError("");
    setReport(null);
    setSuccess("");
    try {
      const data = await ingestionApi.upload(file, source || undefined);
      setReport(data);
      setSuccess(
        `Ingestion complete: ${data.accepted} accepted, ${data.rejected} rejected, ${data.skipped} skipped (${data.duplicates} duplicates).`,
      );
    } catch (err: any) {
      setError(err.message || "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-100">Log Ingestion</h2>
        <p className="text-slate-400 text-sm">
          Import and normalize security event logs. Supported: Linux auth,
          syslog, Windows event exports, JSON, CSV.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="mb-4 text-sm font-semibold text-slate-300 uppercase tracking-wider">
            Upload Log File
          </h3>
          <form onSubmit={handleUpload} className="space-y-4">
            <div className="space-y-2">
              <label className="block text-sm font-medium text-slate-300">
                Log file
              </label>
              <input
                type="file"
                accept=".json,.csv,.log,.txt,.evtx"
                onChange={handleFileChange}
                className="block w-full text-sm text-slate-300
                  file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0
                  file:text-sm file:font-semibold file:bg-blue-600 file:text-white
                  hover:file:bg-blue-500 cursor-pointer"
              />
              {file && (
                <p className="text-xs text-slate-400">
                  {file.name} ({Math.round(file.size / 1024)} KB)
                </p>
              )}
            </div>
            <div className="space-y-2">
              <label className="block text-sm font-medium text-slate-300">
                Source type (optional override)
              </label>
              <select
                className="input"
                value={source}
                onChange={(e) => setSource(e.target.value)}
              >
                <option value="">Auto-detect</option>
                {sources.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.label}
                  </option>
                ))}
              </select>
            </div>
            <button
              type="submit"
              disabled={!file || loading}
              className="w-full btn btn-primary"
            >
              {loading ? "Ingesting…" : "Ingest Log File"}
            </button>
          </form>
          <div className="mt-4 p-3 rounded bg-sentinel-navy/30 border border-slate-800/50 text-xs text-slate-400">
            <p className="font-medium mb-1">How it works:</p>
            <ul className="list-disc list-inside space-y-1 text-xs">
              <li>Each record is parsed and normalized to the common schema.</li>
              <li>The original raw event is preserved for investigation.</li>
              <li>Malformed records are rejected with a reason — never silently discarded.</li>
              <li>Duplicate events are detected and skipped.</li>
            </ul>
          </div>
        </div>

        <div className="card">
          <h3 className="mb-4 text-sm font-semibold text-slate-300 uppercase tracking-wider">
            Ingestion Report
          </h3>
          {loading && (
            <div className="animate-pulse flex items-center gap-2 text-slate-500">
              <span className="w-4 h-4 rounded-full bg-slate-700"></span>
              Processing…
            </div>
          )}
          {!loading && !report && !error && !success && (
            <p className="text-slate-500 text-sm">
              Upload a file to see the ingestion report.
            </p>
          )}
          {success && (
            <div className="p-3 rounded bg-emerald-900/20 border border-emerald-900/30 text-emerald-400 text-sm">
              {success}
            </div>
          )}
          {error && (
            <div className="p-3 rounded bg-red-900/20 border border-red-900/30 text-red-400 text-sm">
              {error}
            </div>
          )}
          {report && (
            <div className="space-y-3">
              <div className="grid grid-cols-4 gap-2 text-sm">
                <div className="p-2 rounded bg-sentinel-navy border border-slate-700">
                  <div className="text-xs text-slate-400 uppercase">Total</div>
                  <div className="text-slate-200 font-mono">{report.total_records}</div>
                </div>
                <div className="p-2 rounded bg-emerald-900/20 border border-emerald-900/30 text-emerald-400">
                  <div className="text-xs text-emerald-400 uppercase">Accepted</div>
                  <div className="font-mono">{report.accepted}</div>
                </div>
                <div className="p-2 rounded bg-red-900/20 border border-red-900/30 text-red-400">
                  <div className="text-xs text-red-400 uppercase">Rejected</div>
                  <div className="font-mono">{report.rejected}</div>
                </div>
                <div className="p-2 rounded bg-amber-900/20 border border-amber-900/30 text-amber-400">
                  <div className="text-xs text-amber-400 uppercase">Skipped</div>
                  <div className="font-mono">{report.skipped}</div>
                </div>
              </div>
              <div className="overflow-x-auto">
                <table className="data-table text-xs">
                  <thead>
                    <tr>
                      <th>Line</th>
                      <th>Accepted</th>
                      <th>Event ID</th>
                      <th>Reason</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(report.results || []).map((r: any, i: number) => (
                      <tr key={i} className="hover:bg-slate-800/20">
                        <td className="font-mono text-slate-400">{r.line_number}</td>
                        <td>
                          <span className={`badge ${
                            r.accepted
                              ? "bg-emerald-900/20 text-emerald-400 border-emerald-900/30"
                              : "bg-red-900/20 text-red-400 border-red-900/30"
                          }`}>
                            {r.accepted ? "Yes" : "No"}
                          </span>
                        </td>
                        <td className="font-mono text-slate-300 truncate max-w-xs">
                          {r.event_id || "—"}
                        </td>
                        <td className="text-slate-400">{r.reason || "—"}</td>
                      </tr>
                    ))}
                    {report.results && report.results.length === 0 && (
                      <tr>
                        <td colSpan={4} className="text-center py-4 text-slate-500">
                          No records.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
