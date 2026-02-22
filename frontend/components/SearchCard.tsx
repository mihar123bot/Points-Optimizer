'use client';

import { FormEvent } from 'react';
import { TabGroup } from './ui/TabGroup';
import { TravelerControl } from './ui/TravelerControl';
import { AirportCombobox } from './AirportCombobox';
import { ProgramChip } from './ProgramChip';
import { PROGRAMS } from '@/lib/constants';

interface SearchCardProps {
  tripType: 'roundtrip' | 'oneway';
  searchMode: 'cash' | 'points' | 'mixed';
  travelers: number;
  originCodes: string[];
  destCodes: string[];
  start: string;
  end: string;
  nights: number;
  hours: number;
  selectedPrograms: Record<string, boolean>;
  badgeBalances: Record<string, string>;
  loading: boolean;
  canSearch: boolean;

  onTripTypeChange: (v: 'roundtrip' | 'oneway') => void;
  onSearchModeChange: (v: 'cash' | 'points' | 'mixed') => void;
  onTravelersChange: (v: number) => void;
  onOriginChange: (codes: string[]) => void;
  onDestChange: (codes: string[]) => void;
  onStartChange: (v: string) => void;
  onEndChange: (v: string) => void;
  onNightsChange: (v: number) => void;
  onHoursChange: (v: number) => void;
  onProgramToggle: (id: string) => void;
  onBalanceChange: (id: string, v: string) => void;
  onSubmit: (e: FormEvent) => void;

  onSwapAirports: () => void;
}

const FIELD_LABEL = 'text-[11px] font-semibold tracking-[0.08em] uppercase text-mut mb-2';

export function SearchCard({
  tripType,
  searchMode,
  travelers,
  originCodes,
  destCodes,
  start,
  end,
  nights,
  hours,
  selectedPrograms,
  badgeBalances,
  loading,
  canSearch,
  onTripTypeChange,
  onSearchModeChange,
  onTravelersChange,
  onOriginChange,
  onDestChange,
  onStartChange,
  onEndChange,
  onNightsChange,
  onHoursChange,
  onProgramToggle,
  onBalanceChange,
  onSubmit,
  onSwapAirports,
}: SearchCardProps) {
  const showPrograms = searchMode === 'points' || searchMode === 'mixed';

  return (
    <div
      className="
        bg-[rgba(12,20,35,0.82)] backdrop-blur-[24px] backdrop-saturate-[1.4]
        border border-white/[0.12] rounded-card p-8 shadow-card
      "
    >
      <form onSubmit={onSubmit}>
        {/* ── Top controls row ── */}
        <div className="flex items-center justify-between flex-wrap gap-4 mb-7">
          <TabGroup
            tabs={[
              { value: 'roundtrip', label: 'Round trip' },
              { value: 'oneway',    label: 'One way'    },
            ]}
            value={tripType}
            onChange={(v) => onTripTypeChange(v as 'roundtrip' | 'oneway')}
          />

          <div className="flex items-center gap-3 flex-wrap">
            <TabGroup
              tabs={[
                { value: 'cash',   label: 'Cash'   },
                { value: 'points', label: 'Points' },
                { value: 'mixed',  label: 'Mixed'  },
              ]}
              value={searchMode}
              onChange={(v) => onSearchModeChange(v as 'cash' | 'points' | 'mixed')}
              variant="purple"
            />
            <TravelerControl value={travelers} onChange={onTravelersChange} />
          </div>
        </div>

        {/* ── From / Swap / To row ── */}
        <div className="grid grid-cols-[1fr_auto_1fr] gap-3 items-end mb-5">
          <AirportCombobox
            label="From"
            selected={originCodes}
            onChange={onOriginChange}
            placeholder="City or airport…"
          />

          <button
            type="button"
            onClick={onSwapAirports}
            className="pp-swap-btn w-10 h-10 rounded-full bg-white/[0.11] border border-white/10 flex items-center justify-center text-sec hover:text-pri hover:bg-white/[0.18] cursor-pointer mb-[2px] text-[16px]"
            aria-label="Swap airports"
          >
            ⇄
          </button>

          <AirportCombobox
            label="To"
            selected={destCodes}
            onChange={onDestChange}
            placeholder="Anywhere"
          />
        </div>

        {/* ── Date / Nights / Max hrs row ── */}
        <div
          className={`grid gap-3 items-end mb-5 ${
            tripType === 'roundtrip'
              ? 'grid-cols-[1fr_1fr_1fr_1fr]'
              : 'grid-cols-[1fr_1fr_1fr]'
          }`}
        >
          <div>
            <div className={FIELD_LABEL}>Earliest Depart</div>
            <input
              type="date"
              value={start}
              onChange={(e) => onStartChange(e.target.value)}
              className="pp-date-input"
            />
          </div>

          {tripType === 'roundtrip' && (
            <div>
              <div className={FIELD_LABEL}>Latest Return</div>
              <input
                type="date"
                value={end}
                onChange={(e) => onEndChange(e.target.value)}
                className="pp-date-input"
              />
            </div>
          )}

          <div>
            <div className={FIELD_LABEL}>Nights</div>
            <input
              type="number"
              min={2}
              max={14}
              value={nights}
              onChange={(e) => onNightsChange(Number(e.target.value || 5))}
              className="pp-num-input"
            />
          </div>

          <div>
            <div className={FIELD_LABEL}>Max Hrs</div>
            <input
              type="number"
              min={4}
              max={16}
              value={hours}
              onChange={(e) => onHoursChange(Number(e.target.value || 10))}
              className="pp-num-input"
            />
          </div>
        </div>

        {/* ── Loyalty programs ── */}
        {showPrograms && (
          <div className="mb-6">
            <div className={FIELD_LABEL}>Your loyalty programs</div>
            <div className="flex flex-wrap gap-2">
              {PROGRAMS.map((p) => (
                <ProgramChip
                  key={p.id}
                  id={p.id}
                  label={p.label}
                  color={p.color}
                  selected={!!selectedPrograms[p.id]}
                  balance={badgeBalances[p.id] || ''}
                  onToggle={() => onProgramToggle(p.id)}
                  onBalanceChange={(v) => onBalanceChange(p.id, v)}
                />
              ))}
            </div>
          </div>
        )}

        {/* ── Explore button ── */}
        <button
          type="submit"
          disabled={!canSearch || loading}
          className="pp-explore-btn w-full py-4 rounded-[12px] border-none text-[#0a1520] text-[16px] font-semibold tracking-[0.01em] cursor-pointer transition-all duration-200 shadow-explore flex items-center justify-center gap-2"
          style={{
            background: 'linear-gradient(135deg, #7ec8f4 0%, #5baee8 100%)',
          }}
        >
          {loading ? 'Searching…' : 'Explore Flights →'}
        </button>

        {/* ── Supported programs footer ── */}
        <div className="mt-4 flex items-center justify-center gap-1.5 flex-wrap">
          <span className="text-[11px] text-white/50 mr-1">Supports</span>
          {PROGRAMS.map((p) => (
            <span
              key={p.id}
              className="text-[10px] font-bold tracking-[0.05em] text-white/55 px-2 py-[2px] border border-white/20 rounded-[4px]"
            >
              {p.label}
            </span>
          ))}
        </div>
      </form>
    </div>
  );
}
