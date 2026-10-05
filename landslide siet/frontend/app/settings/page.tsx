import Link from 'next/link';

export default function AlertsPage() {
  return (
    <main className="min-h-screen bg-slate-50 px-6 py-10 text-slate-900">
      <div className="mx-auto max-w-4xl">
        <header className="mb-8 flex items-center justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Alerts</p>
            <h1 className="mt-2 text-3xl font-bold">Alert history</h1>
          </div>
          <Link href="/" className="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700">
            Back to home
          </Link>
        </header>

        <div className="space-y-4">
          <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold">Coonoor – HIGH</p>
                <p className="mt-1 text-sm text-slate-600">Elevated rainfall and soil moisture in monitored area.</p>
              </div>
              <span className="rounded-full bg-orange-100 px-3 py-1 text-xs font-semibold text-orange-700">NEW</span>
            </div>
          </div>

          <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold">Ooty – WATCH</p>
                <p className="mt-1 text-sm text-slate-600">Conditions are elevated but still manageable with monitoring.</p>
              </div>
              <span className="rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-700">ACKNOWLEDGED</span>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
