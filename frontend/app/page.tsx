'use client';

import { FormEvent, useMemo, useState } from 'react';
import { createTripSearch, generatePlaybook, generateRecommendations } from '@/lib/api';
import { PlaybookResponse, RecommendationBundle } from '@/lib/types';
import { BackendProgram, PROGRAM_BACKEND } from '@/lib/constants';
import { SearchCard } from '@/components/SearchCard';
import { ResultsView } from '@/components/ResultsView';
import { PlaybookView } from '@/components/PlaybookView';

type Step = 'search' | 'results' | 'playbook';

function buildBalances(
  selected: Record<string, boolean>,
  balances: Record<string, string>
) {
  const totals: Partial<Record<BackendProgram, number>> = {};
  for (const id of Object.keys(selected)) {
    if (!selected[id]) continue;
    const pts = parseInt(balances[id] || '0', 10);
    if (!pts) continue;
    const type = PROGRAM_BACKEND[id];
    if (!type) continue;
    totals[type] = (totals[type] ?? 0) + pts;
  }
  return (Object.entries(totals) as [BackendProgram, number][]).map(
    ([program, balance]) => ({ program, balance })
  );
}

export default function HomePage() {
  // ── View state
  const [step, setStep] = useState<Step>('search');

  // ── Search form state
  const [originCodes, setOriginCodes]         = useState<string[]>(['IAD', 'DCA']);
  const [destCodes,   setDestCodes]           = useState<string[]>([]);
  const [start,       setStart]               = useState('');
  const [end,         setEnd]                 = useState('');
  const [travelers,   setTravelers]           = useState(1);
  const [nights,      setNights]              = useState(5);
  const [hours,       setHours]               = useState(10);
  const [tripType,    setTripType]            = useState<'roundtrip' | 'oneway'>('roundtrip');
  const [searchMode,  setSearchMode]          = useState<'cash' | 'points' | 'mixed'>('mixed');
  const [selectedPrograms, setSelectedPrograms] = useState<Record<string, boolean>>({ chase: true });
  const [badgeBalances,    setBadgeBalances]   = useState<Record<string, string>>({});

  // ── Async state
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState('');
  const [bundle,  setBundle]  = useState<RecommendationBundle | null>(null);
  const [playbook, setPlaybook] = useState<PlaybookResponse | null>(null);

  const canSearch = useMemo(
    () => originCodes.length > 0 && !!start && (tripType === 'oneway' || !!end),
    [originCodes, start, end, tripType]
  );

  // ── Handlers
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!canSearch) return;
    setLoading(true);
    setError('');
    setPlaybook(null);
    try {
      const trip = await createTripSearch({
        origins:               originCodes,
        preferred_destinations: destCodes,
        date_window_start:     start,
        date_window_end:       end,
        duration_nights:       nights,
        travelers,
        vibe_tags:             [],
        cabin_preference:      'economy',
        constraints: {
          max_travel_hours:   hours,
          max_stops:          1,
          nonstop_preferred:  false,
        },
        balances: buildBalances(selectedPrograms, badgeBalances),
      });
      const recs = await generateRecommendations(trip.id);
      setBundle(recs);
      setStep('results');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Request failed');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenPlaybook = async (optionId: string) => {
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

  const handleNewSearch = () => {
    setBundle(null);
    setPlaybook(null);
    setStep('search');
  };

  const handleBackToResults = () => {
    setStep('results');
  };

  return (
    <main className="relative min-h-screen overflow-x-hidden">
      {/* ── Background ── */}
      <div className="pp-bg" />

      {/* ── Nav ── */}
      <nav className="relative z-10 flex items-center justify-between px-8 md:px-12 py-5 border-b border-white/10 bg-[rgba(13,17,23,0.7)] backdrop-blur-[12px]">
        {/* Logo */}
        <div className="flex items-center gap-2.5">
          <svg width="34" height="34" viewBox="0 0 34 34" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <circle cx="17" cy="17" r="15.5" fill="rgba(255,255,255,0.1)" stroke="rgba(255,255,255,0.5)" strokeWidth="1.2"/>
            <path d="M17 5 L19.4 15 L17 12.8 L14.6 15 Z" fill="white"/>
            <path d="M17 29 L19.4 19 L17 21.2 L14.6 19 Z" fill="rgba(255,255,255,0.28)"/>
            <path d="M29 17 L19 14.6 L21.2 17 L19 19.4 Z" fill="rgba(255,255,255,0.28)"/>
            <path d="M5 17 L15 14.6 L12.8 17 L15 19.4 Z" fill="rgba(255,255,255,0.28)"/>
            <circle cx="17" cy="17" r="2.2" fill="rgba(255,255,255,0.88)"/>
          </svg>
          <span className="font-sans text-[20px] font-semibold tracking-[-0.03em] text-pri">
            point<em className="font-serif not-italic text-accent text-[22px] tracking-[-0.01em]">pilot.</em>
          </span>
        </div>

        {/* Right side */}
        <div className="flex items-center gap-4">
          {/* Breadcrumb (results / playbook steps) */}
          {step !== 'search' && (
            <div className="hidden sm:flex items-center gap-1 text-[12px] font-semibold">
              <span className="text-white/35">Explore</span>
              <span className="text-white/20 mx-0.5">›</span>
              <span className={step === 'results' ? 'text-pri' : 'text-white/35'}>Discover</span>
              <span className="text-white/20 mx-0.5">›</span>
              <span className={step === 'playbook' ? 'text-pri' : 'text-white/35'}>Capitalize</span>
            </div>
          )}

          <button className="bg-accent text-bg px-[22px] py-[9px] rounded-full text-[14px] font-semibold hover:opacity-85 transition-opacity">
            Sign up
          </button>
        </div>
      </nav>

      {/* ── Page content ── */}
      <div className="relative z-5 max-w-[900px] mx-auto px-6 md:px-12">

        {/* ─── SEARCH step ─── */}
        {step === 'search' && (
          <>
            {/* Hero */}
            <div className="pt-[72px] pb-10">
              <h1 className="font-serif text-[clamp(42px,6vw,68px)] font-semibold leading-[1.08] tracking-[-0.02em] text-pri">
                Fly smarter<br />
                <em className="italic font-normal text-accent">with points.</em>
              </h1>
              <p className="mt-4 text-[17px] text-sec font-light max-w-[480px] leading-relaxed">
                Search award flights across Chase, Amex, Capital One &amp; more — in seconds.
              </p>
            </div>

            <SearchCard
              tripType={tripType}
              searchMode={searchMode}
              travelers={travelers}
              originCodes={originCodes}
              destCodes={destCodes}
              start={start}
              end={end}
              nights={nights}
              hours={hours}
              selectedPrograms={selectedPrograms}
              badgeBalances={badgeBalances}
              loading={loading}
              canSearch={canSearch}
              onTripTypeChange={setTripType}
              onSearchModeChange={setSearchMode}
              onTravelersChange={setTravelers}
              onOriginChange={setOriginCodes}
              onDestChange={setDestCodes}
              onStartChange={setStart}
              onEndChange={setEnd}
              onNightsChange={setNights}
              onHoursChange={setHours}
              onProgramToggle={(id) =>
                setSelectedPrograms((prev) => ({ ...prev, [id]: !prev[id] }))
              }
              onBalanceChange={(id, v) =>
                setBadgeBalances((prev) => ({ ...prev, [id]: v }))
              }
              onSubmit={handleSubmit}
              onSwapAirports={() => {
                const tmp = originCodes;
                setOriginCodes(destCodes);
                setDestCodes(tmp);
              }}
            />
          </>
        )}

        {/* ─── RESULTS step ─── */}
        {step === 'results' && bundle && (
          <div className="py-10">
            <ResultsView
              bundle={bundle}
              loading={loading}
              onOpenPlaybook={handleOpenPlaybook}
              onNewSearch={handleNewSearch}
            />
          </div>
        )}

        {/* ─── PLAYBOOK step ─── */}
        {step === 'playbook' && playbook && (
          <div className="py-10">
            <PlaybookView playbook={playbook} onBack={handleBackToResults} />
          </div>
        )}

        {/* ── Error banner ── */}
        {error && (
          <p className="mt-4 text-[13px] text-red-200 bg-red-900/40 border border-red-300/30 rounded-[12px] p-3">
            {error}
          </p>
        )}

        {/* Spacer */}
        <div className="pb-24" />
      </div>
    </main>
  );
}
