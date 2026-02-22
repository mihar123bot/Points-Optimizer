'use client';

import { RecommendationOption } from '@/lib/types';

interface FlightResultCardProps {
  option: RecommendationOption;
  badge: string | null;
  loading: boolean;
  onOpenPlaybook: (id: string) => void;
}

function formatDate(d: string | undefined): string {
  if (!d) return '—';
  const parts = d.split('-');
  if (parts.length !== 3) return d;
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  return `${months[Number(parts[1]) - 1] ?? ''} ${Number(parts[2])}, ${parts[0]}`;
}

function DealBadge({ rating }: { rating: string }) {
  const styles: Record<string, string> = {
    excellent: 'bg-deal-excellent/10 text-deal-excellent border-deal-excellent/25',
    good:      'bg-deal-good/10 text-deal-good border-deal-good/25',
    fair:      'bg-deal-fair/10 text-deal-fair border-deal-fair/25',
    poor:      'bg-deal-poor/10 text-deal-poor border-deal-poor/25',
  };
  return (
    <span className={`inline-block rounded-[6px] px-2 py-0.5 text-[10px] font-bold tracking-widest uppercase border ${styles[rating.toLowerCase()] ?? styles.poor}`}>
      {rating}
    </span>
  );
}

export function FlightResultCard({ option: o, badge, loading, onOpenPlaybook }: FlightResultCardProps) {
  const isCash = o.search_mode === 'cash';
  const pts    = o.points_breakdown?.flight_points;
  const taxes  = o.award_details?.taxes_fees ?? o.points_breakdown?.taxes_fees;
  const cpp    = o.points_breakdown?.flight_cpp ?? o.cpp_flight;

  return (
    <article className="pp-result-card flex flex-col gap-0">
      {/* ── Header: destination + badges ── */}
      <div className="flex items-start justify-between gap-2 mb-3">
        <div className="min-w-0">
          <div className="text-[18px] font-bold text-pri leading-snug">
            {o.city_name || o.destination}
            {o.city_name && (
              <span className="text-[14px] font-medium text-sec ml-1">· {o.destination}</span>
            )}
          </div>
          <div className="text-[13px] text-sec mt-0.5">
            {o.origin} → {o.destination}
            {o.airline  ? ` · ${o.airline}`  : ''}
            {o.duration ? ` · ${o.duration}` : ''}
          </div>
          {(o.depart_date || o.return_date) && (
            <div className="text-[12px] text-mut mt-0.5">
              {formatDate(o.depart_date)}
              {o.return_date ? ` – ${formatDate(o.return_date)}` : ''}
            </div>
          )}
        </div>

        {/* Right badges */}
        <div className="flex flex-col items-end gap-1.5 shrink-0">
          {badge && (
            <span className="inline-flex items-center bg-accent/[0.15] text-accent border border-accent/25 rounded-full px-2.5 py-0.5 text-[11px] font-semibold tracking-[0.03em] whitespace-nowrap">
              {badge}
            </span>
          )}
          {o.valuation && <DealBadge rating={o.valuation.deal_rating} />}
        </div>
      </div>

      {/* ── Divider ── */}
      <div className="h-px bg-white/[0.07] mb-3" />

      {/* ── Pricing ── */}
      {isCash ? (
        <div>
          <div className="text-[22px] font-bold text-pri leading-tight">
            ${o.cash_price_pp ? o.cash_price_pp.toFixed(0) : o.oop_total.toFixed(0)}
            <span className="text-[13px] font-normal text-sec ml-1">/person</span>
          </div>
          <div className="text-[12px] text-mut mt-1">
            ${o.oop_total.toFixed(0)} est. total trip
          </div>
        </div>
      ) : pts ? (
        <div>
          <div className="text-[22px] font-bold text-pri leading-tight">
            {pts.toLocaleString()} pts
            {taxes ? (
              <span className="text-[13px] font-normal text-sec ml-1">
                + ${taxes.toFixed(0)} taxes
              </span>
            ) : null}
          </div>

          {/* CPP range */}
          {o.valuation ? (
            <div className="inline-flex items-center gap-1 bg-deal-excellent/10 text-deal-excellent rounded-[6px] px-2 py-0.5 text-[12px] font-semibold mt-2">
              {o.valuation.cpp_low.toFixed(1)}–{o.valuation.cpp_high.toFixed(1)}¢/pt
              <span className="text-deal-excellent/70 font-normal">
                ({o.valuation.cpp_mid.toFixed(1)}¢ mid)
              </span>
            </div>
          ) : (
            cpp && (
              <div className="inline-flex items-center bg-deal-excellent/10 text-deal-excellent rounded-[6px] px-2 py-0.5 text-[12px] font-semibold mt-2">
                {cpp.toFixed(1)}¢/pt value
              </div>
            )
          )}

          {/* Confidence */}
          {o.valuation && (
            <div className="flex items-center gap-1.5 text-[12px] text-mut mt-1.5">
              <span
                className={`w-[7px] h-[7px] rounded-full shrink-0 ${
                  o.valuation.confidence === 'HIGH'   ? 'bg-deal-excellent' :
                  o.valuation.confidence === 'MEDIUM' ? 'bg-yellow-400'     :
                                                        'bg-red-400'
                }`}
              />
              {o.valuation.confidence} · {o.valuation.score}/100
              {o.no_award_seats && (
                <span className="text-deal-fair/70"> · estimated</span>
              )}
            </div>
          )}

          <div className="text-[12px] text-mut mt-1">
            vs ${o.cash_price_pp ? o.cash_price_pp.toFixed(0) : '—'} cash/person
          </div>
        </div>
      ) : (
        <div className="text-[22px] font-bold text-pri">
          ${o.oop_total.toFixed(0)}
          <span className="text-[13px] font-normal text-sec ml-1">out of pocket</span>
        </div>
      )}

      {/* ── Playbook button ── */}
      <button
        onClick={() => onOpenPlaybook(o.id)}
        disabled={loading}
        className="
          mt-4 w-full py-3 px-4 rounded-[10px] border border-white/[0.15]
          bg-white/[0.07] text-pri text-[14px] font-semibold
          hover:bg-white/[0.12] hover:border-white/25 transition-all duration-150
          disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer
          flex items-center justify-center gap-1.5
        "
      >
        {loading ? 'Loading…' : 'Open Playbook →'}
      </button>
    </article>
  );
}
