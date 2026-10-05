import Link from 'next/link';

export default function EvaluationPage() {
  return (
    <main className="min-h-screen bg-slate-50 px-6 py-10 text-slate-900">
      <div className="mx-auto max-w-6xl">
        <header className="mb-8 flex items-center justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Evaluation</p>
            <h1 className="mt-2 text-3xl font-bold">Selected area analysis</h1>
          </div>
          <Link href="/" className="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700">
            Back to home
          </Link>
        </header>

        <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <section className="space-y-6">
            <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-sm font-medium uppercase tracking-[0.2em] text-slate-500">Selected Area</h2>
              <div className="mt-4 grid gap-4 md:grid-cols-2">
                <div><p className="text-slate-500">Location</p><p className="mt-1 text-lg font-semibold">Coonoor</p></div>
                <div><p className="text-slate-500">Administrative region</p><p className="mt-1 text-lg font-semibold">Nilgiris District</p></div>
                <div><p className="text-slate-500">Latitude</p><p className="mt-1 text-lg font-semibold">11.35° N</p></div>
                <div><p className="text-slate-500">Longitude</p><p className="mt-1 text-lg font-semibold">76.80° E</p></div>
                <div><p className="text-slate-500">Elevation</p><p className="mt-1 text-lg font-semibold">520 m</p></div>
                <div><p className="text-slate-500">Last updated</p><p className="mt-1 text-lg font-semibold">4 minutes ago</p></div>
              </div>
            </div>

            <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-sm font-medium uppercase tracking-[0.2em] text-slate-500">Environmental Signals</h2>
              <div className="mt-5 grid gap-4 sm:grid-cols-2">
                <div className="rounded-2xl bg-slate-50 p-4"><p className="text-slate-500">Rainfall</p><p className="mt-2 text-xl font-semibold">42 mm</p></div>
                <div className="rounded-2xl bg-slate-50 p-4"><p className="text-slate-500">Soil Moisture</p><p className="mt-2 text-xl font-semibold">68%</p></div>
                <div className="rounded-2xl bg-slate-50 p-4"><p className="text-slate-500">Wind</p><p className="mt-2 text-xl font-semibold">18 km/h</p></div>
                <div className="rounded-2xl bg-slate-50 p-4"><p className="text-slate-500">Temperature</p><p className="mt-2 text-xl font-semibold">23.4°C</p></div>
                <div className="rounded-2xl bg-slate-50 p-4"><p className="text-slate-500">Elevation</p><p className="mt-2 text-xl font-semibold">520 m</p></div>
                <div className="rounded-2xl bg-slate-50 p-4"><p className="text-slate-500">Slope</p><p className="mt-2 text-xl font-semibold">27°</p></div>
                <div className="rounded-2xl bg-slate-50 p-4"><p className="text-slate-500">Vegetation</p><p className="mt-2 text-xl font-semibold">Moderate</p></div>
                <div className="rounded-2xl bg-slate-50 p-4"><p className="text-slate-500">Recent rainfall accumulation</p><p className="mt-2 text-xl font-semibold">156 mm</p></div>
              </div>
            </div>
          </section>

          <aside className="space-y-6">
            <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-sm font-medium uppercase tracking-[0.2em] text-slate-500">Risk Analysis</h2>
              <div className="mt-5 flex items-end justify-between">
                <div>
                  <div className="text-5xl font-bold">68</div>
                  <div className="text-sm text-slate-500">/ 100</div>
                </div>
                <span className="rounded-full bg-orange-100 px-3 py-1 text-sm font-semibold text-orange-700">HIGH</span>
              </div>

              <div className="mt-6 space-y-4 text-sm text-slate-700">
                <div className="flex justify-between"><span>Risk level</span><span className="font-semibold">HIGH</span></div>
                <div className="flex justify-between"><span>Confidence</span><span className="font-semibold">Moderate</span></div>
                <div className="flex justify-between"><span>Trend</span><span className="font-semibold">Increasing</span></div>
              </div>
            </div>

            <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-sm font-medium uppercase tracking-[0.2em] text-slate-500">AI Explanation</h2>
              <ol className="mt-5 space-y-3 text-sm text-slate-700">
                <li>1. High 24-hour rainfall ↑</li>
                <li>2. Elevated soil moisture ↑</li>
                <li>3. Steep terrain ↑</li>
                <li>4. Recent rainfall accumulation ↑</li>
              </ol>
            </div>

            <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-sm font-medium uppercase tracking-[0.2em] text-slate-500">Recommended Action</h2>
              <p className="mt-4 text-sm leading-6 text-slate-700">
                Risk is elevated. Avoid unnecessary travel through steep or vulnerable areas and monitor official emergency instructions.
              </p>
            </div>
          </aside>
        </div>
      </div>
    </main>
  );
}
