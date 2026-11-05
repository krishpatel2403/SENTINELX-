import { useEffect, useState } from "react";
import { intelligenceApi } from "../services/api";
import { ThreatIndicator, ThreatIndicatorFilter } from "../types";

const TYPES = ["ip", "domain", "hash", "url"];
const CLASSIFICATIONS = ["malicious", "suspicious", "benign", "unknown"];

export function ThreatIntelligence() {
  const [indicators, setIndicators] = useState<ThreatIndicator[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [filter, setFilter] = useState<ThreatIndicatorFilter>({ page: 1, page_size: 25 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [enrichInput, setEnrichInput] = useState({ type: "ip", value: "" });
  const [enrichResult, setEnrichResult] = useState<any>(null);
  const [enrichLoading, setEnrichLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const data = await intelligenceApi.listIndicators({
        ...filter, page, page_size: pageSize,
      });
      setIndicators(data.items);
      setTotal(data.total);
    } catch (err: any) {
      setError(err.message || "Failed to load indicators");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [page, pageSize, filter.indicator_type, filter.classification, filter.search]);

  const handleEnrich = async (e: React.FormEvent) => {
    e.preventDefault();
    setEnrichLoading(true);
    setEnrichResult(null);
    try {
      const result = await intelligenceApi.enrich(enrichInput.type, enrichInput.value);
      setEnrichResult(result);
    } catch (err: any) {
      setError(err.message || "Enrichment failed");
    } finally {
      setEnrichLoading(false);
    }
  };

  const classColor = (cls: string) => {
    switch (cls) {
      case "malicious": return "badge-critical";
      case "suspicious": return "badge-high";
      case "benign": return "badge-low";
      default: return "badge-unknown";
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-100">Threat Intelligence</h2>
        <p className="text-slate-400 text-sm">
          Enrich indicators of compromise (IPs, domains, file hashes, URLs).
        </p>
      </div>

      {/* Enrichment card */}
      <div className="card">
        <h3 className="mb-4 text-sm font-semibold text-slate-300 uppercase tracking-wider">
          Enrich an Indicator
        </h3>
        <form onSubmit={handleEnrich} className="grid grid-cols-1 sm:grid-cols-3 gap-4 items-end">
          <div className="space-y-2">
            <label className="text-xs font-medium text-slate-400 uppercase">Type</label>
            <select
              className="input"
              value={enrichInput.type}
              onChange={(e) => setEnrichInput({ ...enrichInput, type: e.target.value })}
            >
              {TYPES.map((t) => (
                <option key={t} value={t}>
                  {t.toUpperCase()}
                </option>
              ))}
            </select>
          </div>
          <div className="space-y-2">
            <label className="text-xs font-medium text-slate-400 uppercase">Value</label>
            <input
              className="input"
              placeholder="e.g. 1.2.3.4 or evil.example.com"
              value={enrichInput.value}
              onChange={(e) => setEnrichInput({ ...enrichInput, value: e.target.value })}
            />
          </div>
          <button
            type="submit"
            disabled={enrichLoading}
            className="btn btn-primary"
          >
            {enrichLoading ? "Enriching…" : "Enrich"}
          </button>
        </form>
        {enrichResult && (
          <div className="mt-4 p-4 rounded border bg-sentinel-navy/30">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
              <div>
                <div className="text-xs text-slate-400 uppercase">Classification</div>
                <span className={`badge ${classColor(enrichResult.classification)}`}>
                  {enrichResult.classification}
                </span>
              </div>
              <div>
                <div className="text-xs text-slate-400 uppercase">Available</div>
                <span className={`text-xs font-mono ${
                  enrichResult.available ? "text-emerald-400" : "text-slate-500"
                }`}>
                  {enrichResult.available ? "Yes" : "No (unknown)"}
                </span>
              </div>
              <div>
                <div className="text-xs text-slate-400 uppercase">Source</div>
                <span className="text-xs text-slate-300">{enrichResult.source || "—"}</span>
              </div>
              <div>
                <div className="text-xs text-slate-400 uppercase">Confidence</div>
                <span className="text-xs text-slate-300">{enrichResult.confidence ?? "—"}</span>
              </div>
            </div>
            <div className="mt-3 space-y-1 text-xs">
              <div><span className="text-slate-400">Value:</span> {enrichResult.indicator_value}</div>
              <div><span className="text-slate-400">Reputation:</span> {enrichResult.reputation || "—"}</div>
              <div><span className="text-slate-400">First seen:</span> {enrichResult.first_seen || "—"}</div>
              <div><span className="text-slate-400">Last seen:</span> {enrichResult.last_seen || "—"}</div>
            </div>
            <p className="mt-2 text-xs text-slate-500">
              {enrichResult.available
                ? "Intelligence found from configured source."
                : "No intelligence available for this IOC — this does not mean it is clean."}
            </p>
          </div>
        )}
        {error && (
          <div className="mt-3 p-3 rounded bg-red-900/20 border border-red-900/30 text-red-400 text-sm">
            {error}
          </div>
        )}
      </div>

      {/* Indicators table */}
      <div className="card overflow-x-auto">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 p-4">
          <FilterSelect
            label="Type"
            value={filter.indicator_type ?? ""}
            onChange={(v) => setFilter({ ...filter, indicator_type: v || undefined })}
            options={TYPES}
          />
          <FilterSelect
            label="Classification"
            value={filter.classification ?? ""}
            onChange={(v) => setFilter({ ...filter, classification: v || undefined })}
            options={CLASSIFICATIONS}
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
        <table className="data-table">
          <thead>
            <tr>
              <th>Type</th>
              <th>Value</th>
              <th>Classification</th>
              <th>Source</th>
              <th>Confidence</th>
              <th>First Seen</th>
              <th>Last Seen</th>
            </tr>
          </thead>
          <tbody>
            {indicators.length === 0 ? (
              <tr>
                <td colSpan={7} className="text-center py-8 text-slate-500">
                  No threat indicators. Use enrichment to add indicators.
                </td>
              </tr>
            ) : (
              indicators.map((ind) => (
                <tr key={ind.id} className="hover:bg-slate-800/30">
                  <td className="text-xs text-slate-400 capitalize">{ind.indicator_type}</td>
                  <td className="font-mono text-xs text-slate-300 truncate max-w-xs">
                    {ind.indicator_value}
                  </td>
                  <td>
                    <span className={`badge ${classColor(ind.classification)}`}>
                      {ind.classification}
                    </span>
                  </td>
                  <td className="text-xs text-slate-400">{ind.source || "—"}</td>
                  <td className="text-xs text-slate-300 font-mono">{ind.confidence ?? "—"}</td>
                  <td className="text-xs text-slate-400">{ind.first_seen || "—"}</td>
                  <td className="text-xs text-slate-400">{ind.last_seen || "—"}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between text-sm">
        <div className="text-slate-400">
          Showing {indicators.length} of {total} indicators
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
            {o.toUpperCase()}
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
