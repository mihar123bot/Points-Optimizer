'use client';

import { FormEvent, useMemo, useState } from 'react';
import { createTripSearch, generatePlaybook, generateRecommendations } from '@/lib/api';
import { PlaybookResponse, RecommendationBundle } from '@/lib/types';

type Step = 'search' | 'options' | 'playbook';

const ORIGINS = ['IAD', 'DCA', 'BWI', 'JFK', 'EWR', 'BOS', 'LAX', 'SFO', 'ORD', 'ATL', 'MIA', 'DFW', 'SEA'];
const DESTS = ['CUN', 'PUJ', 'NAS', 'SJD', 'YVR', 'EZE', 'LIM', 'CDG', 'FCO', 'LHR', 'KEF', 'ATH', 'HND', 'BKK'];

function Pill({ text, active }: { text: string; active: boolean }) {
  return <span className={`px-3 py-1 rounded-full text-xs border ${active ? 'bg-blue-600 text-white border-blue-600' : 'bg-white/30 text-slate-700 border-white/40'}`}>{text}</span>;
}

export default function HomePage() {
  const [step, setStep] = useState<Step>('search');
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

      <section className="mx-auto w-full max-w-6xl px-5 py-8">
        <div className="glass min-h-[34vh] p-6 flex flex-col justify-end mb-5">
          <h1 className="text-white text-[clamp(40px,6vw,64px)] font-bold tracking-[-0.02em] leading-[1.02]">PointPilot</h1>
          <p className="text-white/90 text-lg mt-2">Fly smarter with points you already have.</p>
        </div>

        <div className="flex gap-2 mb-4">
          <Pill text="1. Search" active={step === 'search'} />
          <Pill text="2. Options" active={step === 'options'} />
          <Pill text="3. Playbook" active={step === 'playbook'} />
        </div>

        {step === 'search' && (
          <form onSubmit={onSubmit} className="search-tray p-4 md:p-5">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div>
                <label className="label">From (airports)</label>
                <input className="control w-full" value={origins.join(',')} onChange={(e) => setOrigins(e.target.value.split(',').map(s => s.trim().toUpperCase()).filter(Boolean))} placeholder={ORIGINS.join(', ')} />
              </div>
              <div>
                <label className="label">To (optional)</label>
                <input className="control w-full" value={dests.join(',')} onChange={(e) => setDests(e.target.value.split(',').map(s => s.trim().toUpperCase()).filter(Boolean))} placeholder={DESTS.join(', ')} />
              </div>
              <div>
                <label className="label">Points budget</label>
                <input className="control w-full" type="number" min={10000} step={1000} value={budget} onChange={(e) => setBudget(Number(e.target.value || 0))} />
              </div>

              <div>
                <label className="label">Depart</label>
                <input className="control w-full" type="date" value={start} onChange={(e) => setStart(e.target.value)} />
              </div>
              <div>
                <label className="label">Return</label>
                <input className="control w-full" type="date" value={end} onChange={(e) => setEnd(e.target.value)} />
              </div>
              <div>
                <label className="label">Nights</label>
                <input className="control w-full" type="number" min={2} max={14} value={nights} onChange={(e) => setNights(Number(e.target.value || 5))} />
              </div>

              <div>
                <label className="label">Max travel hours</label>
                <input className="control w-full" type="number" min={4} max={16} value={hours} onChange={(e) => setHours(Number(e.target.value || 10))} />
              </div>
              <div>
                <label className="label">Max stops</label>
                <select className="control w-full" value={stops} onChange={(e) => setStops(Number(e.target.value))}>
                  <option value={0}>0</option>
                  <option value={1}>1</option>
                  <option value={2}>2</option>
                </select>
              </div>
            </div>

            <div className="mt-4">
              <button type="submit" className="btn-primary" disabled={!canSearch || loading}>
                {loading ? 'Searching...' : 'Search Trips'}
              </button>
            </div>
          </form>
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
                  <div className="text-white/90 text-sm mt-1">Score: {o.score_final?.toFixed(3)} · OOP: ${o.oop_total?.toFixed(0)}</div>
                  <div className="text-white/90 text-sm">Flight CPP: {o.cpp_flight ?? '-'} · Hotel CPP: {o.cpp_hotel ?? '-'}</div>
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
              <div>
                <h3 className="font-semibold mb-2">Warnings</h3>
                <ul className="list-disc pl-5 space-y-1 text-sm">
                  {playbook.warnings.map((s, i) => <li key={i}>{s}</li>)}
                </ul>
              </div>
              <div>
                <h3 className="font-semibold mb-2">Fallbacks</h3>
                <ul className="list-disc pl-5 space-y-1 text-sm">
                  {playbook.fallbacks.map((s, i) => <li key={i}>{s}</li>)}
                </ul>
              </div>
            </div>
          </section>
        )}

        {error && <p className="mt-4 text-sm text-red-200 bg-red-900/40 border border-red-300/30 rounded-lg p-3">{error}</p>}
      </section>
    </main>
  );
}
