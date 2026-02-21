'use client';

import { FormEvent, useMemo, useState } from 'react';
import { createTripSearch, generatePlaybook, generateRecommendations } from '@/lib/api';
import { PlaybookResponse, RecommendationBundle } from '@/lib/types';

type Step = 'search' | 'options' | 'playbook';
type Mode = 'simple' | 'nerd';

const ORIGINS = ['IAD', 'DCA', 'BWI', 'JFK', 'EWR', 'BOS', 'LAX', 'SFO', 'ORD', 'ATL', 'MIA', 'DFW', 'SEA'];
const DESTS = ['CUN', 'PUJ', 'NAS', 'SJD', 'YVR', 'EZE', 'LIM', 'CDG', 'FCO', 'LHR', 'KEF', 'ATH', 'HND', 'BKK'];

function Pill({ text, active }: { text: string; active: boolean }) {
  return <span className={`px-3 py-1 rounded-full text-xs border ${active ? 'bg-blue-600 text-white border-blue-600' : 'bg-white/25 text-white border-white/40'}`}>{text}</span>;
}

function ChipGroup({ values, selected, onToggle }: { values: string[]; selected: string[]; onToggle: (v: string) => void }) {
  return (
    <div className="flex flex-wrap gap-2">
      {values.map((v) => (
        <button key={v} type="button" className={`chip ${selected.includes(v) ? 'active' : ''}`} onClick={() => onToggle(v)}>
          {v}
        </button>
      ))}
    </div>
  );
}

export default function HomePage() {
  const [step, setStep] = useState<Step>('search');
  const [mode, setMode] = useState<Mode>('simple');
  const [origins, setOrigins] = useState<string[]>(['IAD', 'DCA']);
  const [dests, setDests] = useState<string[]>([]);
  const [start, setStart] = useState('');
  const [end, setEnd] = useState('');
  const [budget, setBudget] = useState(150000);
  const [nights, setNights] = useState(5);
  const [hours, setHours] = useState(10);
  const [stops, setStops] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [bundle, setBundle] = useState<RecommendationBundle | null>(null);
  const [playbook, setPlaybook] = useState<PlaybookResponse | null>(null);

  const canSearch = useMemo(() => origins.length > 0 && !!start && !!end && budget > 0, [origins, start, end, budget]);

  const toggle = (arr: string[], set: (v: string[]) => void, v: string) => {
    if (arr.includes(v)) set(arr.filter((x) => x !== v));
    else set([...arr, v]);
  };

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!canSearch) return;
    setLoading(true);
    setError('');
    setPlaybook(null);
    try {
      const trip = await createTripSearch({
        origins,
        preferred_destinations: dests,
        date_window_start: start,
        date_window_end: end,
        duration_nights: nights,
        travelers: 2,
        vibe_tags: ['warm beach'],
        cabin_preference: 'economy',
        constraints: {
          max_travel_hours: hours,
          max_stops: stops,
          nonstop_preferred: stops === 0
        },
        balances: [
          { program: 'MR', balance: budget },
          { program: 'CAP1', balance: Math.round(budget * 0.5) },
          { program: 'MARRIOTT', balance: Math.round(budget * 0.4) }
        ]
      });
      const recs = await generateRecommendations(trip.id);
      setBundle(recs);
      setStep('options');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Request failed');
    } finally {
      setLoading(false);
    }
  };

  const onChooseOption = async (optionId: string) => {
    setLoading(true);
    setError('');
    try {
      const pb = await generatePlaybook(optionId);
      setPlaybook(pb);
      setStep('playbook');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Playbook request failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="relative min-h-screen">
      <div className="hero-bg" />
      <div className="hero-overlay" />
      <div className="hero-overlay-warm" />

      <section className="mobile-shell w-full px-5 md:px-8 py-8 pb-16">
        <div className="glass min-h-[72vh] p-6 md:p-8 flex flex-col mb-4">
          <div className="flex items-center justify-between">
            <div className="text-white text-4xl font-semibold tracking-tight">pointpilot</div>
            <button className="btn-primary">Sign up</button>
          </div>

          <div className="mt-6 text-center">
            <div className="hero-tabs">
              <span className="hero-tab active">Flights</span>
              <span className="hero-tab">Hotels</span>
            </div>
          </div>

          <div className="mt-auto">
            <h1 className="text-white text-[clamp(52px,13vw,82px)] font-bold tracking-[-0.03em] leading-[0.9] max-w-4xl">
              Free flights using points
            </h1>
            <p className="text-white/90 text-[clamp(24px,3vw,40px)] mt-4 max-w-2xl font-light">Book your dream vacation with points</p>

            <div className="hero-search-pill mt-8 p-4 md:p-5 text-white">
              <div className="text-3xl font-semibold tracking-wide">{origins[0] || 'JFK'} → {dests[0] || 'SFO'}</div>
              <div className="text-white/85 text-lg mt-1">{start || 'Feb 22'} • Economy • 1 Traveler</div>
            </div>
          </div>
        </div>

        <div className="flex gap-2 mb-4 items-center">
          <Pill text="1. Search" active={step === 'search'} />
          <Pill text="2. Options" active={step === 'options'} />
          <Pill text="3. Playbook" active={step === 'playbook'} />
          <div className="ml-auto">
            <button className={`chip ${mode === 'simple' ? 'active' : ''}`} onClick={() => setMode('simple')}>Simple</button>
            <button className={`chip ml-2 ${mode === 'nerd' ? 'active' : ''}`} onClick={() => setMode('nerd')}>Nerd</button>
          </div>
        </div>

        {step === 'search' && (
          <>
            <form onSubmit={onSubmit} className="search-tray p-4 mt-2 relative z-10 g-search-shell">
              <div className="g-top-row mb-3">
                <span>⇄ Round trip</span>
                <span>👤 1</span>
                <span>Economy</span>
              </div>

              <div className="g-route-row">
                <input
                  className="g-route-input"
                  value={origins.join(', ')}
                  onChange={(e) => setOrigins(e.target.value.split(',').map((s) => s.trim().toUpperCase()).filter(Boolean))}
                  placeholder="From (IAD, DCA)"
                />
                <button
                  type="button"
                  className="g-swap"
                  onClick={() => {
                    const firstOrigin = origins[0] || '';
                    const firstDest = dests[0] || '';
                    setOrigins(firstDest ? [firstDest] : []);
                    setDests(firstOrigin ? [firstOrigin] : []);
                  }}
                >
                  ⇄
                </button>
                <input
                  className="g-route-input"
                  value={dests.join(', ')}
                  onChange={(e) => setDests(e.target.value.split(',').map((s) => s.trim().toUpperCase()).filter(Boolean))}
                  placeholder="Where to?"
                />
              </div>

              <div className="g-date-row mt-3">
                <input className="g-date-input" type="date" value={start} onChange={(e) => setStart(e.target.value)} />
                <input className="g-date-input" type="date" value={end} onChange={(e) => setEnd(e.target.value)} />
              </div>

              <div className="g-points-row mt-3">
                <input
                  className="g-route-input"
                  type="number"
                  min={10000}
                  step={1000}
                  value={budget}
                  onChange={(e) => setBudget(Number(e.target.value || 0))}
                  placeholder="How many points do you want to use?"
                />
              </div>

              {mode === 'nerd' && (
                <div className="grid grid-cols-2 gap-2 mt-3">
                  <input className="control w-full" type="number" min={2} max={14} value={nights} onChange={(e) => setNights(Number(e.target.value || 5))} placeholder="Nights" />
                  <input className="control w-full" type="number" min={4} max={16} value={hours} onChange={(e) => setHours(Number(e.target.value || 10))} placeholder="Max travel hours" />
                </div>
              )}

              <div className="g-cta-wrap">
                <button type="submit" className="btn-primary g-explore-btn" disabled={!canSearch || loading}>
                  {loading ? 'Searching...' : 'Explore'}
                </button>
              </div>
            </form>

            <section className="deals-shell mt-5">
              <h2 className="deals-title">Discover the best deals</h2>
              <p className="deals-sub">in First, Business, and Economy class</p>

              <div className="deal-card mt-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="text-2xl font-semibold text-slate-900">8:35 AM - 11:45 AM</div>
                    <div className="text-slate-500">Air France · Business</div>
                  </div>
                  <div className="text-right">
                    <div className="text-4xl font-semibold text-slate-900">47,500 pts</div>
                    <div className="text-slate-500">+$86.00 · Seats Left: 1+</div>
                  </div>
                </div>
                <div className="mt-3 text-slate-700">Apr 15 · FDF → CAY · 2h 10m · Nonstop</div>
              </div>

              <div className="mt-4">
                <button className="btn-pink">View All</button>
              </div>
            </section>
          </>
        )}

        {step === 'options' && bundle && (
          <section className="glass p-5">
            <div className="flex items-center justify-between">
              <h2 className="text-[22px] font-semibold text-white">Options</h2>
              <button className="btn-primary" onClick={() => setStep('search')}>Edit Search</button>
            </div>
            <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3">
              {bundle.options?.map((o) => (
                <article key={o.id} className="rounded-xl border border-white/30 bg-white/20 p-4">
                  <div className="text-white font-semibold">{o.destination}</div>
                  <div className="text-white/90 text-sm mt-1">OOP: ${o.oop_total?.toFixed(0)}</div>
                  {mode === 'nerd' && (
                    <>
                      <div className="text-white/90 text-sm">Score: {o.score_final?.toFixed(3)}</div>
                      <div className="text-white/90 text-sm">Flight CPP: {o.cpp_flight ?? '-'} · Hotel CPP: {o.cpp_hotel ?? '-'}</div>
                    </>
                  )}
                  <div className="mt-3">
                    <button className="btn-primary" onClick={() => onChooseOption(o.id)} disabled={loading}>
                      {loading ? 'Loading...' : 'Open Playbook'}
                    </button>
                  </div>
                </article>
              ))}
            </div>
          </section>
        )}

        {step === 'playbook' && playbook && (
          <section className="glass p-5">
            <div className="flex items-center justify-between">
              <h2 className="text-[22px] font-semibold text-white">Playbook</h2>
              <button className="btn-primary" onClick={() => setStep('options')}>Back to Options</button>
            </div>
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4 text-white">
              <div>
                <h3 className="font-semibold mb-2">Transfer Steps</h3>
                <ul className="list-disc pl-5 space-y-1 text-sm">
                  {playbook.transfer_steps.map((s, i) => <li key={i}>{s}</li>)}
                </ul>
              </div>
              <div>
                <h3 className="font-semibold mb-2">Booking Steps</h3>
                <ul className="list-disc pl-5 space-y-1 text-sm">
                  {playbook.booking_steps.map((s, i) => <li key={i}>{s}</li>)}
                </ul>
              </div>
            </div>
          </section>
        )}

        {error && <p className="mt-4 text-sm text-red-100 bg-red-900/40 border border-red-300/30 rounded-lg p-3">{error}</p>}
      </section>
    </main>
  );
}
