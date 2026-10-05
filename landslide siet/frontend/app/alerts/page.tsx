import Link from 'next/link';

export default function RescueHubPage() {
  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-slate-100">
      <div className="mx-auto max-w-6xl">
        <header className="mb-8 flex items-center justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Emergency</p>
            <h1 className="mt-2 text-3xl font-bold text-white">Rescue Hub</h1>
          </div>
          <Link href="/" className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-2 text-sm font-medium text-slate-100">
            Home
          </Link>
        </header>

        <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="space-y-6">
            <div className="rounded-3xl border border-slate-800 bg-slate-900 p-6">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Current Location</p>
              <div className="mt-4 flex items-center justify-between">
                <div>
                  <div className="text-xl font-semibold text-white">Coonoor</div>
                  <div className="text-sm text-slate-400">Nilgiris District</div>
                </div>
                <div className="rounded-full bg-red-500/20 px-3 py-1 text-sm font-semibold text-red-300">HIGH RISK</div>
              </div>
              <div className="mt-6 h-56 rounded-2xl border border-slate-700 bg-gradient-to-br from-slate-800 to-slate-700" />
            </div>

            <div className="rounded-3xl border border-slate-800 bg-slate-900 p-6">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Safe Zone</p>
              <div className="mt-4 space-y-3 text-sm text-slate-200">
                <div className="flex justify-between"><span>Town Relief Center</span><span>2.8 km</span></div>
                <div className="flex justify-between"><span>District Control Hub</span><span>6.1 km</span></div>
              </div>
            </div>
          </div>

          <aside className="space-y-6">
            <div className="rounded-3xl border border-slate-800 bg-slate-900 p-6">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Emergency Contacts</p>
              <ul className="mt-4 space-y-3 text-sm text-slate-200">
                <li>District Control Room: +91-00000-00000</li>
                <li>Fire Service: +91-00000-00001</li>
                <li>Local Relief Desk: +91-00000-00002</li>
              </ul>
            </div>

            <div className="rounded-3xl border border-slate-800 bg-slate-900 p-6">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Recommended Route</p>
              <p className="mt-4 text-sm leading-6 text-slate-200">Follow the safest practical route away from steep, saturated terrain and toward the designated relief center.</p>
            </div>

            <button className="w-full rounded-2xl bg-red-600 px-5 py-4 text-lg font-semibold text-white shadow-lg shadow-red-900/40">
              GET HELP
            </button>
          </aside>
        </div>
      </div>
    </main>
  );
}
