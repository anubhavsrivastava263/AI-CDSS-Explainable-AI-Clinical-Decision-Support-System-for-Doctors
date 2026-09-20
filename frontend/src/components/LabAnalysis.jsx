import React, { useEffect, useState } from 'react';
import { FlaskConical, ShieldCheck } from 'lucide-react';
import { patientService } from '../services/api';

const initialForm = { test_name: 'Glucose', value: '', unit: 'mg/dL', test_date: new Date().toISOString().slice(0, 10) };
const statusStyle = {
  Normal: 'bg-emerald-50 text-emerald-800 border-emerald-200',
  'Potentially High': 'bg-amber-50 text-amber-800 border-amber-200',
  'Potentially Low': 'bg-sky-50 text-sky-800 border-sky-200',
};

export default function LabAnalysis({ patientId }) {
  const [results, setResults] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const load = async () => {
    try { setResults((await patientService.listLabResults(patientId)).data || []); }
    catch { setError('Unable to load laboratory results.'); }
  };
  useEffect(() => { load(); }, [patientId]);

  const submit = async (event) => {
    event.preventDefault();
    setError('');
    setSaving(true);
    try {
      await patientService.addLabResult(patientId, { ...form, value: Number(form.value), unit: form.unit || undefined });
      setForm(initialForm);
      await load();
    } catch (err) { setError(err.response?.data?.detail || 'Unable to analyse and save this result.'); }
    finally { setSaving(false); }
  };
  const change = (event) => setForm({ ...form, [event.target.name]: event.target.value });

  return <section className="med-card p-5">
    <div className="flex items-start justify-between gap-3 border-b border-slate-100 pb-3">
      <div className="flex items-center gap-2"><FlaskConical className="w-4 h-4 text-[#0e7c5b]" /><h2 className="text-sm font-bold text-slate-800">Laboratory Analysis</h2></div>
      <span className="text-[10px] bg-emerald-50 text-emerald-800 border border-emerald-200 px-2 py-0.5 rounded">Week 4 ready</span>
    </div>
    <p className="mt-3 text-xs text-slate-600">Enter a clinician-reviewed result. The configured rule only flags a value as Normal, Potentially High, or Potentially Low; it is not a diagnosis.</p>
    <form onSubmit={submit} className="mt-3 grid grid-cols-1 sm:grid-cols-4 gap-2">
      <input name="test_name" value={form.test_name} onChange={change} className="input-med text-xs" placeholder="Test (e.g. HbA1c)" required />
      <input name="value" type="number" step="any" value={form.value} onChange={change} className="input-med text-xs" placeholder="Result" required />
      <input name="unit" value={form.unit} onChange={change} className="input-med text-xs" placeholder="Unit" />
      <div className="flex gap-2"><input name="test_date" type="date" value={form.test_date} onChange={change} className="input-med text-xs min-w-0" /><button disabled={saving} className="btn-med-primary text-xs px-3 whitespace-nowrap">{saving ? 'Checking…' : 'Analyse'}</button></div>
    </form>
    <p className="mt-2 text-[10px] text-slate-400">Supported: HbA1c, Glucose, Hemoglobin, WBC, Platelets, Creatinine, Urea, Sodium, Potassium, Cholesterol, LDL, HDL, Triglycerides, TSH.</p>
    {error && <p className="mt-2 text-xs text-rose-700">{error}</p>}
    <div className="mt-4 space-y-2">
      {!results.length ? <p className="text-xs text-slate-400">No clinician-reviewed laboratory results saved.</p> : results.map((result) => <div key={result.id} className="rounded-lg border border-slate-100 p-3 text-xs">
        <div className="flex items-center justify-between gap-2"><span className="font-semibold text-slate-800">{result.test_name}: {result.value} {result.unit}</span><span className={`border rounded-full px-2 py-0.5 font-semibold ${statusStyle[result.status] || 'bg-slate-50 text-slate-700 border-slate-200'}`}>{result.status}</span></div>
        <p className="mt-1 text-slate-500">Reference: {result.reference_range}. {result.clinical_basis}</p>
        <p className="mt-1 flex items-center gap-1 text-slate-400"><ShieldCheck className="w-3 h-3" /> Doctor review required{result.test_date ? ` · Test date: ${result.test_date}` : ''}</p>
      </div>)}</div>
  </section>;
}
