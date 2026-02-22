'use client';

import { RecommendationBundle } from '@/lib/types';
import { FlightResultCard } from './FlightResultCard';

interface ResultsViewProps {
  bundle: RecommendationBundle;
  loading: boolean;
  onOpenPlaybook: (id: string) => void;
  onNewSearch: () => void;
}

export function ResultsView({ bundle, loading, onOpenPlaybook, onNewSearch }: ResultsViewProps) {
  const isCash = bundle.options?.[0]?.search_mode === 'cash';

  return (
    <section>
      {/* ── Header ── */}
      <div className="flex items-center justify-between mb-5">
        <div>
          <h2 className="font-serif text-[28px] font-semibold text-pri leading-tight">
            Discover
          </h2>
          <p className="text-[14px] text-sec mt-0.5">
            {isCash ? 'Sorted by lowest total cost' : 'Sorted by best points value'}
          </p>
        </div>

        <button
          onClick={onNewSearch}
          className="
            flex items-center gap-2 px-4 py-2.5 rounded-full
            bg-white/[0.08] border border-white/[0.15] text-sec
            hover:text-pri hover:bg-white/[0.12] hover:border-white/25
            text-[13px] font-medium transition-all duration-150 cursor-pointer
          "
        >
          ← New Search
        </button>
      </div>

      {/* ── Result cards grid ── */}
      {bundle.options?.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {bundle.options.map((o) => {
            const isBestBalanced = bundle.winner_tiles?.best_balanced === o.id;
            const isBestCpp      = !isBestBalanced && bundle.winner_tiles?.best_cpp  === o.id;
            const isBestPrice    = !isBestBalanced && !isBestCpp && bundle.winner_tiles?.best_oop === o.id;
            const badge = isBestBalanced ? 'Best Balanced'
                        : isBestCpp      ? 'Best CPP'
                        : isBestPrice    ? 'Best Price'
                        : null;
            return (
              <FlightResultCard
                key={o.id}
                option={o}
                badge={badge}
                loading={loading}
                onOpenPlaybook={onOpenPlaybook}
              />
            );
          })}
        </div>
      ) : (
        <div className="text-center py-16 text-sec">
          <p className="text-[18px] font-medium mb-2">No results found</p>
          <p className="text-[14px] text-mut">Try adjusting your dates, destinations, or programs.</p>
        </div>
      )}
    </section>
  );
}
