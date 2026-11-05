import { Outlet } from "react-router-dom";
import { Sidebar, TopBar } from "./Sidebar";

export function MainLayout() {
  return (
    <div className="min-h-screen bg-sentinel-deep text-slate-200">
      <Sidebar />
      <div className="ml-64">
        <TopBar />
        <main className="p-6"><Outlet /></main>
      </div>
    </div>
  );
}
