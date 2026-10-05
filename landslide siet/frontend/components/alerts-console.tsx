'use client';

import { FormEvent, useEffect, useState } from 'react';

const API_BASE = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');
type AlertItem = { id: string; location_id: string; risk_level: string; message: string; lifecycle_state: string; created_at: string; events: Array<{ sequence: number; to_state: string; detail: string; created_at: string }> };

export function AlertsConsole() {
  const [items, setItems] = useState<AlertItem[]>([]);
  const [token, setToken] = useState('');
  const [location, setLocation] = useState('coonor');
  const [level, setLevel] = useState('WATCH');
  const [message, setMessage] = useState('');
  const [notice, setNotice] = useState('');
  const [error, setError] = useState('');
  async function refresh() {
    try {
      const response = await fetch(`${API_BASE}/api/v1/alerts`, { cache: 'no-store' });
      if (!response.ok) throw new Error(`Alert history returned HTTP ${response.status}`);
      const payload = await response.json();
      setItems(payload.items || []);
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Alert history unavailable.'); }
  }
  useEffect(() => { void refresh(); }, []);

  async function createAlert(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(''); setNotice('');
    try {
      const response = await fetch(`${API_BASE}/api/v1/alerts`, {
        method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ location_id: location, risk_level: level, message }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || `Create returned HTTP ${response.status}`);
      setMessage(''); setNotice('Alert created. It has not been approved or sent.'); await refresh();
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Alert could not be created.'); }
  }

  async function transition(id: string, state: string) {
    setError(''); setNotice('');
    try {
      const response = await fetch(`${API_BASE}/api/v1/alerts/${id}/lifecycle`, {
        method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ state, detail: state === 'SENT' ? 'UI mock action; no external dispatch' : '' }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || `Transition returned HTTP ${response.status}`);
      setNotice(state === 'SENT' ? 'Recorded MOCK SENT state. No message was dispatched.' : `Alert moved to ${state}.`);
      await refresh();
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Alert transition failed.'); }
  }

  return <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
    <p className="text-xs font-bold uppercase tracking-[0.12em] text-emerald-900">Authority console · requires a role token</p>
    <h1 className="mt-2 text-3xl font-bold">Alert history</h1>
    <p className="mt-2 text-sm text-slate-600">New alerts are not warnings. External delivery adapters are not configured; SENT below is a simulation state.</p>
    <label htmlFor="authority-token" className="mt-5 block text-sm font-semibold">Short-lived authority token</label>
    <input id="authority-token" type="password" autoComplete="off" value={token} onChange={(event) => setToken(event.target.value)} placeholder="Paste token for this session only" className="mt-1 min-h-11 w-full max-w-2xl border border-slate-300 bg-white px-3 text-sm" />
    <form onSubmit={createAlert} className="mt-5 grid gap-3 border border-slate-200 bg-white p-4 md:grid-cols-[1fr_150px_2fr_auto]">
      <label className="text-xs font-semibold">Location<select value={location} onChange={(event) => setLocation(event.target.value)} className="mt-1 block min-h-10 w-full border border-slate-300 px-2 text-sm"><option value="coonor">Coonoor (DEMO)</option><option value="ooty">Ooty (DEMO)</option><option value="kodaikanal">Kodaikanal (DEMO)</option></select></label>
      <label className="text-xs font-semibold">Risk<select value={level} onChange={(event) => setLevel(event.target.value)} className="mt-1 block min-h-10 w-full border border-slate-300 px-2 text-sm"><option>WATCH</option><option>HIGH</option><option>CRITICAL</option><option>LOW</option></select></label>
      <label className="text-xs font-semibold">Message<input value={message} onChange={(event) => setMessage(event.target.value)} required maxLength={1000} className="mt-1 block min-h-10 w-full border border-slate-300 px-2 text-sm" /></label>
      <button disabled={!token} className="self-end min-h-10 bg-slate-900 px-4 text-sm font-semibold text-white disabled:bg-slate-400">Create draft</button>
    </form>
    {notice && <p role="status" className="mt-3 border-l-4 border-emerald-700 bg-emerald-50 px-3 py-2 text-sm">{notice}</p>}
    {error && <p role="alert" className="mt-3 border-l-4 border-red-700 bg-red-50 px-3 py-2 text-sm text-red-900">{error}</p>}
    <div className="mt-6 divide-y divide-slate-200 border-y border-slate-200 bg-white">
      {items.length === 0 && <p className="p-5 text-sm text-slate-600">No persisted alerts yet.</p>}
      {items.map((item) => <article key={item.id} className="grid gap-3 p-4 lg:grid-cols-[1fr_auto]">
        <div><div className="flex flex-wrap items-center gap-2"><h2 className="font-bold">{item.risk_level} · {item.location_id}</h2><span className="border border-slate-300 px-2 py-1 text-xs font-bold">{item.lifecycle_state}</span></div><p className="mt-1 text-sm text-slate-700">{item.message}</p><p className="mt-1 text-xs text-slate-500">Created {new Date(item.created_at).toLocaleString()}</p><ol className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-600">{item.events.map((entry) => <li key={entry.sequence}>{entry.sequence}. {entry.to_state} · {entry.detail}</li>)}</ol></div>
        <div className="flex flex-wrap items-start gap-2">{item.lifecycle_state === 'CREATED' && <button disabled={!token} onClick={() => transition(item.id, 'APPROVED')} className="min-h-9 border border-slate-300 px-3 text-xs font-semibold disabled:opacity-50">Approve</button>}{item.lifecycle_state === 'APPROVED' && <button disabled={!token} onClick={() => transition(item.id, 'SENT')} className="min-h-9 border border-amber-600 px-3 text-xs font-semibold text-amber-950 disabled:opacity-50">Simulate send</button>}{['SENT', 'DELIVERED'].includes(item.lifecycle_state) && <button disabled={!token} onClick={() => transition(item.id, 'ACKNOWLEDGED')} className="min-h-9 border border-slate-300 px-3 text-xs font-semibold disabled:opacity-50">Acknowledge</button>}{item.lifecycle_state !== 'RESOLVED' && <button disabled={!token} onClick={() => transition(item.id, 'RESOLVED')} className="min-h-9 border border-slate-300 px-3 text-xs font-semibold disabled:opacity-50">Resolve</button>}</div>
      </article>)}
    </div>
  </div>;
}
