import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, Users, UserPlus, FileText, FlaskConical, 
  TrendingUp, Sparkles, BookOpen, Bot, ClipboardPlus, ShieldCheck, HelpCircle
} from 'lucide-react';

const Sidebar = () => {
  const activeClass = "flex items-center space-x-3 px-3.5 py-2.5 rounded-xl bg-[#ecfdf5] text-[#0f4c3a] font-medium border border-[#a7f3d0] shadow-xs";
  const inactiveClass = "flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-slate-600 hover:bg-[#f1f7f4] hover:text-[#0f4c3a] font-medium transition-colors";

  return (
    <aside className="w-64 bg-white border-r border-[#e2ece7] min-h-[calc(100vh-4rem)] p-4 flex flex-col justify-between hidden md:flex">
      <div className="space-y-6">
        {/* Main Navigation */}
        <div>
          <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 px-3.5 mb-2">
            Core Modules
          </div>
          <nav className="space-y-1">
            <NavLink to="/dashboard" className={({ isActive }) => isActive ? activeClass : inactiveClass}>
              <LayoutDashboard className="w-4 h-4 text-[#0e7c5b]" />
              <span>Dashboard</span>
            </NavLink>
            <NavLink to="/patients" className={({ isActive }) => isActive ? activeClass : inactiveClass}>
              <Users className="w-4 h-4 text-[#0e7c5b]" />
              <span>Patients</span>
            </NavLink>
            <NavLink to="/patients/new" className={({ isActive }) => isActive ? activeClass : inactiveClass}>
              <UserPlus className="w-4 h-4 text-[#0e7c5b]" />
              <span>Add Patient</span>
            </NavLink>
          </nav>
        </div>

        {/* Clinical Intelligence Modules */}
        <div>
          <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 px-3.5 mb-2 flex items-center justify-between">
            <span>AI Modules</span>
            <span className="text-[9px] bg-slate-100 text-slate-500 px-1.5 py-0.5 rounded font-mono">12-Week Roadmap</span>
          </div>
          <nav className="space-y-1">
            <NavLink to="/reports" className={({ isActive }) => isActive ? activeClass : inactiveClass}>
              <div className="flex items-center space-x-3">
                <FileText className="w-4 h-4 text-[#0e7c5b]" />
                <span>OCR Medical Reports</span>
              </div>
              <span className="text-[9px] bg-emerald-100 text-emerald-800 font-semibold px-1.5 py-0.5 rounded">Ready</span>
            </NavLink>

            <NavLink to="/laboratory" className={({ isActive }) => isActive ? activeClass : inactiveClass}>
              <div className="flex items-center space-x-3">
                <FlaskConical className="w-4 h-4 text-[#0e7c5b]" />
                <span>Lab Value Engine</span>
              </div>
              <span className="text-[9px] bg-emerald-100 text-emerald-800 font-semibold px-1.5 py-0.5 rounded">Ready</span>
            </NavLink>

            <NavLink to="/readmission" className={({ isActive }) => isActive ? activeClass : "flex items-center justify-between px-3.5 py-2 rounded-xl text-emerald-800 bg-emerald-50/50 border border-emerald-100 text-xs"}>
              <div className="flex items-center space-x-3 font-medium">
                <TrendingUp className="w-4 h-4 text-emerald-600" />
                <span>XGBoost Readmission</span>
              </div>
              <span className="text-[9px] bg-emerald-100 text-emerald-800 font-semibold px-1.5 py-0.5 rounded">Ready</span>
            </NavLink>

            <NavLink to="/explainability" className={({ isActive }) => isActive ? activeClass : "flex items-center justify-between px-3.5 py-2 rounded-xl text-slate-600 hover:bg-[#f1f7f4] hover:text-[#0f4c3a] text-xs font-medium transition-colors"}>
              <div className="flex items-center space-x-3">
                <Sparkles className="w-4 h-4 text-emerald-600" />
                <span>SHAP Explainability</span>
              </div>
              <span className="text-[9px] bg-emerald-100 text-emerald-800 font-semibold px-1.5 py-0.5 rounded">Ready</span>
            </NavLink>

            <NavLink to="/evidence" className={({ isActive }) => isActive ? activeClass : "flex items-center justify-between px-3.5 py-2 rounded-xl text-emerald-800 bg-emerald-50/50 border border-emerald-100 text-xs"}>
              <div className="flex items-center space-x-3">
                <BookOpen className="w-4 h-4 text-emerald-600" />
                <span>RAG Evidence Base</span>
              </div>
              <span className="text-[9px] bg-emerald-100 text-emerald-800 font-semibold px-1.5 py-0.5 rounded">Ready</span>
            </NavLink>

            <NavLink to="/assistant" className="flex items-center justify-between px-3.5 py-2 rounded-xl text-emerald-800 bg-emerald-50/50 border border-emerald-100 text-xs">
              <div className="flex items-center space-x-3">
                <Bot className="w-4 h-4 text-emerald-600" />
                <span>AI Clinical Assistant</span>
              </div>
              <span className="text-[9px] bg-emerald-100 text-emerald-800 font-semibold px-1.5 py-0.5 rounded">Ready</span>
            </NavLink>

            <NavLink to="/clinical-summary" className={({ isActive }) => isActive ? activeClass : "flex items-center justify-between px-3.5 py-2 rounded-xl text-emerald-800 bg-emerald-50/50 border border-emerald-100 text-xs"}>
              <div className="flex items-center space-x-3">
                <ClipboardPlus className="w-4 h-4 text-emerald-600" />
                <span>AI Clinical Summary</span>
              </div>
              <span className="text-[9px] bg-emerald-100 text-emerald-800 font-semibold px-1.5 py-0.5 rounded">Ready</span>
            </NavLink>
          </nav>
        </div>
      </div>

      {/* Bottom Status Card */}
      <div className="bg-[#f7faf8] border border-[#e2ece7] rounded-xl p-3 text-xs space-y-2">
        <div className="flex items-center space-x-2 text-[#0f4c3a] font-medium">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
          <span>System Status: Online</span>
        </div>
        <p className="text-[11px] text-slate-500">
          Week 1 Foundation active with secure Doctor JWT authentication and PostgreSQL DB integration.
        </p>
      </div>
    </aside>
  );
};

export default Sidebar;
