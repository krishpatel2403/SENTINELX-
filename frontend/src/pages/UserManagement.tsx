import { useEffect, useState } from "react";
import { usersApi } from "../services/api";
import { useAuth } from "../hooks/useAuth";
import { User } from "../types";

const ROLES = ["admin", "analyst"];

export function UserManagement() {
  const { isAdmin } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    role: "analyst" as const,
  });

  const load = async () => {
    setLoading(true);
    try {
      const data = await usersApi.list();
      setUsers(data);
    } catch (err: any) {
      setError(err.message || "Failed to load users");
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
      await usersApi.create(form);
      setOpen(false);
      setForm({ username: "", email: "", password: "", role: "analyst" });
      await load();
    } catch (err: any) {
      setError(err.message || "Failed to create user");
    }
  };

  const handleUpdateRole = async (user: User, role: string) => {
    try {
      await usersApi.update(user.id, { role: role as any });
      await load();
    } catch (err: any) {
      setError(err.message || "Failed to update role");
    }
  };

  const handleToggleActive = async (user: User) => {
    try {
      await usersApi.update(user.id, { is_active: !user.is_active });
      await load();
    } catch (err: any) {
      setError(err.message || "Failed to update user");
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm("Delete this user?")) return;
    try {
      await usersApi.remove(id);
      await load();
    } catch (err: any) {
      setError(err.message || "Failed to delete user");
    }
  };

  if (!isAdmin) {
    return (
      <div className="p-6 card">
        <h2 className="text-2xl font-bold text-slate-100">User Management</h2>
        <p className="text-slate-400 mt-2">
          User management is restricted to administrators.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-100">User Management</h2>
          <p className="text-slate-400 text-sm">
            Manage analyst and administrator accounts (admin-only).
          </p>
        </div>
        <button
          onClick={() => setOpen(true)}
          className="btn btn-outline"
        >
          Add User
        </button>
      </div>

      {error && (
        <div className="p-4 rounded bg-red-900/20 border border-red-900/30 text-red-400 text-sm">
          {error}
        </div>
      )}

      {loading ? (
        <div className="animate-pulse flex items-center gap-2 text-slate-500">
          <span className="w-4 h-4 rounded-full bg-slate-700"></span>
          Loading users…
        </div>
      ) : (
        <div className="overflow-x-auto card">
          <table className="data-table">
            <thead>
              <tr>
                <th>Username</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.length === 0 ? (
                <tr>
                  <td colSpan={5} className="text-center py-8 text-slate-500">
                    No users found.
                  </td>
                </tr>
              ) : (
                users.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-800/30">
                    <td className="font-mono text-xs text-slate-300">{u.username}</td>
                    <td className="text-xs text-slate-400">{u.email}</td>
                    <td>
                      <select
                        value={u.role}
                        onChange={(e) => handleUpdateRole(u, e.target.value)}
                        className="input h-8 text-xs bg-transparent border-0 focus:ring-0"
                      >
                        {ROLES.map((r) => (
                          <option key={r} value={r}>
                            {r}
                          </option>
                        ))}
                      </select>
                    </td>
                    <td>
                      <span className={`badge ${
                        u.is_active ? "badge-low" : "badge-unknown"
                      }`}>
                        {u.is_active ? "Active" : "Inactive"}
                      </span>
                    </td>
                    <td className="text-xs">
                      <button
                        onClick={() => handleToggleActive(u)}
                        className="text-xs text-blue-400 hover:text-blue-300 underline"
                      >
                        {u.is_active ? "Deactivate" : "Activate"}
                      </button>{" "}
                      {u.id !== 1 && (
                        <button
                          onClick={() => handleDelete(u.id)}
                          className="text-xs text-red-400 hover:text-red-300 underline ml-2"
                        >
                          Delete
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Add user modal */}
      <div className={`fixed inset-0 z-50 ${open ? "flex" : "hidden"} items-center justify-center`}>
        <div className="fixed inset-0 bg-black/60 backdrop-blur" onClick={() => setOpen(false)} />
        <div className="relative bg-sentinel-navy border border-slate-700 rounded-xl p-6 w-full max-w-md shadow-2xl">
          <h3 className="text-lg font-bold text-slate-100 mb-4">Add User</h3>
          <p className="text-xs text-slate-500 mb-4">
            Passwords are hashed with bcrypt. Registration is admin-restricted.
          </p>
          <form onSubmit={handleCreate} className="space-y-4">
            <div className="space-y-2">
              <label className="block text-xs font-medium text-slate-400 uppercase">
                Username
              </label>
              <input
                className="input"
                value={form.username}
                onChange={(e) => setForm({ ...form, username: e.target.value })}
                required
              />
            </div>
            <div className="space-y-2">
              <label className="block text-xs font-medium text-slate-400 uppercase">
                Email
              </label>
              <input
                className="input"
                type="email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                required
              />
            </div>
            <div className="space-y-2">
              <label className="block text-xs font-medium text-slate-400 uppercase">
                Password (min 8 chars)
              </label>
              <input
                className="input"
                type="password"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                required
              />
            </div>
            <div className="space-y-2">
              <label className="block text-xs font-medium text-slate-400 uppercase">
                Role
              </label>
              <select
                className="input"
                value={form.role}
                onChange={(e) => setForm({ ...form, role: e.target.value as any })}
              >
                {ROLES.map((r) => (
                  <option key={r} value={r}>
                    {r}
                  </option>
                ))}
              </select>
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
                Create User
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
