'use client';

import { useEffect, useState } from 'react';
import { SiteHeader } from '@/components/site-header';

const API_BASE = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');
type Metrics = { status: string; metrics: unknown; message?: string };

export default function TransparencyPage() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  useEffect(() => {
    const controller = new AbortController();
    fetch(`${API_BASE}/api/v1/models/metrics`, { cache: 'no-store', signal: controller.signal })
      .then((response) => response.json())
      .then(setMetrics)
      .catch(() => { if (!controller.signal.aborted) setMetrics({ status: 'UNAVAILABLE', metrics: null, message: 'Metrics endpoint unavailable.' }); });
    return () => controller.abort();
  }, []);
  return <><SiteHeader /><main className="mx-auto min-h-screen max-w-5xl px-4 py-8 sm:px-6">
    <p className="text-xs font-bold uppercase tracking-[0.12em] text-emerald-900">Public accountability</p>
    <h1 className="mt-2 text-3xl font-bold">System transparency</h1>
    <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-700">TerraSafe is a prototype decision-support tool. It is not a landslide-warning authority and cannot confirm that an event will or will not occur.</p>
    <section className="mt-7 border border-slate-200 bg-white p-5">
      <div className="flex flex-wrap items-baseline justify-between gap-3"><h2 className="text-lg font-bold">Model performance</h2><span className="text-sm font-bold">{metrics?.status || 'CHECKING'}</span></div>
      <p className="mt-2 text-sm text-slate-700">No independently validated real-event model metrics are available in this deployment.</p>
      {metrics?.message && <p className="mt-2 text-sm text-slate-600">{metrics.message}</p>}
      {Boolean(metrics?.metrics) && <pre className="mt-4 max-h-80 overflow-auto bg-slate-950 p-4 text-xs text-white">{JSON.stringify(metrics?.metrics, null, 2)}</pre>}
    </section>
    <section className="mt-5 border border-slate-200 bg-white p-5">
      <h2 className="text-lg font-bold">What is in use</h2>
      <dl className="mt-4 divide-y divide-slate-200 text-sm">
        <StatusRow name="Risk calculation" status="DEMO" detail="Weighted heuristic using demo terrain and environmental inputs; not a validated model." />
        <StatusRow name="Weather history" status="LIVE SOURCE / REANALYSIS" detail="One small Open-Meteo ERA5-Land response was retrieved for Nilgiris. Reanalysis is modeled, not a local gauge." />
        <StatusRow name="Earthquake context" status="LIVE SOURCE / EMPTY RESULT" detail="USGS query completed with no matching events in the bounded window and magnitude filter." />
        <StatusRow name="Terrain / satellite" status="DEMO" detail="Elevation, slope, vegetation and satellite observations are not live products in this build." />
        <StatusRow name="Colab model notebooks" status="SCAFFOLD / NOT RUN" detail="Notebooks are authored but have no executed cells or exported validated model." />
        <StatusRow name="Rescue contacts / shelters" status="DEMO / UNVERIFIED" detail="Do not rely on sample locations for emergency navigation. No invented emergency numbers are provided here." />
      </dl>
    </section>
    <section className="mt-5 border-l-4 border-red-700 bg-red-50 p-5 text-sm leading-6 text-red-950">
      <h2 className="font-bold">Emergency guidance</h2>
      <p className="mt-1">This platform does not replace official IMD, NDMA, GSI, or local-authority warnings. Follow instructions issued by local authorities and emergency services.</p>
    </section>
  </main></>;
}

function StatusRow({ name, status, detail }: { name: string; status: string; detail: string }) {
  return <div className="grid gap-1 py-3 sm:grid-cols-[190px_180px_1fr]"><dt className="font-semibold">{name}</dt><dd className="font-bold text-slate-800">{status}</dd><dd className="text-slate-600">{detail}</dd></div>;
}
