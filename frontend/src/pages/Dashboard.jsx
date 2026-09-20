import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { patientService } from '../services/api';
import { useAuth } from '../context/AuthContext';
import StatCard from '../components/StatCard';
import ClinicalDisclaimer from '../components/ClinicalDisclaimer';
import { 
  Users, Activity, TrendingUp, UserPlus, ArrowRight, 
  Clock, ShieldCheck, CheckCircle2, ChevronRight, AlertCircle, FileText, FlaskConical, Bot
} from 'lucide-react';

const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const res = await patientService.getStats();
      setStats(res.data);
    } catch (err) {
      console.error("Dashboard error:", err);
      setError('Unable to load clinical statistics.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b border-[#e2ece7]">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 tracking-tight">
            Clinical Dashboard
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Welcome back, <span className="font-semibold text-[#0e7c5b]">Dr. {user?.full_name}</span> • {user?.hospital_affiliation || 'City Central Hospital'}
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <Link to="/patients/new" className="btn-med-primary text-xs flex items-center space-x-1.5 shadow-sm">
            <UserPlus className="w-4 h-4" />
            <span>Add New Patient</span>
          </Link>
          <Link to="/patients" className="btn-med-secondary text-xs flex items-center space-x-1.5">
            <Users className="w-4 h-4" />
            <span>Patient Directory</span>
          </Link>
        </div>
      </div>

      {/* Doctor-in-the-Loop Safety Banner */}
      <ClinicalDisclaimer />

      {/* Error state */}
      {error && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm flex items-center space-x-2">
          <AlertCircle className="w-4 h-4" />
          <span>{error}</span>
        </div>
      )}

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Assigned Patients"
          value={loading ? '...' : (stats?.total_patients || 0)}
          subtitle="Managed in PostgreSQL"
          trend="Week 1 Core"
          icon={Users}
          color="green"
        />
        <StatCard
          title="Tracked Diagnoses"
          value={loading ? '...' : (stats?.total_conditions || 0)}
          subtitle="Medical history records"
          trend="Active"
          icon={Activity}
          color="blue"
        />
        <StatCard
          title="Readmission Model"
          value="XGBoost"
          subtitle="UCI 130-US Hospitals (30-Day)"
          trend="Week 9–10 Ready"
          icon={TrendingUp}
          color="purple"
        />
        <StatCard
          title="Clinical Safety"
          value="Supervised"
          subtitle="Doctor review mandated"
          trend="100% In-Loop"
          icon={ShieldCheck}
          color="amber"
        />
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
        {[
          { to: '/patients', label: 'Patients', hint: 'Live', icon: Users, live: true },
          { label: 'Reports', hint: 'Coming Soon', icon: FileText },
          { label: 'Lab Results', hint: 'Coming Soon', icon: FlaskConical },
          { label: 'Risk Prediction UI', hint: 'Coming Soon · W9', icon: TrendingUp },
          { label: 'AI Assistant', hint: 'Coming Soon', icon: Bot },
        ].map((item) => {
          const Icon = item.icon;
          const live = {
            Patients: { to: '/patients', hint: 'Live' }, Reports: { to: '/reports', hint: 'Live' },
            'Lab Results': { to: '/laboratory', hint: 'Live' }, 'Risk Prediction UI': { to: '/readmission', hint: 'Live' },
            'AI Assistant': { to: '/assistant', hint: 'Live' },
          }[item.label] || item;
          const inner = (
            <div className="med-card p-3 flex items-center space-x-3 hover:border-emerald-300 hover:bg-emerald-50/30 transition-colors">
              <Icon className="w-4 h-4 text-[#0e7c5b]" />
              <div>
                <div className="text-xs font-semibold text-slate-800">{item.label}</div>
                <div className="text-[10px] text-emerald-700">{live.hint}</div>
              </div>
            </div>
          );
          return <Link key={item.label} to={live.to}>{inner}</Link>;
        })}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Recent Patients Table */}
        <div className="lg:col-span-2 med-card p-6">
          <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-100">
            <div>
              <h2 className="text-base font-bold text-slate-800 flex items-center space-x-2">
                <Clock className="w-4 h-4 text-[#0e7c5b]" />
                <span>Recently Admitted Patients</span>
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">Direct clinical records under your supervision</p>
            </div>
            <Link to="/patients" className="text-xs font-semibold text-[#0e7c5b] hover:text-[#0a5c43] flex items-center space-x-1">
              <span>View All</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {loading ? (
            <div className="py-12 text-center text-sm text-slate-400">Loading patient records...</div>
          ) : stats?.recent_patients?.length === 0 ? (
            <div className="py-12 text-center">
              <div className="w-12 h-12 rounded-full bg-emerald-50 text-[#0e7c5b] flex items-center justify-center mx-auto mb-3">
                <Users className="w-6 h-6" />
              </div>
              <p className="text-sm font-medium text-slate-700">No patients recorded yet.</p>
              <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
                Add your first patient to start tracking medical history and testing XGBoost readmission risk predictions.
              </p>
              <Link to="/patients/new" className="mt-4 btn-med-primary text-xs inline-flex items-center space-x-1">
                <UserPlus className="w-3.5 h-3.5" />
                <span>Create Patient Record</span>
              </Link>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="text-slate-400 uppercase tracking-wider border-b border-slate-100">
                    <th className="pb-3 font-semibold">Patient Name</th>
                    <th className="pb-3 font-semibold">Gender</th>
                    <th className="pb-3 font-semibold">DOB</th>
                    <th className="pb-3 font-semibold">Conditions</th>
                    <th className="pb-3 font-semibold text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {stats?.recent_patients?.map((p) => (
                    <tr key={p.id} className="hover:bg-slate-50/70 transition-colors">
                      <td className="py-3 font-medium text-slate-800 flex items-center space-x-2.5">
                        <div className="w-7 h-7 rounded-full bg-emerald-100 text-[#0f4c3a] flex items-center justify-center font-bold text-xs">
                          {p.full_name.charAt(0)}
                        </div>
                        <span className="font-semibold">{p.full_name}</span>
                      </td>
                      <td className="py-3 text-slate-600">{p.gender}</td>
                      <td className="py-3 text-slate-600">{p.date_of_birth || 'N/A'}</td>
                      <td className="py-3">
                        <span className="px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 text-[11px] font-medium">
                          {p.conditions_count} tracked
                        </span>
                      </td>
                      <td className="py-3 text-right">
                        <Link
                          to={`/patients/${p.id}`}
                          className="inline-flex items-center space-x-1 text-[#0e7c5b] hover:text-[#0b6348] font-semibold text-xs bg-emerald-50/60 hover:bg-emerald-100/60 px-2.5 py-1 rounded-md transition-colors"
                        >
                          <span>Open Profile</span>
                          <ChevronRight className="w-3.5 h-3.5" />
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Right 1 Col: AI-CDSS 12-Week Architecture & Pipeline Status */}
        <div className="med-card p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <h2 className="text-base font-bold text-slate-800">System Modules</h2>
              <span className="text-[10px] uppercase font-bold tracking-wider bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full">
                Week 12 Ready
              </span>
            </div>

            <div className="space-y-3 text-xs">
              <div className="p-2.5 rounded-lg bg-emerald-50/80 border border-emerald-200 flex items-start space-x-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5 flex-shrink-0" />
                <div>
                  <div className="font-semibold text-emerald-950">Week 1: Core Foundation & DB</div>
                  <p className="text-emerald-800/90 text-[11px] mt-0.5">
                    FastAPI, JWT Doctor Auth, PostgreSQL Patient Management & UCI XGBoost Readmission baseline.
                  </p>
                </div>
              </div>

              <div className="p-2.5 rounded-lg bg-emerald-50/80 border border-emerald-200 flex items-start space-x-2.5 text-emerald-800">
                <div>
                  <div className="font-semibold text-emerald-950">Week 2-3: OCR & Clinical NLP · Ready</div>
                  <p className="text-[11px] mt-0.5">Tesseract medical report text extraction and entity recognition.</p>
                </div>
              </div>

              <div className="p-2.5 rounded-lg bg-emerald-50/80 border border-emerald-200 flex items-start space-x-2.5 text-emerald-800">
                <div>
                  <div className="font-semibold text-emerald-950">Week 4: Lab Value Engine · Ready</div>
                  <p className="text-[11px] mt-0.5">Rules-based reference range comparison (Normal/High/Low).</p>
                </div>
              </div>

              <div className="p-2.5 rounded-lg bg-emerald-50/80 border border-emerald-200 flex items-start space-x-2.5 text-emerald-800">
                <div>
                  <div className="font-semibold text-emerald-950">Week 5-8: RAG + Clinical Assistant · Ready</div>
                  <p className="text-[11px] mt-0.5">Vector retrieval on curated medical guidelines for clinical Q&A.</p>
                </div>
              </div>

              <div className="p-2.5 rounded-lg bg-emerald-50/80 border border-emerald-200 flex items-start space-x-2.5 text-emerald-800">
                <div>
                  <div className="font-semibold text-emerald-950">Week 9-12: ML, SHAP/XAI & Integration · Ready</div>
                  <p className="text-[11px] mt-0.5">Local & global explainability: "Why this readmission prediction?".</p>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] text-slate-400 text-center">
            Final-Year CSE Project Architecture
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
