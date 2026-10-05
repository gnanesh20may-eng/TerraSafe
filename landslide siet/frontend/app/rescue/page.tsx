'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { MapPinned, RadioTower, RotateCcw, Smartphone, Users, Wifi, WifiOff } from 'lucide-react';
import { RiskMap } from '@/components/risk-map';

const rescueCenter: [number, number] = [76.8, 11.35];
const relayStages = [
  'SOS created on Asha’s phone (no signal)',
  'Message relayed to Ravi’s phone (signal available)',
  'Rescue team receives the message on its map',
];

export default function RescueSimulationPage() {
  const [relayStep, setRelayStep] = useState(3);
  const [isRunning, setIsRunning] = useState(false);

  useEffect(() => {
    if (!isRunning) return;
    const interval = window.setInterval(() => {
      setRelayStep((current) => {
        if (current >= relayStages.length) {
          window.clearInterval(interval);
          setIsRunning(false);
          return current;
        }
        return current + 1;
      });
    }, 900);
    return () => window.clearInterval(interval);
  }, [isRunning]);

  function replaySimulation() {
    setRelayStep(0);
    setIsRunning(true);
  }

  return (
    <main className="min-h-screen bg-slate-50 px-5 py-8 text-slate-900 md:px-8">
      <div className="mx-auto max-w-6xl">
        <header className="mb-8 flex flex-wrap items-center justify-between gap-4 border-b border-slate-200 pb-5">
          <div>
            <Link href="/" className="text-sm font-semibold text-slate-600">TerraSafe</Link>
            <h1 className="mt-2 text-3xl font-bold">Rescue relay</h1>
          </div>
          <span className="rounded-md border border-amber-300 bg-amber-50 px-3 py-1.5 text-sm font-semibold text-amber-900">Simulation</span>
        </header>

        <div className="mb-6 flex flex-wrap items-center justify-between gap-4 border-b border-slate-200 pb-5">
          <p className="max-w-2xl text-sm leading-6 text-slate-600">
            Demonstration only. No Bluetooth, radio, or device-to-device network connection is made.
          </p>
          <button type="button" onClick={replaySimulation} className="inline-flex items-center gap-2 rounded-md bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white">
            <RotateCcw className="h-4 w-4" /> Replay relay
          </button>
        </div>

        <section aria-label="Simulated devices" className="grid gap-3 md:grid-cols-3">
          <article className="rounded-lg border border-slate-200 bg-white p-4">
            <div className="flex items-center justify-between">
              <Smartphone className="h-5 w-5 text-rose-700" />
              <span className="inline-flex items-center gap-1 text-xs font-semibold text-rose-800"><WifiOff className="h-4 w-4" /> No signal</span>
            </div>
            <h2 className="mt-3 font-semibold">Asha’s phone</h2>
            <p className="mt-1 text-sm text-slate-600">SOS waiting to relay</p>
          </article>
          <article className="rounded-lg border border-slate-200 bg-white p-4">
            <div className="flex items-center justify-between">
              <Smartphone className="h-5 w-5 text-emerald-700" />
              <span className="inline-flex items-center gap-1 text-xs font-semibold text-emerald-800"><Wifi className="h-4 w-4" /> Signal</span>
            </div>
            <h2 className="mt-3 font-semibold">Ravi’s phone</h2>
            <p className="mt-1 text-sm text-slate-600">Nearby relay device</p>
          </article>
          <article className="rounded-lg border border-slate-200 bg-white p-4">
            <div className="flex items-center justify-between">
              <RadioTower className="h-5 w-5 text-sky-800" />
              <span className="inline-flex items-center gap-1 text-xs font-semibold text-sky-900"><Wifi className="h-4 w-4" /> Online</span>
            </div>
            <h2 className="mt-3 font-semibold">Rescue team</h2>
            <p className="mt-1 text-sm text-slate-600">Map endpoint</p>
          </article>
        </section>

        <div className="mt-6 grid gap-6 lg:grid-cols-[1.35fr_0.65fr]">
          <section className="rounded-lg border border-slate-200 bg-white p-5">
            <div className="flex items-center gap-2">
              <MapPinned className="h-5 w-5 text-slate-700" />
              <h2 className="font-semibold">Relay path</h2>
            </div>
            <ol className="mt-5 space-y-3" aria-live="polite">
              {relayStages.map((stage, index) => (
                <li key={stage} className={`flex items-center gap-3 rounded-md border p-3 text-sm ${relayStep >= index + 1 ? 'border-emerald-300 bg-emerald-50 text-emerald-950' : 'border-slate-200 bg-slate-50 text-slate-500'}`}>
                  <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full border border-current text-xs font-bold">{index + 1}</span>
                  {stage}
                </li>
              ))}
            </ol>
            <div className="mt-5 overflow-hidden rounded-md border border-slate-200">
              <div className="flex items-center justify-between border-b border-slate-200 px-3 py-2 text-sm">
                <span className="font-semibold">Rescue team map</span>
                <span className="text-slate-500">{relayStep === relayStages.length ? 'SOS received' : 'Awaiting simulated relay'}</span>
              </div>
              <RiskMap center={rescueCenter} selectedName="Simulated SOS · Coonoor" />
            </div>
          </section>

          <aside className="rounded-lg border border-slate-200 bg-white p-5">
            <div className="flex items-center gap-2">
              <Users className="h-5 w-5 text-slate-700" />
              <h2 className="font-semibold">Linked family</h2>
            </div>
            <ul className="mt-4 divide-y divide-slate-200">
              <li className="py-3"><p className="font-medium">Asha</p><p className="mt-1 text-sm text-rose-800">No signal · SOS queued</p></li>
              <li className="py-3"><p className="font-medium">Ravi</p><p className="mt-1 text-sm text-emerald-800">Signal · Relay device</p></li>
              <li className="py-3"><p className="font-medium">Meena</p><p className="mt-1 text-sm text-slate-600">Last seen · 10:42</p></li>
            </ul>
            <p className="mt-4 border-t border-slate-200 pt-4 text-xs leading-5 text-slate-500">Device states and family links are illustrative simulation data.</p>
          </aside>
        </div>
      </div>
    </main>
  );
}