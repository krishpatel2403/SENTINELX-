import { useEffect, useState } from "react";
import { useAuth } from "../hooks/useAuth";

export function Settings() {
  const { user } = useAuth();
  const [settings, setSettings] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    // Settings are read from backend config; here we surface a read-only view.
    setLoading(false);
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-100">Settings</h2>
        <p className="text-slate-400 text-sm">
          Platform configuration and environment information.
        </p>
      </div>

      {loading ? (
        <div className="animate-pulse flex items-center gap-2 text-slate-500">
          <span className="w-4 h-4 rounded-full bg-slate-700"></span>
          Loading settings…
        </div>
      ) : (
        <>
          <div className="card">
            <h3 className="mb-4 text-sm font-semibold text-slate-300 uppercase tracking-wider">
              Account
            </h3>
            <table className="data-table text-xs">
              <tbody>
                <tr>
                  <td className="text-slate-400">Username</td>
                  <td className="font-mono text-slate-300">{user?.username}</td>
                </tr>
                <tr>
                  <td className="text-slate-400">Email</td>
                  <td className="text-slate-300">{user?.email}</td>
                </tr>
                <tr>
                  <td className="text-slate-400">Role</td>
                  <td className="text-slate-300 capitalize">{user?.role}</td>
                </tr>
                <tr>
                  <td className="text-slate-400">Status</td>
                  <td className="text-slate-300">{user?.is_active ? "Active" : "Inactive"}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div className="card">
            <h3 className="mb-4 text-sm font-semibold text-slate-300 uppercase tracking-wider">
              Platform
            </h3>
            <table className="data-table text-xs">
              <tbody>
                <tr>
                  <td className="text-slate-400">Application</td>
                  <td className="font-mono text-slate-300">SentinelX SOC Platform</td>
                </tr>
                <tr>
                  <td className="text-slate-400">Version</td>
                  <td className="font-mono text-slate-300">0.1.0</td>
                </tr>
                <tr>
                  <td className="text-slate-400">Database</td>
                  <td className="font-mono text-slate-300">SQLite (default) / PostgreSQL (optional)</td>
                </tr>
                <tr>
                  <td className="text-slate-400">Authentication</td>
                  <td className="font-mono text-slate-300">JWT + RBAC (admin/analyst)</td>
                </tr>
                <tr>
                  <td className="text-slate-400">Threat Intel</td>
                  <td className="font-mono text-slate-300">Offline by default (optional public feeds)</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div className="card">
            <h3 className="mb-4 text-sm font-semibold text-slate-300 uppercase tracking-wider">
              Security Notes
            </h3>
            <ul className="list-disc list-inside space-y-2 text-xs text-slate-400">
              <li>Passwords are hashed with bcrypt; hashes are never exposed via APIs.</li>
              <li>JWT access tokens are short-lived.</li>
              <li>Role-based access control: admin and analyst roles.</li>
              <li>All authenticated actions are written to the audit log.</li>
              <li>No automatic destructive containment actions are performed.</li>
              <li>Suspicious commands/payloads are never executed during analysis.</li>
            </ul>
          </div>
        </>
      )}
    </div>
  );
}
