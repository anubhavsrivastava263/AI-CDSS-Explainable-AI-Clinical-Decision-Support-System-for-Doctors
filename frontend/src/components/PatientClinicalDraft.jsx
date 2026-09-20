import React, { useState } from 'react';
import { Bot, FileText } from 'lucide-react';
import api from '../services/api';

export default function PatientClinicalDraft({ patientId }) {
  const [data, setData] = useState(null), [loading, setLoading] = useState(false), [error, setError] = useState('');
  const create = async () => { setLoading(true); setError(''); try { setData((await api.get(`/assistant/patients/${patientId}/draft`)).data); } catch (e) { setError(e.response?.data?.detail || 'Unable to create the clinical draft.'); } finally { setLoading(false); } };
  return <section className="med-card p-5"><div className="flex items-center justify-between gap-3 border-b border-slate-100 pb-3"><div className="flex items-center gap-2"><Bot className="w-4 h-4 text-[#0e7c5b]" /><div><h2 className="text-sm font-bold text-slate-800">AI Clinical Summary</h2><p className="text-[11px] text-slate-500">Draft compiled from this patient’s stored records</p></div></div><span className="text-[10px] bg-emerald-50 text-emerald-800 border border-emerald-200 px-2 py-0.5 rounded">Week 11</span></div><button onClick={create} disabled={loading} className="mt-4 btn-med-primary text-xs flex items-center gap-1.5"><FileText className="w-3.5 h-3.5" />{loading ? 'Creating draft…' : 'Create draft for review'}</button>{error && <p className="mt-3 text-xs text-rose-700">{error}</p>}{data && <><pre className="mt-4 whitespace-pre-wrap font-sans text-xs leading-relaxed text-slate-700 rounded-lg bg-slate-50 border border-slate-100 p-3">{data.draft}</pre><p className="mt-2 text-[11px] text-amber-800">{data.disclaimer}</p></>}</section>;
}
