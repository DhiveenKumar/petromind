import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import {
  LayoutDashboard, MessageSquare, TrendingUp, Camera,
  FileText, Activity, Flame
} from "lucide-react";
import Dashboard from "./pages/Dashboard";
import KnowledgeCopilot from "./pages/KnowledgeCopilot";
import PredictiveMaintenance from "./pages/PredictiveMaintenance";
import VisualInspection from "./pages/VisualInspection";
import UnifiedReport from "./pages/UnifiedReport";
import Monitoring from "./pages/Monitoring";
import RoleSwitcher from "./components/RoleSwitcher";

const navItems = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/knowledge", icon: MessageSquare, label: "Knowledge Copilot" },
  { to: "/prediction", icon: TrendingUp, label: "Predictive Maintenance" },
  { to: "/vision", icon: Camera, label: "Visual Inspection" },
  { to: "/report", icon: FileText, label: "Unified AI Report" },
  { to: "/monitoring", icon: Activity, label: "Monitoring" },
];

function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen bg-[#0a0908] text-[#e8e3dc]">
        {/* Sidebar */}
        <aside className="w-64 bg-[#1a1614] border-r border-[#332b26] flex flex-col">
          <div className="p-5 border-b border-[#332b26]">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-[#d97706] to-[#f59e0b] flex items-center justify-center">
                <Flame size={20} className="text-[#0a0908]" />
              </div>
              <div>
                <div className="font-bold text-[15px] text-white tracking-tight">PetroMind</div>
                <div className="text-[10px] text-[#a89a8c] uppercase tracking-widest">AI Platform</div>
              </div>
            </div>
          </div>

          <nav className="flex-1 p-3 space-y-1">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                    isActive
                      ? "bg-[#d97706]/10 text-[#f59e0b] border border-[#d97706]/30"
                      : "text-[#a89a8c] hover:bg-[#241f1c] hover:text-[#e8e3dc]"
                  }`
                }
              >
                <item.icon size={17} />
                {item.label}
              </NavLink>
            ))}
          </nav>

          <div className="p-3 border-t border-[#332b26]">
            <RoleSwitcher />
          </div>
        </aside>

        {/* Main content */}
        <main className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/knowledge" element={<KnowledgeCopilot />} />
            <Route path="/prediction" element={<PredictiveMaintenance />} />
            <Route path="/vision" element={<VisualInspection />} />
            <Route path="/report" element={<UnifiedReport />} />
            <Route path="/monitoring" element={<Monitoring />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;