import { useEffect, useState } from "react";
import { mitreApi } from "../services/api";
import { MitreTechnique, RuleMapping } from "../types";

export function MitreAttck() {
  const [techniques, setTechniques] = useState<MitreTechnique[]>([]);
  const [mapping, setMapping] = useState<RuleMapping[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;
    mitreApi.mapping().then((data) => {
      if (!mounted) return;
      setTechniques(data.techniques);
      setMapping(data.rule_mapping);
    }).catch((err: any) => {
      if (!mounted) return;
      setError(err.message || "Failed to load MITRE mapping");
    }).finally(() => {
      if (mounted) setLoading(false);
    });
    return () => { mounted = false; };
  }, []);

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse flex items-center gap-2 text-slate-500">
          <span className="w-4 h-4 rounded-full bg-slate-700"></span>
          Loading MITRE ATT&CK mapping…
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

  const tactics = [...new Set(techniques.map((t) => t.tactic))];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-100">MITRE ATT&CK Mapping</h2>
        <p className="text-slate-400 text-sm">
          Detection rules mapped to official MITRE ATT&CK tactics and techniques.
        </p>
      </div>

      {/* Tactic filter */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        <button
          className="px-3 py-1.5 rounded-md bg-blue-600/10 text-blue-400 border border-blue-900/30 text-sm font-medium"
        >
          All Tactics
        </button>
        {tactics.map((tactic) => (
          <button
            key={tactic}
            className="px-3 py-1.5 rounded-md bg-slate-800/50 text-slate-300 border border-slate-700 text-sm font-medium hover:bg-slate-700"
          >
            {tactic}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {techniques.map((tech) => (
          <div key={tech.technique_id} className="card p-5">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs font-bold text-blue-400 uppercase tracking-wider">
                {tech.technique_id}
              </span>
              <span className="text-xs text-slate-400">{tech.tactic}</span>
            </div>
            <h3 className="text-sm font-semibold text-slate-200 mb-2">
              {tech.technique_name}
            </h3>
            <p className="text-xs text-slate-400 mb-3 line-clamp-2">
              {tech.description}
            </p>
            <div className="flex items-start gap-2">
              <span className="text-xs font-medium text-slate-300">Rules:</span>
              <span className="text-xs text-slate-500">
                {tech.detection_rule_types.join(", ")}
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="card overflow-x-auto">
        <h3 className="mb-4 text-sm font-semibold text-slate-300 uppercase tracking-wider">
          Rule → Technique Mapping
        </h3>
        <table className="data-table text-xs">
          <thead>
            <tr>
              <th>Rule</th>
              <th>Type</th>
              <th>Technique ID</th>
              <th>Technique</th>
              <th>Tactic</th>
            </tr>
          </thead>
          <tbody>
            {mapping.length === 0 ? (
              <tr>
                <td colSpan={5} className="text-center py-8 text-slate-500">
                  No rules mapped yet.
                </td>
              </tr>
            ) : (
              mapping.map((m) => (
                <tr key={m.rule_id} className="hover:bg-slate-800/20">
                  <td className="text-slate-300 truncate max-w-xs">{m.rule_name}</td>
                  <td className="text-slate-400 capitalize">{m.rule_type}</td>
                  <td className="font-mono text-slate-300">
                    {m.technique ? m.technique.technique_id : "—"}
                  </td>
                  <td className="text-slate-300 truncate max-w-xs">
                    {m.technique ? m.technique.technique_name : "—"}
                  </td>
                  <td className="text-slate-400 capitalize">
                    {m.technique ? m.technique.tactic : "—"}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
