import { createContext, useContext, useState, useCallback, ReactNode } from "react";
import { User } from "../types";

interface AppContextType {
  sidebarOpen: boolean;
  toggleSidebar: () => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const toggleSidebar = useCallback(() => setSidebarOpen((s) => !s), []);
  return (
    <AppContext.Provider value={{ sidebarOpen, toggleSidebar }}>
      {children}
    </AppContext.Provider>
  );
}

export const useApp = (): AppContextType => {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useApp must be used within AppProvider");
  return ctx;
};
