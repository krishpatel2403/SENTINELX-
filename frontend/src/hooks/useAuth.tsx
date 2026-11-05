import {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  ReactNode,
} from "react";
import { authApi, Token } from "../services/api";
import { User } from "../types";

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  register: (
    username: string,
    email: string,
    password: string,
    role?: string,
  ) => Promise<void>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
  isAdmin: boolean;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const t = localStorage.getItem("sentinelx_token");
    if (t) {
      setToken(t);
      authApi
        .me()
        .then((u) => setUser(u))
        .catch(() => {
          localStorage.removeItem("sentinelx_token");
          setToken(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = useCallback(
    async (username: string, password: string) => {
      const data: Token = await authApi.login({ username, password });
      localStorage.setItem("sentinelx_token", data.access_token);
      setToken(data.access_token);
      const u = await authApi.me();
      setUser(u);
    },
    [],
  );

  const register = useCallback(
    async (username: string, email: string, password: string, role?: string) => {
      await authApi.register({ username, email, password, role });
    },
    [],
  );

  const logout = useCallback(async () => {
    try {
      await authApi.logout();
    } catch {
      // ignore
    }
    localStorage.removeItem("sentinelx_token");
    setToken(null);
    setUser(null);
  }, []);

  const isAuthenticated = !!token && !!user;
  const isAdmin = user?.role === "admin";

  return (
    <AuthContext.Provider
      value={{ user, token, login, register, logout, isAuthenticated, isAdmin, loading }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = (): AuthContextType => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
};
