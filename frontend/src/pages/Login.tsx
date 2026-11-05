import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(username, password);
      navigate("/app/dashboard");
    } catch (err: any) {
      setError(err.message || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-sentinel-deep p-4">
      <div className="w-full max-w-md card">
        <div className="mb-6 text-center">
          <div className="w-12 h-12 rounded bg-blue-600 flex items-center justify-center mx-auto mb-3">
            <span className="text-white font-bold text-xl">S</span>
          </div>
          <h2 className="text-2xl font-bold text-slate-100">SENTINELX</h2>
          <p className="text-slate-400 text-sm mt-1">
            Security Operations Center Platform
          </p>
        </div>
        {error && (
          <div className="mb-4 p-3 rounded bg-red-900/20 border border-red-900/30 text-red-400 text-sm">
            {error}
          </div>
        )}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <label className="block text-sm font-medium text-slate-300">
              Username
            </label>
            <input
              className="input"
              placeholder="admin"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          <div className="space-y-2">
            <label className="block text-sm font-medium text-slate-300">
              Password
            </label>
            <input
              className="input"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button
            type="submit"
            className="w-full btn btn-primary"
            disabled={loading}
          >
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </form>
        <p className="mt-6 text-center text-xs text-slate-500">
          Default admin: admin / ChangeMeAdmin123!
        </p>
      </div>
    </div>
  );
}
