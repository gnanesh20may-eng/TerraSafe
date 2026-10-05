'use client';

import Link from 'next/link';
import { useState } from 'react';
import { Menu, ShieldAlert, X } from 'lucide-react';

const links = [
  { href: '/', en: 'Overview', ta: 'கண்ணோட்டம்' },
  { href: '/evaluation', en: 'Evaluation', ta: 'மதிப்பீடு' },
  { href: '/rescue-hub', en: 'Rescue Hub', ta: 'மீட்பு மையம்' },
  { href: '/alerts', en: 'Alerts', ta: 'எச்சரிக்கைகள்' },
  { href: '/data-sources', en: 'Data sources', ta: 'தரவு மூலங்கள்' },
  { href: '/transparency', en: 'Transparency', ta: 'வெளிப்படைத்தன்மை' },
  { href: '/settings', en: 'Settings', ta: 'அமைப்புகள்' },
] as const;

export function SiteHeader() {
  const [language, setLanguage] = useState<'en' | 'ta'>('en');
  const [menuOpen, setMenuOpen] = useState(false);
  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
        <Link href="/" className="flex shrink-0 items-center gap-2 text-slate-900" aria-label="TerraSafe home">
          <span className="flex h-9 w-9 items-center justify-center bg-emerald-800 text-white"><ShieldAlert size={19} aria-hidden="true" /></span>
          <span className="text-sm font-bold uppercase tracking-[0.12em]">TerraSafe</span>
        </Link>
        <nav aria-label="Primary navigation" className="hidden items-center gap-4 lg:flex">
          {links.map((link) => <Link key={link.href} href={link.href} className="text-sm text-slate-700 underline-offset-4 hover:text-emerald-900 hover:underline">{language === 'en' ? link.en : link.ta}</Link>)}
        </nav>
        <div className="flex items-center gap-2">
          <button type="button" onClick={() => setLanguage(language === 'en' ? 'ta' : 'en')} className="min-h-10 border border-slate-300 px-3 text-sm font-semibold text-slate-800 focus-visible:outline focus-visible:outline-2 focus-visible:outline-emerald-700" aria-label="Change language">
            {language === 'en' ? 'தமிழ்' : 'English'}
          </button>
          <Link href="/rescue-hub" className="hidden min-h-10 items-center bg-red-800 px-3 text-sm font-bold text-white sm:flex">GET HELP</Link>
          <button type="button" onClick={() => setMenuOpen(!menuOpen)} className="flex h-10 w-10 items-center justify-center border border-slate-300 lg:hidden" aria-label={menuOpen ? 'Close menu' : 'Open menu'} aria-expanded={menuOpen}>
            {menuOpen ? <X size={19} /> : <Menu size={19} />}
          </button>
        </div>
      </div>
      {menuOpen && <nav aria-label="Mobile navigation" className="grid border-t border-slate-200 bg-white px-4 py-2 lg:hidden">
        {links.map((link) => <Link key={link.href} href={link.href} onClick={() => setMenuOpen(false)} className="min-h-11 border-b border-slate-100 py-3 text-sm text-slate-800">{language === 'en' ? link.en : link.ta}</Link>)}
        <Link href="/rescue-hub" onClick={() => setMenuOpen(false)} className="min-h-11 bg-red-800 py-3 text-center text-sm font-bold text-white">GET HELP</Link>
      </nav>}
    </header>
  );
}
