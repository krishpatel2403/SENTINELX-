import { useState } from "react";
import { reportsApi } from "../services/api";
import { ReportGenerate } from "../types";

export function Reports() {
  const [reports, setReports] = useState<Array<{
    id: number;
    report_id: string;
    format: string;
    period_start?: string | null;
    period_end?: string | null;
    checksum?: string | null;
    created_at: string;
  }>>([]);
  const [loading, setLoading] = useState(false);
  const [generateLoading, setGenerateLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [format, setFormat] = useState<"pdf" | "json" | "csv">("json");
  const [periodStart, setPeriodStart] = useState("");
  const [periodEnd, setPeriodEnd] = useState("");

  const load = async () => {
    setLoading(true);
    try {
      const data = await reportsApi.list();
      setReports(data);
    } catch (err: any) {
      setError(err.message || "Failed to load reports");
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setGenerateLoading(true);
    setError("");
    setSuccess("");
    try {
      const data: ReportGenerate = {
        format,
        period_start: periodStart || undefined,
        period_end: periodEnd || undefined,
      };
      const result = await reportsApi.generate(data);
      setSuccess(
        `Report generated: ${result.report_id} (${result.format}).`,
      );
      await load();
    } catch (err: any) {
      setError(err.message || "Report generation failed");
    } finally {
      setGenerateLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-100">Reports</h2>
        <p className="text-slate-400 text-sm">
          Generate professional security reports in PDF, JSON, or CSV.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="mb-4 text-sm font-semibold text-slate-300 uppercase tracking-wider">
            Generate Report
          </h3>
          <form onSubmit={handleGenerate} className="space-y-4">
            <div className="space-y-2">
              <label className="text-xs font-medium text-slate-400 uppercase">
                Format
              </label>
              <select
                className="input"
                value={format}
                onChange={(e) => setFormat(e.target.value as any)}
              >
                <option value="json">JSON</option>
                <option value="csv">CSV</option>
                <option value="pdf">PDF</option>
              </select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-xs font-medium text-slate-400 uppercase">
                  Period Start
                </label>
                <input
                  className="input"
                  type="date"
                  value={periodStart}
                  onChange={(e) => setPeriodStart(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs font-medium text-slate-400 uppercase">
                  Period End
                </label>
                <input
                  className="input"
                  type="date"
                  value={periodEnd}
                  onChange={(e) => setPeriodEnd(e.target.value)}
                />
              </div>
            </div>
            <button
              type="submit"
              disabled={generateLoading}
              className="w-full btn btn-primary"
            >
              {generateLoading ? "Generating…" : "Generate Report"}
            </button>
          </form>
          {success && (
            <div className="mt-4 p-3 rounded bg-emerald-900/20 border border-emerald-900/30 text-emerald-400 text-sm">
              {success}
            </div>
          )}
          {error && (
            <div className="mt-3 p-3 rounded bg-red-900/20 border border-red-900/30 text-red-400 text-sm">
              {error}
            </div>
          )}
          <div className="mt-4 p-3 rounded bg-sentinel-navy/30 border border-slate-800/50 text-xs text-slate-400">
            <p className="font-medium mb-1">Reports include:</p>
            <ul className="list-disc list-inside space-y-1">
              <li>Reporting period</li>
              <li>Total events and detection statistics</li>
              <li>Alert breakdown by severity and status</li>
              <li>Incident summaries</li>
              <li>Relevant indicators of compromise</li>
              <li>Investigation notes and recommendations</li>
            </ul>
          </div>
        </div>

        <div className="card">
          <h3 className="mb-4 text-sm font-semibold text-slate-300 uppercase tracking-wider">
            Generated Reports
          </h3>
          {loading ? (
            <div className="animate-pulse flex items-center gap-2 text-slate-500">
              <span className="w-4 h-4 rounded-full bg-slate-700"></span>
              Loading…
            </div>
          ) : reports.length === 0 ? (
            <p className="text-slate-500 text-sm text-center py-8">
              No reports generated yet.
            </p>
          ) : (
            <table className="data-table text-xs">
              <thead>
                <tr>
                  <th>Report ID</th>
                  <th>Format</th>
                  <th>Period Start</th>
                  <th>Period End</th>
                  <th>SHA-256</th>
                  <th>Generated</th>
                </tr>
              </thead>
              <tbody>
                {reports.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-800/20">
                    <td className="font-mono text-slate-300 truncate max-w-xs">
                      {r.report_id}
                    </td>
                    <td className="text-slate-400 capitalize">{r.format}</td>
                    <td className="text-slate-400">{r.period_start || "—"}</td>
                    <td className="text-slate-400">{r.period_end || "—"}</td>
                    <td className="font-mono text-slate-400 truncate max-w-xs">
                      {r.checksum || "—"}
                    </td>
                    <td className="text-slate-400">
                      {new Date(r.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
