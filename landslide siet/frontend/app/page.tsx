export default function HomePage() {
  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <section className="mx-auto max-w-6xl px-6 py-20">
        <div className="mb-8 flex items-center justify-between border-b border-slate-200 pb-6">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">LandSense</p>
            <h1 className="mt-2 text-4xl font-bold tracking-tight">Know your area. Stay one step ahead.</h1>
          </div>
          <div className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700">
            Status: Demo mode
          </div>
        </div>

        <div className="grid gap-8 md:grid-cols-[1.4fr_0.8fr]">
          <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
            <p className="text-sm font-medium uppercase tracking-[0.2em] text-slate-500">Search your area</p>
            <div className="mt-6 rounded-xl border border-slate-200 bg-slate-50 p-4 text-slate-700">
              Village, town, district, pincode, or landmark search
            </div>
            <div className="mt-6 flex flex-wrap gap-3">
              <button className="rounded-xl bg-brand-700 px-5 py-3 text-sm font-semibold text-white">Check Area Risk →</button>
              <button className="rounded-xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700">Rescue Hub</button>
            </div>
          </div>

          <aside className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <p className="text-sm font-medium uppercase tracking-[0.2em] text-slate-500">Current risk</p>
            <div className="mt-4 flex items-end justify-between">
              <div>
                <div className="text-4xl font-bold">68</div>
                <div className="text-sm text-slate-500">/ 100</div>
              </div>
              <span className="rounded-full bg-orange-100 px-3 py-1 text-sm font-semibold text-orange-700">HIGH</span>
            </div>
            <ul className="mt-6 space-y-3 text-sm text-slate-700">
              <li>Rainfall: 42 mm</li>
              <li>Soil moisture: 68%</li>
              <li>Wind: 18 km/h</li>
              <li>Elevation: 480 m</li>
              <li>Last updated: 4 min ago</li>
            </ul>
          </aside>
        </div>
      </section>
    </main>
  );
}
