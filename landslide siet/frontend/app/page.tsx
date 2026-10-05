import Link from 'next/link';
import { LocationSearch } from '@/components/location-search';

export default function HomePage() {
  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white/90 backdrop-blur-sm">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-900 text-sm font-bold text-white">L</div>
            <div>
              <p className="text-sm font-semibold tracking-[0.2em] text-slate-500 uppercase">TerraSafe</p>
            </div>
          </div>

          <nav className="hidden items-center gap-6 text-sm font-medium text-slate-600 md:flex">
            <Link href="/">Home</Link>
            <Link href="/evaluation">Evaluation</Link>
            <Link href="/rescue">Rescue Hub</Link>
            <Link href="/alerts">Alerts</Link>
            <Link href="/settings">Settings</Link>
          </nav>

          <div className="rounded-full border border-slate-200 bg-slate-100 px-3 py-1.5 text-xs font-medium text-slate-700">
            Terrain and satellite: DEMO
          </div>
        </div>
      </header>

      <section className="mx-auto max-w-6xl px-6 py-10 md:py-16">
        <div className="mb-8 max-w-2xl">
          <p className="text-sm font-medium uppercase tracking-[0.2em] text-slate-500">Decision support</p>
          <h1 className="mt-3 text-4xl font-bold tracking-tight text-slate-900 md:text-5xl">Know your area.<br />Stay one step ahead.</h1>
          <p className="mt-4 text-lg text-slate-600">
            Real-time terrain, rainfall, and environmental signals are combined to support safer decisions in at-risk areas.
          </p>
          <p className="mt-3 border-l-2 border-amber-500 pl-3 text-sm leading-6 text-slate-600">
            Decision support only. Not a replacement for official IMD, NDMA, or GSI warnings or emergency instructions.
          </p>
        </div>

        <div className="mb-8 rounded-3xl border border-slate-200 bg-white p-4 shadow-sm md:p-6">
          <div className="flex flex-col gap-4 md:flex-row md:items-center">
            <div className="flex-1">
              <div className="text-sm font-medium uppercase tracking-[0.2em] text-slate-500">Search your area</div>
              <div className="mt-2 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-700">
                Village, town, district, pincode, landmark, or map selection
              </div>
            </div>
            <div className="flex gap-3">
              <button className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white">Check Area Risk →</button>
              <button className="rounded-xl border border-slate-200 px-5 py-3 text-sm font-semibold text-slate-700">Rescue Hub</button>
            </div>
          </div>
        </div>

        <div className="grid gap-8 lg:grid-cols-[1.4fr_0.8fr]">
          <div className="rounded-3xl border border-slate-200 bg-white p-4 shadow-sm md:p-6">
            <LocationSearch />
          </div>

          <aside className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-sm font-medium uppercase tracking-[0.2em] text-slate-500">AI risk summary</p>
            <div className="mt-4 flex items-end justify-between">
              <div>
                <div className="text-4xl font-bold text-slate-900">68</div>
                <div className="text-sm text-slate-500">/ 100</div>
              </div>
              <span className="rounded-full bg-orange-100 px-3 py-1 text-sm font-semibold text-orange-700">HIGH</span>
            </div>

            <ul className="mt-6 space-y-3 text-sm text-slate-700">
              <li>Rainfall: 42 mm</li>
              <li>Soil Moisture: 68%</li>
              <li>Wind: 18 km/h</li>
              <li>Elevation: 520 m</li>
              <li>Last Updated: 4 mins ago</li>
              <li>Data freshness: live demo feed</li>
            </ul>
          </aside>
        </div>
      </section>
    </main>
  );
}
