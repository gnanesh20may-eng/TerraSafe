'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { AlertTriangle, LocateFixed, Search, ShieldCheck, Wind, Droplets, Mountain, Clock3 } from 'lucide-react';
import { demoLocations, getRiskLabel, riskColors, type LocationOption, type RiskLevel } from '@/lib/utils';
import { RiskMap } from '@/components/risk-map';

type RiskPayload = {
  location: { name: string; latitude: number; longitude: number; admin_region: string };
  risk: { score: number; level: RiskLevel; trend: string; model_status?: string };
  confidence: { available: boolean; value?: number | null; reason?: string };
  environment: Record<string, number | string | null>;
  terrain: Record<string, number | string | null>;
  recommendation: { severity: string; message: string };
  timestamp: string;
  data_status?: string;
};

type SourceState = 'loading' | 'live' | 'demo' | 'mixed' | 'offline' | 'stale';
const API_BASE = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');

function formatObserved(value: unknown) {
  if (!value || typeof value !== 'string') return 'Unavailable';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? 'Unavailable' : date.toLocaleString();
}

export function DashboardConsole() {
  const [selected, setSelected] = useState<LocationOption>(demoLocations[0]);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<LocationOption[]>(demoLocations);
  const [risk, setRisk] = useState<RiskPayload | null>(null);
  const [sourceState, setSourceState] = useState<SourceState>('loading');
  const [error, setError] = useState('');
  const [showRiskZones, setShowRiskZones] = useState(true);
  const [showShelters, setShowShelters] = useState(true);
  const [period, setPeriod] = useState(0);
  const [scenarioRain, setScenarioRain] = useState(40);
  const [scenario, setScenario] = useState<{ baseline: { score: number; level: string }; scenario: { score: number; level: string } } | null>(null);
  const [scenarioError, setScenarioError] = useState('');

  useEffect(() => {
    const controller = new AbortController();
    setRisk(null);
    setSourceState('loading');
    setError('');
    Promise.all([
      fetch(`${API_BASE}/api/v1/risk/${selected.id}`, { cache: 'no-store', signal: controller.signal }).then(async (response) => {
        if (!response.ok) throw new Error(`Risk service returned HTTP ${response.status}`);
        return response.json() as Promise<RiskPayload>;
      }),
      fetch(`${API_BASE}/api/v1/environment/${selected.id}`, { cache: 'no-store', signal: controller.signal }).then(async (response) => {
        if (!response.ok) throw new Error(`Environmental data returned HTTP ${response.status}`);
        return response.json();
      }),
    ]).then(([riskPayload, environment]) => {
      const merged = { ...riskPayload, data_status: environment.data_status };
      setRisk(merged);
      const status = String(environment.data_status || '').toUpperCase();
      setSourceState(status.includes('MIXED') ? 'mixed' : status.includes('DEMO') ? 'demo' : 'live');
    }).catch((reason: unknown) => {
      if (controller.signal.aborted) return;
      setRisk(null);
      setSourceState('offline');
      setError(reason instanceof Error ? reason.message : 'Risk information is unavailable.');
    });
    return () => controller.abort();
  }, [selected.id]);

  async function searchLocations(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!query.trim()) {
      setResults(demoLocations);
      return;
    }
    try {
      const response = await fetch(`${API_BASE}/api/v1/locations/search?q=${encodeURIComponent(query.trim())}`, { cache: 'no-store' });
      if (!response.ok) throw new Error('Location search is unavailable.');
      const payload = await response.json();
      setResults((payload.results || []).map((location: { id: string; name: string; admin_region?: string; latitude: number; longitude: number; risk_level?: string }) => ({
        id: location.id, name: location.name, region: location.admin_region || 'Administrative area not supplied',
        latitude: location.latitude, longitude: location.longitude,
        riskLevel: (location.risk_level || 'WATCH') as RiskLevel, score: 0,
      })));
    } catch {
      setResults([]);
      setError('Location service unavailable. The local catalogue is not a geocoder.');
    }
  }

  function useCurrentLocation() {
    if (!navigator.geolocation) {
      setError('Location permission is not available in this browser.');
      return;
    }
    navigator.geolocation.getCurrentPosition((position) => {
      const location: LocationOption = {
        id: `coordinates-${position.coords.latitude.toFixed(3)}-${position.coords.longitude.toFixed(3)}`,
        name: 'Selected coordinates', region: 'Administrative region unavailable',
        latitude: position.coords.latitude, longitude: position.coords.longitude,
        riskLevel: 'WATCH', score: 0,
      };
      setSelected(location);
      setError('');
    }, () => setError('Location permission was denied or unavailable.'), { enableHighAccuracy: false, timeout: 8000, maximumAge: 60000 });
  }

  async function runScenario() {
    setScenarioError('');
    try {
      const response = await fetch(`${API_BASE}/api/v1/simulate`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ location_id: selected.id, rainfall_24h_mm: scenarioRain }),
      });
      if (!response.ok) throw new Error(`Scenario service returned HTTP ${response.status}`);
      setScenario(await response.json());
    } catch (reason) {
      setScenario(null);
      setScenarioError(reason instanceof Error ? reason.message : 'Scenario service unavailable.');
    }
  }

  const score = risk?.risk.score;
  const level = risk?.risk.level || selected.riskLevel || (score === undefined ? 'WATCH' : getRiskLabel(score));
  const tone = riskColors[level];
  const ageMinutes = risk ? Math.max(0, Math.floor((Date.now() - new Date(risk.timestamp).getTime()) / 60000)) : null;
  const stale = ageMinutes !== null && ageMinutes > 15;

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <section className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:py-9">
        <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
          <div className="max-w-2xl">
            <p className="text-xs font-bold uppercase tracking-[0.12em] text-emerald-900">Nilgiris monitoring desk · decision support</p>
            <h1 className="mt-2 text-3xl font-bold text-slate-950">Know your area. Stay one step ahead.</h1>
            <p className="mt-2 max-w-xl text-sm leading-6 text-slate-600">Conditions and terrain indicators support local awareness. Risk scores are not deterministic predictions or official warnings.</p>
          </div>
          <Link href="/rescue-hub" className="flex min-h-12 items-center bg-red-800 px-5 text-sm font-bold text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-800">GET HELP</Link>
        </div>

        <form onSubmit={searchLocations} className="mb-5 flex flex-col gap-2 sm:flex-row">
          <label htmlFor="area-search" className="sr-only">Search village, town, district, pincode, or landmark</label>
          <div className="flex min-h-12 flex-1 items-center gap-2 border border-slate-300 bg-white px-3">
            <Search size={18} className="text-slate-500" aria-hidden="true" />
            <input id="area-search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search village, town, district or pincode" className="w-full bg-transparent text-sm outline-none" />
          </div>
          <button className="min-h-12 bg-emerald-900 px-5 text-sm font-semibold text-white">Search area</button>
          <button type="button" onClick={useCurrentLocation} className="flex min-h-12 items-center justify-center gap-2 border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-800"><LocateFixed size={17} aria-hidden="true" /> Use my location</button>
        </form>
        <div className="mb-5 flex flex-wrap gap-2" aria-label="Search results">
          {results.length === 0 ? <p className="text-sm text-slate-600">No matching catalogue location. Search coverage is limited.</p> : results.map((item) => <button type="button" key={item.id} onClick={() => setSelected(item)} aria-pressed={item.id === selected.id} className={`min-h-10 border px-3 text-sm ${item.id === selected.id ? 'border-emerald-900 bg-emerald-900 text-white' : 'border-slate-300 bg-white text-slate-800'}`}>{item.name}<span className="ml-2 text-xs opacity-75">{item.region}</span></button>)}
        </div>

        <div className="mb-4 flex flex-wrap items-center gap-3 border-y border-slate-200 py-3 text-xs text-slate-700">
          <span className={`font-bold ${sourceState === 'offline' ? 'text-red-800' : sourceState === 'live' ? 'text-emerald-800' : 'text-amber-900'}`}>{sourceState === 'loading' ? 'CHECKING SOURCES' : sourceState === 'offline' ? 'OFFLINE / UNAVAILABLE' : sourceState === 'live' ? 'LIVE DATA' : sourceState === 'mixed' ? 'MIXED LIVE + DEMO' : 'DEMO DATA'}</span>
          <span>Area: {selected.name} · {selected.latitude.toFixed(4)}, {selected.longitude.toFixed(4)}</span>
          <span>{risk ? `Assessment fetched ${ageMinutes} min ago` : 'Assessment not available'}</span>
          {stale && <span className="font-bold text-red-800">Data may be outdated</span>}
          {risk?.confidence?.available === false && <span>Model confidence: unavailable</span>}
        </div>
        {error && <p role="alert" className="mb-4 border-l-4 border-red-700 bg-red-50 px-4 py-3 text-sm text-red-900">{error}</p>}

        <div className="grid gap-5 xl:grid-cols-[minmax(0,1.7fr)_minmax(300px,0.8fr)]">
          <section aria-label="Risk map and layers" className="min-w-0 border border-slate-200 bg-white">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 px-4 py-3">
              <div><h2 className="font-semibold text-slate-900">Risk map</h2><p className="text-xs text-slate-600">Selected location · MapLibre demo basemap</p></div>
              <span className="border border-amber-400 bg-amber-50 px-2 py-1 text-xs font-bold text-amber-950">RISK ZONES: DEMO GIS</span>
            </div>
            <RiskMap center={[selected.longitude, selected.latitude]} selectedName={selected.name} showRiskZones={showRiskZones} showShelters={showShelters} />
            <div className="grid gap-3 border-t border-slate-200 p-4 sm:grid-cols-2">
              <label className="flex min-h-10 items-center gap-2 text-sm"><input type="checkbox" checked={showRiskZones} onChange={(event) => setShowRiskZones(event.target.checked)} /> Susceptibility zones <span className="text-xs font-bold text-amber-900">DEMO</span></label>
              <label className="flex min-h-10 items-center gap-2 text-sm"><input type="checkbox" checked={showShelters} onChange={(event) => setShowShelters(event.target.checked)} /> Shelter markers <span className="text-xs font-bold text-amber-900">DEMO</span></label>
              <span className="text-sm text-slate-500">Rainfall raster <strong className="text-slate-700">MISSING</strong></span>
              <span className="text-sm text-slate-500">Inventory / road hazards <strong className="text-slate-700">MISSING</strong></span>
            </div>
          </section>

          <aside className="min-w-0 border border-slate-200 bg-white" aria-label="Risk assessment">
            <div className="border-b border-slate-200 p-4">
              <p className="text-xs font-bold uppercase tracking-[0.1em] text-slate-600">Current risk · DEMO heuristic</p>
              {risk ? <div className="mt-3 flex items-end justify-between gap-3"><div><span className="text-5xl font-bold tabular-nums text-slate-950">{risk.risk.score}</span><span className="ml-1 text-sm text-slate-500">/ 100</span></div><span className="border px-3 py-2 text-sm font-extrabold" style={{ borderColor: tone, color: tone }}>{risk.risk.level} RISK</span></div> : <p className="mt-4 text-sm text-slate-600">{sourceState === 'loading' ? 'Loading assessment…' : 'No current assessment available.'}</p>}
              {risk?.risk.model_status && <p className="mt-2 text-xs text-slate-600">{risk.risk.model_status}</p>}
            </div>
            <div className="divide-y divide-slate-100 px-4">
              <Signal icon={<Droplets size={17} />} name="Rainfall · 24h" value={risk?.environment.rainfall_24h_mm} unit="mm" />
              <Signal icon={<Droplets size={17} />} name="Soil moisture" value={risk?.environment.soil_moisture_pct} unit="%" />
              <Signal icon={<Wind size={17} />} name="Wind speed" value={risk?.environment.wind_speed_kmh} unit="km/h" />
              <Signal icon={<Mountain size={17} />} name="Elevation" value={risk?.terrain.elevation_m} unit="m" />
              <Signal icon={<Mountain size={17} />} name="Slope" value={risk?.terrain.slope_deg} unit="°" />
            </div>
            <div className="border-t border-slate-200 p-4">
              <p className="text-sm font-semibold">Recommended action</p>
              <p className="mt-1 text-sm leading-5 text-slate-700">{risk?.recommendation.message || 'Risk guidance is unavailable while the service is offline.'}</p>
              <p className="mt-2 text-xs font-semibold text-slate-600">Follow official IMD, NDMA, GSI and local-authority instructions.</p>
              <Link href="/evaluation" className="mt-4 inline-flex min-h-10 items-center border border-slate-300 px-3 text-sm font-semibold text-slate-900">Open evaluation</Link>
            </div>
          </aside>
        </div>

        <div className="mt-5 grid gap-5 lg:grid-cols-2">
          <section className="border border-slate-200 bg-white p-4">
            <div className="flex items-start justify-between gap-3"><div><h2 className="font-semibold">Observation window</h2><p className="mt-1 text-xs text-slate-600">Historical storage and forecast API are not connected.</p></div><span className="text-xs font-bold text-slate-700">MISSING</span></div>
            <label className="mt-4 block text-sm text-slate-700" htmlFor="period-slider">Time selection (disabled until time series are available)</label>
            <input id="period-slider" className="mt-2 w-full" type="range" min="0" max="10" value={period} onChange={(event) => setPeriod(Number(event.target.value))} disabled aria-valuetext="No time-series observations available" />
            <div className="flex justify-between text-xs text-slate-500"><span>7 days ago</span><span>Now</span><span>+3 days</span></div>
          </section>
          <section className="border border-slate-200 bg-white p-4">
            <div className="flex items-start justify-between gap-3"><div><h2 className="font-semibold">What-if rainfall</h2><p className="mt-1 text-xs text-slate-600">Runs the DEMO weighted heuristic; not a forecast.</p></div><span className="text-xs font-bold text-amber-900">SIMULATED</span></div>
            <label htmlFor="scenario-rain" className="mt-4 block text-sm">Hypothetical 24-hour rainfall: {scenarioRain} mm</label>
            <input id="scenario-rain" className="mt-2 w-full" type="range" min="0" max="200" step="5" value={scenarioRain} onChange={(event) => setScenarioRain(Number(event.target.value))} />
            <button type="button" onClick={runScenario} className="mt-3 min-h-10 bg-slate-900 px-4 text-sm font-semibold text-white">Run demonstration scenario</button>
            {scenario && <p className="mt-3 text-sm">Demo score: {scenario.baseline.score} → {scenario.scenario.score} · {scenario.baseline.level} → {scenario.scenario.level}</p>}
            {scenarioError && <p role="alert" className="mt-3 text-sm text-red-800">{scenarioError}</p>}
          </section>
        </div>
        <p className="mt-6 flex items-start gap-2 text-xs leading-5 text-slate-600"><AlertTriangle size={15} className="mt-0.5 shrink-0" />TerraSafe is decision support, not a replacement for official warnings. Sample shelters, terrain, and risk-zone polygons are DEMO data. Do not rely on this interface alone for evacuation decisions.</p>
      </section>
    </main>
  );
}

function Signal({ icon, name, value, unit }: { icon: React.ReactNode; name: string; value: unknown; unit: string }) {
  const available = typeof value === 'number' && Number.isFinite(value);
  return <div className="flex min-h-12 items-center justify-between gap-3 py-2 text-sm"><span className="flex items-center gap-2 text-slate-700">{icon}{name}</span><span className="font-semibold tabular-nums text-slate-900">{available ? `${value} ${unit}` : 'Unavailable'}</span></div>;
}
