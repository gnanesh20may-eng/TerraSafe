'use client';

import { useState } from 'react';
import Link from 'next/link';
import { SiteHeader } from '@/components/site-header';
import { RiskMap } from '@/components/risk-map';

const API_BASE = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');

type RouteInfo = { status: string; destination: { name: string; type: string }; straight_line_distance_km: number; route: unknown; route_provider: string; disclaimer: string };

export default function RescueHubPage() {
  const [coords, setCoords] = useState<[number, number]>([76.8, 11.35]);
  const [locationStatus, setLocationStatus] = useState('DEMO default location · Coonoor');
  const [route, setRoute] = useState<RouteInfo | null>(null);
  const [notice, setNotice] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  function useLocation() {
    if (!navigator.geolocation) { setError('Browser location is unavailable.'); return; }
    navigator.geolocation.getCurrentPosition((position) => {
      setCoords([position.coords.longitude, position.coords.latitude]);
      setLocationStatus('CURRENT LOCATION · obtained after your permission');
      setError('');
    }, () => setError('Location was denied or unavailable. The DEMO location remains selected.'), { enableHighAccuracy: false, timeout: 8000, maximumAge: 60000 });
  }

  async function getRoute() {
    setBusy(true); setError(''); setRoute(null);
    try {
      const response = await fetch(`${API_BASE}/api/v1/rescue/route?latitude=${coords[1]}&longitude=${coords[0]}`, { cache: 'no-store' });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || `Route service returned HTTP ${response.status}`);
      setRoute(payload);
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Route service unavailable.'); }
    finally { setBusy(false); }
  }

  async function sendSos() {
    setBusy(true); setError(''); setNotice('');
    try {
      const response = await fetch(`${API_BASE}/sos`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: 'Emergency assistance request from TerraSafe Rescue Hub', latitude: coords[1], longitude: coords[0] }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || `SOS service returned HTTP ${response.status}`);
      setNotice(`Request ${payload.id} was recorded locally. No emergency service or contact was notified.`);
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'SOS request could not be recorded.'); }
    finally { setBusy(false); }
  }

  return <><SiteHeader /><main className="min-h-screen bg-slate-950 text-slate-100">
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6">
      <div className="flex flex-wrap items-end justify-between gap-4 border-b border-slate-700 pb-4"><div><p className="text-xs font-bold uppercase tracking-[0.12em] text-red-300">Rescue assistance · SIMULATION</p><h1 className="mt-1 text-3xl font-bold">Rescue Hub</h1></div><Link href="/" className="min-h-10 border border-slate-600 px-3 py-2 text-sm">Back to monitoring</Link></div>
      <div className="mt-4 border-l-4 border-red-500 bg-red-950/60 p-4 text-sm leading-6 text-red-100">DEMO only. SOS requests are stored for this prototype but do not dispatch emergency services. Do not use sample shelter points or this route for real evacuation decisions.</div>
      <div className="mt-5 grid gap-5 xl:grid-cols-[minmax(0,1.6fr)_minmax(290px,0.7fr)]">
        <section className="min-w-0 border border-slate-700 bg-slate-900">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-700 p-4"><div><p className="text-xs font-bold">CURRENT LOCATION</p><p className="mt-1 text-sm text-slate-300">{locationStatus} · {coords[1].toFixed(4)}, {coords[0].toFixed(4)}</p></div><button type="button" onClick={useLocation} className="min-h-10 border border-slate-600 px-3 text-sm">Use current location</button></div>
          <RiskMap center={coords} selectedName={locationStatus.startsWith('DEMO') ? 'Coonoor (DEMO)' : 'Current location'} showRiskZones showShelters />
          <div className="border-t border-slate-700 p-4"><p className="text-sm font-bold">Map data</p><p className="mt-1 text-xs text-slate-300">Basemap: demo tiles · risk polygons: DEMO GIS · shelter locations: DEMO / unverified · road hazards: MISSING</p></div>
        </section>
        <aside className="space-y-5">
          <section className="border border-slate-700 bg-slate-900 p-4"><p className="text-xs font-bold uppercase tracking-[0.1em] text-slate-300">Current risk</p><p className="mt-2 text-xl font-bold">Risk service status is shown on the <Link href="/" className="underline">monitoring desk</Link></p><p className="mt-2 text-xs text-slate-400">Risk is decision support only. Follow official local guidance.</p></section>
          <section className="border border-slate-700 bg-slate-900 p-4"><h2 className="font-bold">Nearby safe locations</h2><p className="mt-1 text-xs text-amber-200">DEMO markers · not authority verified</p><button type="button" disabled={busy} onClick={getRoute} className="mt-3 min-h-11 w-full bg-slate-100 px-3 text-sm font-semibold text-slate-950 disabled:opacity-50">{busy ? 'Checking…' : 'Find nearest demo location'}</button>
            {route && <div className="mt-3 border-t border-slate-700 pt-3 text-sm"><p className="font-semibold">{route.destination.name}</p><p>{route.straight_line_distance_km} km straight-line · {route.status}</p><p className="mt-1 text-xs text-slate-400">{route.route_provider}</p></div>}
          </section>
          <section className="border border-slate-700 bg-slate-900 p-4"><h2 className="font-bold">Emergency contacts</h2><p className="mt-2 text-sm text-slate-300">Verified district contacts are not configured in this build.</p><p className="mt-2 text-xs text-slate-400">Use emergency numbers published by your local authorities. No sample phone numbers are shown.</p></section>
          {notice && <p role="status" className="border-l-4 border-emerald-400 bg-emerald-950 p-3 text-sm text-emerald-100">{notice}</p>}
          {error && <p role="alert" className="border-l-4 border-red-400 bg-red-950 p-3 text-sm text-red-100">{error}</p>}
          <button type="button" disabled={busy} onClick={sendSos} className="min-h-16 w-full bg-red-700 px-4 text-lg font-bold text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white disabled:opacity-50">{busy ? 'PROCESSING…' : 'GET HELP · RECORD DEMO SOS'}</button>
          <p className="text-xs leading-5 text-slate-400">This button records a prototype request in the local database. It does not send SMS, WhatsApp, email, voice, or push alerts.</p>
        </aside>
      </div>
    </div>
  </main></>;
}
