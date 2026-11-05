import { useEffect, useState } from "react";
import { rulesApi } from "../services/api";
import { DetectionRule, DetectionRuleCreate } from "../types";

const RULE_TYPES = [
  "brute_force",
  "failed_login",
  "privilege_escalation",
  "admin_activity",
  "access_denied",
  "suspicious_process",
  "ioc_match",
  "frequency",
  "multi_failure",
];

export function DetectionRules() {
  const [rules, setRules] = useState<DetectionRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState<DetectionRuleCreate>({
    name: "",
    description: "",
    severity: "medium",
    threshold: 5,
    time_window: 300,
    enabled: true,
    rule_type: "brute_force",
    config: {},
  });

  const load = async () => {
    setLoading(true);
    try {
      const data = await rulesApi.list();
      setRules(data);
    } catch (err: any) {
      setError(err.message || "Failed to load rules");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      await rulesApi.create(form);
      setOpen(false);
      setForm({
        name: "",
        description: "",
        severity: "medium",
        threshold: 5,
        time_window: 300,
        enabled: true,
        rule_type: "brute_force",
        config: {},
      });
      await load();
    } catch (err: any) {
      setError(err.message || "Failed to create rule");
    }
  };

  const handleToggle = async (rule: DetectionRule) => {
    try {
      await rulesApi.update(rule.id, { enabled: !rule.enabled });
      await load();
    } catch (err: any) {
      setError(err.message || "Failed to update rule");
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm("Delete this detection rule?")) return;
    try {
      await rulesApi.remove(id);
      await load();
    } catch (err: any) {
      setError(err.message || "Failed to delete rule");
    }
  };

  const handleEvaluate = async () => {
    try {
      const result = await rulesApi.evaluate();
      alert(`Detection evaluation complete: ${result.created_alerts} new alert(s) created.`);
      await load();
    } catch (err: any) {
      setError(err.message || "Evaluation failed");
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

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-100">Detection Rules</h2>
          <p className="text-slate-400 text-sm">
            Configurable detection rules mapped to MITRE ATT&CK techniques.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={handleEvaluate} className="btn btn-primary">
            Evaluate Rules
          </button>
          <button
            onClick={() => setOpen(true)}
            className="btn btn-outline"
          >
            Add Rule
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded bg-red-900/20 border border-red-900/30 text-red-400 text-sm">
          {error}
        </div>
      )}

      {loading ? (
        <div className="animate-pulse flex items-center gap-2 text-slate-500">
          <span className="w-4 h-4 rounded-full bg-slate-700"></span>
          Loading rules…
        </div>
      ) : (
        <div className="overflow-x-auto card">
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>MITRE Technique</th>
                <th>Severity</th>
                <th>Threshold</th>
                <th>Window (s)</th>
                <th>Enabled</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {rules.length === 0 ? (
                <tr>
                  <td colSpan={8} className="text-center py-8 text-slate-500">
                    No detection rules configured.
                  </td>
                </tr>
              ) : (
                rules.map((rule) => (
                  <tr key={rule.id} className="hover:bg-slate-800/30">
                    <td className="font-mono text-xs text-slate-300 truncate max-w-xs">
                      {rule.name}
                    </td>
                    <td className="text-xs text-slate-300 capitalize">{rule.rule_type}</td>
                    <td className="text-xs text-slate-400 font-mono">
                      {rule.mitre_technique_id || "—"}
                    </td>
                    <td>
                      <span className={`badge ${severityColor(rule.severity)}`}>
                        {rule.severity}
                      </span>
                    </td>
                    <td className="text-xs text-slate-300 font-mono">
                      {rule.threshold}
                    </td>
                    <td className="text-xs text-slate-300 font-mono">
                      {rule.time_window}
                    </td>
                    <td>
                      <button
                        onClick={() => handleToggle(rule)}
                        className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                          rule.enabled
                            ? "bg-emerald-900/20 text-emerald-400 border border-emerald-900/30"
                            : "bg-slate-900/20 text-slate-400 border border-slate-800"
                        }`}
                      >
                        {rule.enabled ? "Enabled" : "Disabled"}
                      </button>
                    </td>
                    <td className="text-xs">
                      <button
                        onClick={() => handleDelete(rule.id)}
                        className="text-red-400 hover:text-red-300 underline"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Add rule modal */}
      <div className={`fixed inset-0 z-50 ${open ? "flex" : "hidden"} items-center justify-center`}>
        <div className="fixed inset-0 bg-black/60 backdrop-blur" onClick={() => setOpen(false)} />
        <div className="relative bg-sentinel-navy border border-slate-700 rounded-xl p-6 w-full max-w-md shadow-2xl">
          <h3 className="text-lg font-bold text-slate-100 mb-4">Add Detection Rule</h3>
          <form onSubmit={handleCreate} className="space-y-4">
            <div className="space-y-2">
              <label className="block text-xs font-medium text-slate-400 uppercase">
                Rule Name
              </label>
              <input
                className="input"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="e.g. Brute-force SSH"
                required
              />
            </div>
            <div className="space-y-2">
              <label className="block text-xs font-medium text-slate-400 uppercase">
                Description
              </label>
              <input
                className="input"
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                required
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="block text-xs font-medium text-slate-400 uppercase">
                  Severity
                </label>
                <select
                  className="input"
                  value={form.severity}
                  onChange={(e) => setForm({ ...form, severity: e.target.value })}
                >
                  {["critical", "high", "medium", "low"].map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
              </div>
              <div className="space-y-2">
                <label className="block text-xs font-medium text-slate-400 uppercase">
                  Rule Type
                </label>
                <select
                  className="input"
                  value={form.rule_type}
                  onChange={(e) => setForm({ ...form, rule_type: e.target.value })}
                >
                  {RULE_TYPES.map((t) => (
                    <option key={t} value={t}>
                      {t.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="block text-xs font-medium text-slate-400 uppercase">
                  Threshold
                </label>
                <input
                  className="input"
                  type="number"
                  value={form.threshold}
                  onChange={(e) => setForm({ ...form, threshold: Number(e.target.value) || 0 })}
                />
              </div>
              <div className="space-y-2">
                <label className="block text-xs font-medium text-slate-400 uppercase">
                  Time Window (s)
                </label>
                <input
                  className="input"
                  type="number"
                  value={form.time_window}
                  onChange={(e) => setForm({ ...form, time_window: Number(e.target.value) || 0 })}
                />
              </div>
            </div>
            <div className="space-y-2">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={form.enabled}
                  onChange={(e) => setForm({ ...form, enabled: e.target.checked })}
                  className="rounded bg-slate-800 border-slate-600 text-blue-600 focus:ring-blue-500"
                />
                Enabled by default
              </label>
            </div>
            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setOpen(false)}
                className="btn btn-outline"
              >
                Cancel
              </button>
              <button type="submit" className="btn btn-primary">
                Create Rule
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
