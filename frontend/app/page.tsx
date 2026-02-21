'use client';

import { FormEvent, useMemo, useState } from 'react';
import { createTripSearch, generateRecommendations } from '@/lib/api';
import { RecommendationBundle } from '@/lib/types';

const ORIGINS = ['IAD', 'DCA', 'JFK', 'EWR', 'LAX', 'SFO', 'MIA', 'ORD'];
const DESTS = ['CUN', 'PUJ', 'NAS', 'LIM', 'CDG', 'FCO', 'LHR', 'KEF', 'ATH', 'HND', 'BKK'];

export default function HomePage() {
  const [origins, setOrigins] = useState<string[]>(['IAD', 'DCA']);
  const [dests, setDests] = useState<string[]>([]);
  const [start, setStart] = useState('');
  const [end, setEnd] = useState('');
  const [budget, setBudget] = useState(150000);
  const [hours, setHours] = useState(10);
  const [stops, setStops] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [bundle, setBundle] = useState<RecommendationBundle | null>(null);

  const canSearch = useMemo(() => origins.length > 0 && !!start && !!end && budget > 0, [origins, start, end, budget]);

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!canSearch) return;
    setLoading(true);
    setError('');
    try {
      const trip = await createTripSearch({
        origin_airports: origins,
        preferred_destinations: dests,
        start_date: start,
        end_date: end,
        max_points_budget: budget,
        max_travel_hours: hours,
        stops
      });
      const recs = await generateRecommendations(trip.id);
      setBundle(recs);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Request failed');
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
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="label">Hours</label>
                <input className="control w-full" type="number" min={4} max={16} value={hours} onChange={(e) => setHours(Number(e.target.value || 10))} />
              </div>
              <div>
                <label className="label">Stops</label>
                <select className="control w-full" value={stops} onChange={(e) => setStops(Number(e.target.value))}>
                  <option value={0}>0</option>
                  <option value={1}>1</option>
                  <option value={2}>2</option>
                </select>
              </div>
            </div>
          </div>

          <div className="mt-4">
            <button type="submit" className="btn-primary" disabled={!canSearch || loading}>
              {loading ? 'Searching...' : 'Search Trips'}
            </button>
          </div>

          {error && <p className="mt-3 text-sm text-red-700">{error}</p>}
        </form>

        {bundle && (
          <section className="mt-5 glass p-5">
            <h2 className="text-[22px] font-semibold text-white">Options</h2>
            <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3">
              {bundle.options?.map((o) => (
                <article key={o.option_id} className="rounded-xl border border-white/30 bg-white/20 p-4">
                  <div className="text-white font-semibold">{o.destination_city} ({o.destination_airport})</div>
                  <div className="text-white/90 text-sm mt-1">Mode: {o.api_mode || 'ESTIMATED'} · Score: {o.score ?? '-'}</div>
                  <div className="text-white/90 text-sm">Points: {o.estimated_points_total ?? '-'}</div>
                </article>
              ))}
            </div>
          </section>
        )}
      </section>
    </main>
  );
}
