'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { SiteHeader } from '@/components/site-header';

const API_BASE = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');
type Source = { id: string; name: string; category?: string; status: string; latency_ms?: number | null; record_count?: number | null; newest_timestamp?: string | null; error?: string | null };
type Report = { updated_at?: string | null; region?: string; sources?: Source[]; summary?: Record<string, number>; status?: string; message?: string };

export default function DataSourcesPage() {
  const [report, setReport] = useState<Report | null>(null);
  const [error, setError] = useState('');
  useEffect(() => {
    const controller = new AbortController();
    fetch(`${API_BASE}/api/v1/health/data-sources`, { cache: 'no-store', signal: controller.signal })
      .then(async (response) => { if (!response.ok) throw new Error(`Source health returned HTTP ${response.status}`); return response.json(); })
      .then(setReport)
      .catch((reason: unknown) => { if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : 'Source report unavailable.'); });
    return () => controller.abort();
  }, []);
  return <><SiteHeader /><main className="mx-auto min-h-screen max-w-7xl px-4 py-8 sm:px-6">
    <p className="text-xs font-bold uppercase tracking-[0.12em] text-emerald-900">Provenance register</p>
    <h1 className="mt-2 text-3xl font-bold">Data sources</h1>
    <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">A successful connection check only means the endpoint responded. It does not establish scientific suitability, event completeness, or suitability for warnings.</p>
    <div className="mt-5 flex flex-wrap gap-3 border-y border-slate-200 py-3 text-sm">
      {Object.entries(report?.summary || {}).map(([key, value]) => <span key={key} className="font-semibold">{key}: {value}</span>)}
      <span className="ml-auto text-slate-600">Updated: {report?.updated_at ? new Date(report.updated_at).toLocaleString() : 'Not checked'}</span>
    </div>
    {error && <p role="alert" className="mt-4 border-l-4 border-red-700 bg-red-50 p-3 text-sm text-red-900">{error}</p>}
    {!report && !error && <p className="mt-6 text-sm text-slate-600">Loading source report…</p>}
    {report?.message && <p className="mt-6 border border-amber-300 bg-amber-50 p-4 text-sm text-amber-950">{report.message}</p>}
    <div className="mt-5 overflow-x-auto border border-slate-200 bg-white">
      <table className="w-full min-w-[760px] border-collapse text-left text-sm">
        <thead className="bg-slate-100 text-xs uppercase text-slate-700"><tr><th className="p-3">Source</th><th className="p-3">Status</th><th className="p-3">Latency</th><th className="p-3">Records</th><th className="p-3">Newest observation</th><th className="p-3">Note</th></tr></thead>
        <tbody>{(report?.sources || []).map((source) => <tr key={source.id} className="border-t border-slate-200 align-top"><th scope="row" className="p-3 font-semibold">{source.name}<span className="mt-1 block text-xs font-normal text-slate-500">{source.id}</span></th><td className="p-3 font-bold">{source.status}</td><td className="p-3">{source.latency_ms == null ? '—' : `${source.latency_ms} ms`}</td><td className="p-3">{source.record_count == null ? '—' : source.record_count}</td><td className="p-3">{source.newest_timestamp || '—'}</td><td className="max-w-sm p-3 text-xs text-slate-600">{source.error || 'Response check succeeded; content remains source-specific.'}</td></tr>)}</tbody>
      </table>
    </div>
    <div className="mt-6 border-l-4 border-amber-600 bg-amber-50 p-4 text-sm leading-6 text-amber-950">Open-Meteo is modeled reanalysis, not a local rain gauge. USGS returned zero matching events for the checked query window. Terrain, satellite and sample shelter layers remain DEMO. See <Link className="underline" href="/transparency">system transparency</Link> and <Link className="underline" href="/">the dashboard</Link>.</div>
  </main></>;
}
