'use client';

import { FormEvent, useMemo, useState } from 'react';
import { createTripSearch, generatePlaybook, generateRecommendations } from '@/lib/api';
import { PlaybookResponse, RecommendationBundle } from '@/lib/types';

type Step = 'search' | 'options' | 'playbook';
type BackendProgram = 'MR' | 'CAP1' | 'MARRIOTT';
type Cabin = 'economy' | 'premium_economy' | 'business' | 'first';

interface Bucket {
  program: string;
  points: number;
}

const PROGRAM_OPTIONS = [
  'Amex Membership Rewards',
  'Chase Ultimate Rewards',
  'Citi ThankYou Points',
  'Capital One Miles',
  'Marriott Bonvoy',
  'World of Hyatt',
];

const PROGRAM_BACKEND: Record<string, BackendProgram> = {
  'Amex Membership Rewards': 'MR',
  'Chase Ultimate Rewards': 'MR',
  'Citi ThankYou Points': 'MR',
  'Capital One Miles': 'CAP1',
  'Marriott Bonvoy': 'MARRIOTT',
  'World of Hyatt': 'MARRIOTT',
};

function buildBalances(buckets: Bucket[]) {
  const totals: Partial<Record<BackendProgram, number>> = {};
  for (const b of buckets) {
    if (!b.points) continue;
    const type = PROGRAM_BACKEND[b.program] ?? 'MR';
    totals[type] = (totals[type] ?? 0) + b.points;
  }
  return (Object.entries(totals) as [BackendProgram, number][]).map(
    ([program, balance]) => ({ program, balance })
  );
}

export default function HomePage() {
  const [step, setStep] = useState<Step>('search');
  const [origins, setOrigins] = useState('IAD, DCA');
  const [dests, setDests] = useState('');
  const [start, setStart] = useState('');
  const [end, setEnd] = useState('');
  const [travelers, setTravelers] = useState(1);
  const [cabin, setCabin] = useState<Cabin>('economy');
  const [buckets, setBuckets] = useState<Bucket[]>([
    { program: 'Amex Membership Rewards', points: 0 },
    { program: 'Capital One Miles', points: 0 },
    { program: 'Marriott Bonvoy', points: 0 },
  ]);
  const [nights, setNights] = useState(5);
  const [hours, setHours] = useState(10);
  const [pointsOpen, setPointsOpen] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [bundle, setBundle] = useState<RecommendationBundle | null>(null);
  const [playbook, setPlaybook] = useState<PlaybookResponse | null>(null);

  const originList = useMemo(
    () => origins.split(',').map((s) => s.trim().toUpperCase()).filter(Boolean),
    [origins]
  );
  const destList = useMemo(
    () => dests.split(',').map((s) => s.trim().toUpperCase()).filter(Boolean),
    [dests]
  );
  const hasPoints = useMemo(() => buckets.some((b) => b.points > 0), [buckets]);
  const canSearch = useMemo(
    () => originList.length > 0 && !!start && !!end && hasPoints,
    [originList, start, end, hasPoints]
  );

  const updateBucketProgram = (i: number, program: string) =>
    setBuckets((prev) => prev.map((b, idx) => (idx === i ? { ...b, program } : b)));

  const updateBucketPoints = (i: number, points: number) =>
    setBuckets((prev) => prev.map((b, idx) => (idx === i ? { ...b, points } : b)));

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!canSearch) return;
    setLoading(true);
    setError('');
    setPlaybook(null);
    try {
      const trip = await createTripSearch({
        origins: originList,
        preferred_destinations: destList,
        date_window_start: start,
        date_window_end: end,
        duration_nights: nights,
        travelers,
        vibe_tags: ['warm beach'],
        cabin_preference: cabin,
        constraints: {
          max_travel_hours: hours,
          max_stops: 1,
          nonstop_preferred: false,
        },
        balances: buildBalances(buckets),
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

      <section className="mobile-shell w-full px-4 md:px-8 pt-4 pb-16">
        <div className="glass p-5 md:p-8 mb-4">

          {/* ——— Nav ——— */}
          <div className="flex items-center justify-between">
            <div className="text-white text-2xl font-bold tracking-tight">pointpilot</div>
            <div className="flex items-center gap-3">
              {step !== 'search' && (
                <div className="hidden sm:flex items-center gap-1 text-xs font-semibold">
                  <span className="text-white/35">Explore</span>
                  <span className="text-white/25 mx-0.5">›</span>
                  <span className={step === 'options' ? 'text-white' : 'text-white/35'}>Discover</span>
                  <span className="text-white/25 mx-0.5">›</span>
                  <span className={step === 'playbook' ? 'text-white' : 'text-white/35'}>Capitalize</span>
                </div>
              )}
              <button className="btn-primary">Sign up</button>
            </div>
          </div>

          {/* ——— Search step ——— */}
          {step === 'search' && (
            <>
              <h1 className="text-white text-[clamp(38px,8vw,68px)] font-bold tracking-[-0.03em] leading-[0.92] max-w-3xl mt-6">
                Fly smarter<br />with points.
              </h1>
              <p className="text-white/60 text-[clamp(15px,1.8vw,19px)] mt-3 font-light tracking-wide">
                Explore. Discover. Capitalize.
              </p>

              <form onSubmit={onSubmit} className="search-panel">
                {/* Top row: trip type, traveler count, cabin */}
                <div className="flex items-center gap-3 mb-4 flex-wrap">
                  <span className="text-white/75 text-sm font-medium">Round trip</span>
                  <span className="text-white/25">·</span>
                  <select
                    className="s-top-select"
                    value={travelers}
                    onChange={(e) => setTravelers(Number(e.target.value))}
                  >
                    {[1, 2, 3, 4, 5, 6].map((n) => (
                      <option key={n} value={n}>{n} Traveler{n > 1 ? 's' : ''}</option>
                    ))}
                  </select>
                  <span className="text-white/25">·</span>
                  <select
                    className="s-top-select"
                    value={cabin}
                    onChange={(e) => setCabin(e.target.value as Cabin)}
                  >
                    <option value="economy">Economy</option>
                    <option value="premium_economy">Premium Economy</option>
                    <option value="business">Business</option>
                    <option value="first">First</option>
                  </select>
                </div>

                {/* Route row */}
                <div className="s-route-row">
                  <div className="s-field">
                    <label className="s-label">From</label>
                    <input
                      className="s-input"
                      value={origins}
                      onChange={(e) => setOrigins(e.target.value.toUpperCase())}
                      placeholder="IAD, DCA..."
                    />
                  </div>
                  <button
                    type="button"
                    className="s-swap"
                    onClick={() => {
                      const tmp = origins;
                      setOrigins(dests);
                      setDests(tmp);
                    }}
                  >
                    ⇄
                  </button>
                  <div className="s-field">
                    <label className="s-label">To</label>
                    <input
                      className="s-input"
                      value={dests}
                      onChange={(e) => setDests(e.target.value.toUpperCase())}
                      placeholder="Anywhere"
                    />
                  </div>
                </div>

                {/* Date row */}
                <div className="s-date-row">
                  <div className="s-field">
                    <label className="s-label">Depart</label>
                    <input
                      className="s-input"
                      type="date"
                      value={start}
                      onChange={(e) => setStart(e.target.value)}
                    />
                  </div>
                  <div className="s-field">
                    <label className="s-label">Return</label>
                    <input
                      className="s-input"
                      type="date"
                      value={end}
                      onChange={(e) => setEnd(e.target.value)}
                    />
                  </div>
                </div>

                {/* Nights + Max travel hours */}
                <div className="grid grid-cols-2 gap-3 mb-3">
                  <div className="s-field">
                    <label className="s-label">Nights</label>
                    <input
                      className="s-input"
                      type="number"
                      min={2}
                      max={14}
                      value={nights}
                      onChange={(e) => setNights(Number(e.target.value || 5))}
                    />
                  </div>
                  <div className="s-field">
                    <label className="s-label">Max travel hours</label>
                    <input
                      className="s-input"
                      type="number"
                      min={4}
                      max={16}
                      value={hours}
                      onChange={(e) => setHours(Number(e.target.value || 10))}
                    />
                  </div>
                </div>

                {/* Points buckets — collapsible */}
                <div className="mb-3">
                  <button
                    type="button"
                    className="s-collapse-toggle"
                    onClick={() => setPointsOpen((v) => !v)}
                  >
                    <span className="s-label" style={{ marginBottom: 0 }}>Points & Programs</span>
                    <span className="s-collapse-chevron">{pointsOpen ? '▲' : '▼'}</span>
                  </button>
                  {pointsOpen && (
                    <div className="space-y-2 mt-2">
                      {buckets.map((bucket, i) => (
                        <div key={i} className="s-bucket-row">
                          <select
                            className="s-select"
                            value={bucket.program}
                            onChange={(e) => updateBucketProgram(i, e.target.value)}
                          >
                            {PROGRAM_OPTIONS.map((p) => (
                              <option key={p} value={p}>{p}</option>
                            ))}
                          </select>
                          <input
                            className="s-input"
                            type="number"
                            min={0}
                            step={1000}
                            value={bucket.points || ''}
                            onChange={(e) => updateBucketPoints(i, Number(e.target.value || 0))}
                            placeholder="Points"
                          />
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <button type="submit" className="btn-explore" disabled={!canSearch || loading}>
                  {loading ? 'Searching...' : 'Explore'}
                </button>
              </form>
            </>
          )}

          {/* ——— Options step ——— */}
          {step === 'options' && bundle && (
            <>
              <div className="mt-6 flex items-center justify-between">
                <h2 className="text-white text-2xl font-bold">Flight Options</h2>
                <button className="btn-secondary" onClick={() => setStep('search')}>
                  Edit Search
                </button>
              </div>
              <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3">
                {bundle.options?.map((o) => (
                  <article key={o.id} className="option-card">
                    <div className="option-dest">{o.destination}</div>
                    <div className="option-oop">${o.oop_total?.toFixed(0)} out of pocket</div>
                    <div className="mt-2 text-sm text-white/55 space-y-0.5">
                      <div>Score: {o.score_final?.toFixed(3)}</div>
                      <div>Flight CPP: {o.cpp_flight ?? '—'} · Hotel CPP: {o.cpp_hotel ?? '—'}</div>
                    </div>
                    <button
                      className="btn-open-playbook mt-4"
                      onClick={() => onChooseOption(o.id)}
                      disabled={loading}
                    >
                      {loading ? 'Loading...' : 'Open Playbook →'}
                    </button>
                  </article>
                ))}
              </div>
            </>
          )}

          {/* ——— Playbook step ——— */}
          {step === 'playbook' && playbook && (
            <>
              <div className="mt-6 flex items-center justify-between">
                <h2 className="text-white text-2xl font-bold">Your Playbook</h2>
                <button className="btn-secondary" onClick={() => setStep('options')}>
                  ← Back to Options
                </button>
              </div>
              <div className="mt-5 grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <div className="playbook-section-title">Transfer Steps</div>
                  <ol className="space-y-3">
                    {playbook.transfer_steps.map((s, i) => (
                      <li key={i} className="playbook-step">
                        <span className="playbook-step-num">{i + 1}</span>
                        <span>{s}</span>
                      </li>
                    ))}
                  </ol>
                </div>
                <div>
                  <div className="playbook-section-title">Booking Steps</div>
                  <ol className="space-y-3">
                    {playbook.booking_steps.map((s, i) => (
                      <li key={i} className="playbook-step">
                        <span className="playbook-step-num">{i + 1}</span>
                        <span>{s}</span>
                      </li>
                    ))}
                  </ol>
                </div>
              </div>
            </>
          )}
        </div>

        {/* ——— Deals section (search step only) ——— */}
        {step === 'search' && (
          <section className="deals-shell mt-4">
            <h2 className="deals-title">Discover the best deals</h2>
            <p className="deals-sub">in First, Business, and Economy class</p>

            <div className="deal-card mt-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="text-xl font-semibold text-slate-900">8:35 AM — 11:45 AM</div>
                  <div className="text-slate-500 text-sm mt-0.5">Air France · Business</div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-slate-900">47,500 pts</div>
                  <div className="text-slate-500 text-sm mt-0.5">+$86.00 · 1+ Seat</div>
                </div>
              </div>
              <div className="mt-3 text-slate-500 text-sm">Apr 15 · FDF → CAY · 2h 10m · Nonstop</div>
            </div>

            <div className="mt-4">
              <button className="btn-pink">View All</button>
            </div>
          </section>
        )}

        {error && (
          <p className="mt-4 text-sm text-red-100 bg-red-900/40 border border-red-300/30 rounded-xl p-3">
            {error}
          </p>
        )}
      </section>
    </main>
  );
}
