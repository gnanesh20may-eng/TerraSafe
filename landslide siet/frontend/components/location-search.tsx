"use client";

import { useState } from 'react';
import { MapPin, Search, ShieldAlert, Trees, Wind, Gauge, Droplets } from 'lucide-react';
import { demoLocations, getRiskLabel, riskColors } from '@/lib/utils';
import { RiskMap } from '@/components/risk-map';

export function LocationSearch() {
  const [query, setQuery] = useState('');
  const [selected, setSelected] = useState(demoLocations[0]);

  const filtered = demoLocations.filter((item) => {
    const text = `${item.name} ${item.region}`.toLowerCase();
    return text.includes(query.toLowerCase());
  });

  const riskLevel = getRiskLabel(selected.score);

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
              <div className="text-4xl font-bold text-slate-900">{selected.score}</div>
              <div className="text-sm text-slate-500">/ 100</div>
            </div>
            <span className="rounded-full px-3 py-1 text-sm font-semibold text-white" style={{ backgroundColor: riskColors[riskLevel] }}>
              {riskLevel}
            </span>
          </div>

          <div className="mt-6 space-y-3 text-sm text-slate-700">
            <div className="flex items-center gap-2"><Droplets className="h-4 w-4 text-sky-700" /> Rainfall: 42 mm</div>
            <div className="flex items-center gap-2"><Gauge className="h-4 w-4 text-emerald-700" /> Soil moisture: 68%</div>
            <div className="flex items-center gap-2"><Wind className="h-4 w-4 text-violet-700" /> Wind: 18 km/h</div>
            <div className="flex items-center gap-2"><Trees className="h-4 w-4 text-lime-700" /> Vegetation: healthy</div>
            <div className="flex items-center gap-2"><ShieldAlert className="h-4 w-4 text-amber-700" /> Last updated: 4 minutes ago</div>
          </div>

          <div className="mt-6 flex gap-3">
            <button className="flex-1 rounded-xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white">Check Area Risk →</button>
            <button className="rounded-xl border border-slate-200 px-4 py-3 text-sm font-semibold text-slate-700">Rescue Hub</button>
          </div>
        </aside>
      </div>
    </div>
  );
}
