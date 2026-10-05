'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { SiteHeader } from '@/components/site-header';
import { demoLocations, riskColors, type LocationOption, type RiskLevel } from '@/lib/utils';

const API_BASE = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');
type Evaluation = { location: { name: string; latitude: number; longitude: number; admin_region?: string }; risk: { score: number; level: RiskLevel; trend: string; model_status?: string }; confidence: { available: boolean; reason?: string }; environment: Record<string, unknown>; terrain: Record<string, unknown>; contributors: Array<{ factor: string; impact: string; direction: string }>; recommendation: { message: string }; timestamp: string };

export default function EvaluationPage() {
  const [selected, setSelected] = useState<LocationOption>(demoLocations[0]);
  const [result, setResult] = useState<Evaluation | null>(null);
  const [error, setError] = useState('');
  useEffect(() => {
    const controller = new AbortController();
    setResult(null); setError('');
    fetch(`${API_BASE}/api/v1/risk/${selected.id}`, { cache: 'no-store', signal: controller.signal })
      .then(async (response) => { if (!response.ok) throw new Error(`Risk evaluation returned HTTP ${response.status}`); return response.json(); })
      .then(setResult)
      .catch((reason: unknown) => { if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : 'Risk evaluation unavailable.'); });
    return () => controller.abort();
  }, [selected.id]);
  const tone = result ? riskColors[result.risk.level] : '#475569';
  return <><SiteHeader /><main className="mx-auto min-h-screen max-w-6xl px-4 py-8 sm:px-6">
    <p className="text-xs font-bold uppercase tracking-[0.12em] text-emerald-900">Risk evaluation · decision support</p><h1 className="mt-2 text-3xl font-bold">Area assessment</h1>
    <label htmlFor="evaluation-location" className="mt-5 block text-sm font-semibold">Selected area</label>
    <select id="evaluation-location" value={selected.id} onChange={(event) => setSelected(demoLocations.find((item) => item.id === event.target.value) || demoLocations[0])} className="mt-1 min-h-11 w-full max-w-sm border border-slate-300 bg-white px-3">{demoLocations.map((item) => <option key={item.id} value={item.id}>{item.name} · {item.region} (DEMO catalogue)</option>)}</select>
    {error && <p role="alert" className="mt-4 border-l-4 border-red-700 bg-red-50 p-3 text-sm text-red-900">{error}</p>}
    {!result && !error && <p className="mt-5 text-sm text-slate-600">Loading assessment…</p>}
    {result && <>
      <div className="mt-5 grid gap-5 lg:grid-cols-[1fr_0.85fr]">
        <section className="border border-slate-200 bg-white p-5">
          <div className="flex flex-wrap items-start justify-between gap-3"><div><h2 className="text-xl font-bold">{result.location.name}</h2><p className="mt-1 text-sm text-slate-600">{result.location.admin_region || 'Administrative region unavailable'} · {result.location.latitude.toFixed(4)}, {result.location.longitude.toFixed(4)}</p></div><span className="border px-3 py-2 text-sm font-bold" style={{ borderColor: tone, color: tone }}>{result.risk.level} RISK</span></div>
          <div className="mt-7 flex items-end gap-2"><span className="text-6xl font-bold tabular-nums">{result.risk.score}</span><span className="pb-2 text-slate-500">/ 100 · {result.risk.model_status || 'DEMO'}</span></div>
          <div className="mt-4 grid gap-x-7 border-t border-slate-200 pt-3 sm:grid-cols-2">{[['24-hour rainfall',result.environment.rainfall_24h_mm,'mm'],['7-day rainfall',result.environment.rainfall_7d_mm,'mm'],['Soil moisture',result.environment.soil_moisture_pct,'%'],['Wind',result.environment.wind_speed_kmh,'km/h'],['Temperature',result.environment.temperature_c,'°C'],['Elevation',result.terrain.elevation_m,'m'],['Slope',result.terrain.slope_deg,'°'],['Vegetation index',result.terrain.ndvi,'']].map(([label,value,unit]) => <div key={String(label)} className="flex min-h-11 items-center justify-between border-b border-slate-100 text-sm"><span className="text-slate-700">{String(label)}</span><strong>{typeof value === 'number' ? `${value} ${String(unit)}` : 'Unavailable'}</strong></div>)}</div>
          <p className="mt-3 text-xs text-slate-600">Response timestamp: {new Date(result.timestamp).toLocaleString()}</p>
        </section>
        <aside className="space-y-5">
          <section className="border border-slate-200 bg-white p-5"><h2 className="font-bold">Why this score?</h2><p className="mt-1 text-xs text-slate-600">Heuristic contributors are indicators, not causal findings.</p><ol className="mt-4 divide-y divide-slate-100">{result.contributors.map((item,index) => <li key={`${item.factor}-${index}`} className="flex justify-between gap-3 py-3 text-sm"><span>{item.factor}</span><span className="font-semibold">{item.impact} · {item.direction}</span></li>)}</ol><p className="mt-3 text-xs font-semibold text-slate-700">Confidence: {result.confidence.available ? 'reported by model' : 'Unavailable; no calibrated uncertainty model'}.</p></section>
          <section className="border border-slate-200 bg-white p-5"><h2 className="font-bold">Trend</h2><p className="mt-2 text-sm">{result.risk.trend}</p><p className="mt-1 text-xs text-slate-600">Historical prediction series: MISSING. Trend is a demo rule, not derived from stored model history.</p></section>
          <section className="border-l-4 border-amber-600 bg-amber-50 p-5"><h2 className="font-bold">Recommended action</h2><p className="mt-2 text-sm leading-6">{result.recommendation.message}</p><p className="mt-2 text-xs">Follow official IMD, NDMA, GSI and local-authority instructions.</p></section>
        </aside>
      </div>
      <Link href="/rescue-hub" className="mt-5 inline-flex min-h-11 items-center bg-red-800 px-4 font-bold text-white">Open Rescue Hub</Link>
    </>}
  </main></>;
}
