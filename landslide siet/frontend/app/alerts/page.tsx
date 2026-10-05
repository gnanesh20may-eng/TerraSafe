import { AlertsConsole } from '@/components/alerts-console';
import { SiteHeader } from '@/components/site-header';

export default function AlertsPage() {
  return <><SiteHeader /><main className="min-h-screen bg-slate-50"><AlertsConsole /></main></>;
}
