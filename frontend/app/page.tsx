'use client';

import { FormEvent, useMemo, useState } from 'react';
import { createTripSearch, generatePlaybook, generateRecommendations } from '@/lib/api';
import { PlaybookResponse, RecommendationBundle } from '@/lib/types';

type Step = 'search' | 'options' | 'playbook';
type BackendProgram = 'MR' | 'CAP1' | 'MARRIOTT';

interface Bucket {
  program: string;
  points: number;
}

interface Airport {
  code: string;
  name: string;
  city: string;
}

const AIRPORTS: Airport[] = [
  // DMV
  { code: 'IAD', name: 'Washington Dulles International', city: 'Washington DC' },
  { code: 'DCA', name: 'Ronald Reagan Washington National', city: 'Washington DC' },
  { code: 'BWI', name: 'Baltimore/Washington International', city: 'Baltimore' },
  // Dallas
  { code: 'DFW', name: 'Dallas Fort Worth International', city: 'Dallas' },
  { code: 'DAL', name: 'Dallas Love Field', city: 'Dallas' },
  // NYC
  { code: 'JFK', name: 'John F. Kennedy International', city: 'New York' },
  { code: 'LGA', name: 'LaGuardia', city: 'New York' },
  { code: 'EWR', name: 'Newark Liberty International', city: 'New York' },
  // Houston
  { code: 'IAH', name: 'George Bush Intercontinental', city: 'Houston' },
  { code: 'HOU', name: 'William P. Hobby', city: 'Houston' },
  // International
  { code: 'CUN', name: 'Cancún International', city: 'Cancún' },
  { code: 'PUJ', name: 'Punta Cana International', city: 'Punta Cana' },
  { code: 'NAS', name: 'Lynden Pindling International', city: 'Nassau' },
  { code: 'SJD', name: 'Los Cabos International', city: 'Los Cabos' },
  { code: 'YVR', name: 'Vancouver International', city: 'Vancouver' },
  { code: 'EZE', name: 'Ministro Pistarini International', city: 'Buenos Aires' },
  { code: 'LIM', name: 'Jorge Chávez International', city: 'Lima' },
  { code: 'CDG', name: 'Charles de Gaulle', city: 'Paris' },
  { code: 'FCO', name: 'Leonardo da Vinci–Fiumicino', city: 'Rome' },
  { code: 'LHR', name: 'Heathrow', city: 'London' },
  { code: 'KEF', name: 'Keflavík International', city: 'Reykjavík' },
  { code: 'ATH', name: 'Athens International', city: 'Athens' },
  { code: 'HND', name: 'Tokyo Haneda', city: 'Tokyo' },
  { code: 'BKK', name: 'Suvarnabhumi', city: 'Bangkok' },
];

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

function AirportCombobox({
  label,
  selected,
  onChange,
  placeholder = 'City or airport...',
}: {
  label: string;
  selected: string[];
  onChange: (codes: string[]) => void;
  placeholder?: string;
}) {
  const [query, setQuery] = useState('');
  const [open, setOpen] = useState(false);

  const filtered = useMemo(() => {
    if (!query) return [];
    const q = query.toLowerCase();
    return AIRPORTS.filter(
      (a) =>
        a.code.toLowerCase().startsWith(q) ||
        a.city.toLowerCase().includes(q) ||
        a.name.toLowerCase().includes(q)
    ).slice(0, 7);
  }, [query]);

  const select = (code: string) => {
    if (selected.includes(code)) {
      onChange(selected.filter((c) => c !== code));
    } else {
      onChange([...selected, code]);
    }
    setQuery('');
    setOpen(false);
  };

  const remove = (code: string) => {
    onChange(selected.filter((c) => c !== code));
  };

  return (
    <div className="s-field" style={{ position: 'relative' }}>
      <label className="s-label">{label}</label>
      <div className="airport-input-wrap">
        {selected.map((code) => (
          <span key={code} className="airport-chip">
            {code}
            <button type="button" onClick={() => remove(code)}>×</button>
          </span>
        ))}
        <input
          className="airport-search-input"
          value={query}
          onChange={(e) => { setQuery(e.target.value); setOpen(true); }}
          onFocus={() => setOpen(true)}
          onBlur={() => setTimeout(() => setOpen(false), 150)}
          placeholder={selected.length === 0 ? placeholder : ''}
        />
      </div>
      {open && filtered.length > 0 && (
        <div className="airport-dropdown">
          {filtered.map((a) => (
            <button
              key={a.code}
              type="button"
              className={`airport-option${selected.includes(a.code) ? ' selected' : ''}`}
              onMouseDown={() => select(a.code)}
            >
              <span className="airport-code">{a.code}</span>
              <span className="airport-info">{a.name} · {a.city}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default function HomePage() {
  const [step, setStep] = useState<Step>('search');
  const [originCodes, setOriginCodes] = useState<string[]>(['IAD', 'DCA']);
  const [destCodes, setDestCodes] = useState<string[]>([]);
  const [start, setStart] = useState('');
  const [end, setEnd] = useState('');
  const [travelers, setTravelers] = useState(1);
  const [buckets, setBuckets] = useState<Bucket[]>([
    { program: 'Amex Membership Rewards', points: 0 },
    { program: 'Capital One Miles', points: 0 },
    { program: 'Marriott Bonvoy', points: 0 },
  ]);
  const [nights, setNights] = useState(5);
  const [hours, setHours] = useState(10);
  const [tripType, setTripType] = useState<'roundtrip' | 'oneway'>('roundtrip');
  const [pointsOpen, setPointsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [bundle, setBundle] = useState<RecommendationBundle | null>(null);
  const [playbook, setPlaybook] = useState<PlaybookResponse | null>(null);

  const hasPoints = useMemo(() => buckets.some((b) => b.points > 0), [buckets]);
  const totalPoints = useMemo(() => buckets.reduce((s, b) => s + (b.points || 0), 0), [buckets]);
  const canSearch = useMemo(
    () => originCodes.length > 0 && !!start && (tripType === 'oneway' || !!end),
    [originCodes, start, end, tripType]
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
        origins: originCodes,
        preferred_destinations: destCodes,
        date_window_start: start,
        date_window_end: end,
        duration_nights: nights,
        travelers,
        vibe_tags: [],
        cabin_preference: 'economy',
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
            <div className="flex items-center gap-2.5">
              <svg width="34" height="34" viewBox="0 0 34 34" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                {/* glass ring */}
                <circle cx="17" cy="17" r="15.5" fill="rgba(255,255,255,0.1)" stroke="rgba(255,255,255,0.5)" strokeWidth="1.2"/>
                {/* compass rose — N pointer (top, bright) */}
                <path d="M17 5 L19.4 15 L17 12.8 L14.6 15 Z" fill="white"/>
                {/* S pointer */}
                <path d="M17 29 L19.4 19 L17 21.2 L14.6 19 Z" fill="rgba(255,255,255,0.28)"/>
                {/* E pointer */}
                <path d="M29 17 L19 14.6 L21.2 17 L19 19.4 Z" fill="rgba(255,255,255,0.28)"/>
                {/* W pointer */}
                <path d="M5 17 L15 14.6 L12.8 17 L15 19.4 Z" fill="rgba(255,255,255,0.28)"/>
                {/* center dot */}
                <circle cx="17" cy="17" r="2.2" fill="rgba(255,255,255,0.88)"/>
              </svg>
              <span className="text-white font-bold tracking-[-0.025em]" style={{ fontSize: 21 }}>pointpilot</span>
            </div>
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
                {/* Top row: trip type, traveler count */}
                <div className="flex items-center gap-3 mb-4 flex-wrap">
                  <select
                    className="s-top-select"
                    value={tripType}
                    onChange={(e) => setTripType(e.target.value as 'roundtrip' | 'oneway')}
                  >
                    <option value="roundtrip">Round trip</option>
                    <option value="oneway">One-way</option>
                  </select>
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
                </div>

                {/* Route row */}
                <div className="s-route-row">
                  <AirportCombobox
                    label="From"
                    selected={originCodes}
                    onChange={setOriginCodes}
                    placeholder="City or airport..."
                  />
                  <button
                    type="button"
                    className="s-swap"
                    onClick={() => {
                      const tmp = originCodes;
                      setOriginCodes(destCodes);
                      setDestCodes(tmp);
                    }}
                  >
                    ⇄
                  </button>
                  <AirportCombobox
                    label="To"
                    selected={destCodes}
                    onChange={setDestCodes}
                    placeholder="Anywhere"
                  />
                </div>

                {/* Date row */}
                <div className={`s-date-row${tripType === 'oneway' ? ' s-date-row-single' : ''}`}>
                  <div className="s-field">
                    <label className="s-label">Depart</label>
                    <input
                      className="s-input"
                      type="date"
                      value={start}
                      onChange={(e) => setStart(e.target.value)}
                    />
                  </div>
                  {tripType === 'roundtrip' && (
                    <div className="s-field">
                      <label className="s-label">Return</label>
                      <input
                        className="s-input"
                        type="date"
                        value={end}
                        onChange={(e) => setEnd(e.target.value)}
                      />
                    </div>
                  )}
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
                    <span className="s-points-toggle-label">
                      {pointsOpen ? 'Points & Programs' : 'Enter point information'}
                    </span>
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

                <p className="text-xs text-white/40 text-center mb-2 mt-1">
                  {hasPoints
                    ? `Optimizing ${totalPoints.toLocaleString()} pts across programs`
                    : 'Searching best cash fares — enter points to unlock award search'}
                </p>
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
                <div>
                  <h2 className="text-white text-2xl font-bold">Flight Options</h2>
                  <p className="text-white/45 text-xs mt-0.5">
                    {bundle.options?.[0]?.search_mode === 'cash'
                      ? 'Sorted by lowest total cost'
                      : 'Sorted by best points value'}
                  </p>
                </div>
                <button className="btn-secondary" onClick={() => setStep('search')}>
                  Edit Search
                </button>
              </div>
              <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3">
                {bundle.options?.map((o) => {
                  const isBestBalanced = bundle.winner_tiles?.best_balanced === o.id;
                  const isBestCpp = !isBestBalanced && bundle.winner_tiles?.best_cpp === o.id;
                  const isBestPrice = !isBestBalanced && !isBestCpp && bundle.winner_tiles?.best_oop === o.id;
                  const badge = isBestBalanced ? 'Best Balanced' : isBestCpp ? 'Best CPP' : isBestPrice ? 'Best Price' : null;
                  const isCash = o.search_mode === 'cash';
                  const pts = o.points_breakdown?.flight_points;
                  const taxes = o.award_details?.taxes_fees ?? o.points_breakdown?.taxes_fees;
                  const cpp = o.points_breakdown?.flight_cpp ?? o.cpp_flight;

                  return (
                    <article key={o.id} className="option-card">
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <div>
                          <div className="option-dest">
                            {o.city_name || o.destination}
                            {o.city_name && <span className="option-dest-code"> · {o.destination}</span>}
                          </div>
                          <div className="option-route-line">
                            {o.origin} → {o.destination}
                            {o.airline ? ` · ${o.airline}` : ''}
                            {o.duration ? ` · ${o.duration}` : ''}
                          </div>
                        </div>
                        {badge && <span className="option-badge">{badge}</span>}
                      </div>

                      <div className="option-divider" />

                      {isCash ? (
                        <div>
                          <div className="option-price-big">
                            ${o.cash_price_pp ? o.cash_price_pp.toFixed(0) : o.oop_total.toFixed(0)}
                            <span className="option-price-unit">/person</span>
                          </div>
                          <div className="option-price-sub">${o.oop_total.toFixed(0)} est. total trip</div>
                        </div>
                      ) : (
                        <div>
                          {pts ? (
                            <>
                              <div className="option-price-big">
                                {pts.toLocaleString()} pts
                                {taxes ? <span className="option-price-unit"> + ${taxes.toFixed(0)} taxes</span> : ''}
                              </div>
                              {cpp && <div className="option-cpp-badge">{cpp.toFixed(1)}¢/pt value</div>}
                              <div className="option-price-sub">
                                vs ${o.cash_price_pp ? o.cash_price_pp.toFixed(0) : '—'} cash/person
                              </div>
                            </>
                          ) : (
                            <div className="option-price-big">
                              ${o.oop_total.toFixed(0)}
                              <span className="option-price-unit"> out of pocket</span>
                            </div>
                          )}
                        </div>
                      )}

                      <button
                        className="btn-open-playbook mt-3"
                        onClick={() => onChooseOption(o.id)}
                        disabled={loading}
                      >
                        {loading ? 'Loading...' : 'Open Playbook →'}
                      </button>
                    </article>
                  );
                })}
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
