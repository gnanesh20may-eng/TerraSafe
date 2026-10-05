"use client";

import { useEffect, useState } from 'react';
import { MapPin, Search, ShieldAlert, Trees, Wind, Gauge, Droplets } from 'lucide-react';
import { demoLocations, getRiskLabel, riskColors } from '@/lib/utils';
import { RiskMap } from '@/components/risk-map';

export function LocationSearch() {
  const [query, setQuery] = useState('');
  const [selected, setSelected] = useState(demoLocations[0]);
  const [riskSnapshot, setRiskSnapshot] = useState({
    score: demoLocations[0].score,
    rainfall24h: 42,
    soilMoisture: 68,
    source: 'demo',
  });
  const [sosConfirmation, setSosConfirmation] = useState('');
  const [sendingSos, setSendingSos] = useState(false);
  const [locationMessage, setLocationMessage] = useState('');

  useEffect(() => {
    const controller = new AbortController();
    const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

    const riskUrl = selected.id === 'current-location'
      ? `${apiBase}/api/v1/risk?latitude=${selected.latitude}&longitude=${selected.longitude}&name=${encodeURIComponent(selected.name)}`
      : `${apiBase}/api/v1/risk/${selected.id}`;

    fetch(riskUrl, { signal: controller.signal })
      .then((response) => {
        if (!response.ok) throw new Error('Risk request failed');
        return response.json();
      })
      .then((result) => {
        setRiskSnapshot({
          score: result.risk.score,
          rainfall24h: result.environment.rainfall_24h_mm,
          soilMoisture: result.environment.soil_moisture_pct,
          source: result.environment.source === 'open-meteo' ? 'open-meteo' : 'demo',
        });
      })
      .catch(() => {
        if (!controller.signal.aborted) {
          setRiskSnapshot((current) => ({ ...current, source: 'demo' }));
        }
      });

    return () => controller.abort();
  }, [selected]);

  const filtered = demoLocations.filter((item) => {
    const text = `${item.name} ${item.region}`.toLowerCase();
    return text.includes(query.toLowerCase());
  });

  const riskLevel = getRiskLabel(selected.score);

  async function sendSos() {
    setSendingSos(true);
    setSosConfirmation('');
    const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';
    try {
      const response = await fetch(`${apiBase}/sos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          lat: selected.latitude,
          lon: selected.longitude,
          name: 'Dashboard user',
          timestamp: new Date().toISOString(),
        }),
      });
      if (!response.ok) throw new Error('SOS request failed');
      const event = await response.json();
      setSosConfirmation(`SOS received: ${event.id}`);
    } catch {
      setSosConfirmation('SOS could not be sent. Check the backend connection.');
    } finally {
      setSendingSos(false);
    }
  }

  function useCurrentLocation() {
    setLocationMessage('');
    if (!navigator.geolocation) {
      setLocationMessage('Location is not available in this browser.');
      return;
    }

    navigator.geolocation.getCurrentPosition(
      ({ coords }) => {
        setSelected({
          id: 'current-location',
          name: 'Current location',
          region: 'Device location',
          latitude: coords.latitude,
          longitude: coords.longitude,
          riskLevel: 'WATCH',
          score: riskSnapshot.score,
        });
        setLocationMessage('Location loaded. Risk is being checked for these coordinates.');
      },
      () => setLocationMessage('Location permission was denied or the position is unavailable.'),
      { enableHighAccuracy: false, timeout: 10000, maximumAge: 60000 },
    );
  }

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="flex items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2">
          <Search className="h-4 w-4 text-slate-500" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search your area"
            className="w-full border-0 bg-transparent text-sm outline-none placeholder:text-slate-400"
            aria-label="Search location"
          />
        </div>

        <div className="mt-3 flex flex-wrap gap-2">
          {filtered.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => setSelected(item)}
              className={`rounded-full border px-3 py-2 text-sm font-medium ${
                selected.id === item.id ? 'border-slate-900 bg-slate-900 text-white' : 'border-slate-200 bg-white text-slate-700'
              }`}
            >
              {item.name}
            </button>
          ))}
        </div>
        <button type="button" onClick={useCurrentLocation} className="mt-3 inline-flex items-center gap-2 rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700">
          <MapPin className="h-4 w-4" /> Use current location
        </button>
        {locationMessage && <p role="status" className="mt-2 text-sm text-slate-600">{locationMessage}</p>}
      </div>

      <div className="grid gap-5 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Selected area</p>
              <h2 className="mt-2 text-2xl font-semibold text-slate-900">{selected.name}</h2>
            </div>
            <span className="rounded-full px-3 py-1 text-xs font-semibold text-white" style={{ backgroundColor: riskColors[riskLevel] }}>
              {riskLevel}
            </span>
          </div>

          <div className="mb-4 flex items-center gap-2 text-sm text-slate-600">
            <MapPin className="h-4 w-4" />
            {selected.region} · {selected.latitude}, {selected.longitude}
          </div>

          <RiskMap center={[selected.longitude, selected.latitude]} selectedName={selected.name} />
        </div>

        <aside className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Current risk</p>
          <div className="mt-4 flex items-end justify-between">
            <div>
              <div className="text-4xl font-bold text-slate-900">{riskSnapshot.score}</div>
              <div className="text-sm text-slate-500">/ 100</div>
            </div>
            <div className="flex flex-col items-end gap-2">
              <span className="rounded-full px-3 py-1 text-sm font-semibold text-white" style={{ backgroundColor: riskColors[getRiskLabel(riskSnapshot.score)] }}>
                {getRiskLabel(riskSnapshot.score)}
              </span>
              <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${riskSnapshot.source === 'open-meteo' ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-700'}`}>
                {riskSnapshot.source === 'open-meteo' ? 'Live' : 'Demo'}
              </span>
            </div>
          </div>

          <div className="mt-6 space-y-3 text-sm text-slate-700">
            <div className="flex items-center gap-2"><Droplets className="h-4 w-4 text-sky-700" /> Rainfall: {Number(riskSnapshot.rainfall24h).toFixed(1)} mm</div>
            <div className="flex items-center gap-2"><Gauge className="h-4 w-4 text-emerald-700" /> Soil moisture: {Number(riskSnapshot.soilMoisture).toFixed(1)}%</div>
            <div className="flex items-center gap-2"><Wind className="h-4 w-4 text-violet-700" /> Wind: 18 km/h</div>
            <div className="flex items-center gap-2"><Trees className="h-4 w-4 text-lime-700" /> Vegetation: healthy</div>
            <div className="flex items-center gap-2"><ShieldAlert className="h-4 w-4 text-amber-700" /> Last updated: 4 minutes ago</div>
          </div>

          <div className="mt-6 flex gap-3">
            <button className="flex-1 rounded-xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white">Check Area Risk →</button>
            <button onClick={sendSos} disabled={sendingSos} className="rounded-xl bg-rose-700 px-4 py-3 text-sm font-semibold text-white disabled:opacity-60">
              {sendingSos ? 'Sending…' : 'Send SOS'}
            </button>
          </div>
          {sosConfirmation && <p role="status" className="mt-3 text-sm text-slate-700">{sosConfirmation}</p>}
        </aside>
      </div>
    </div>
  );
}
