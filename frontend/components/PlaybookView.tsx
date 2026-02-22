'use client';

import { PlaybookResponse } from '@/lib/types';

interface PlaybookViewProps {
  playbook: PlaybookResponse;
  onBack: () => void;
}

function StepList({ steps }: { steps: string[] }) {
  return (
    <ol className="space-y-3">
      {steps.map((step, i) => (
        <li key={i} className="flex items-start gap-3 text-[14px] text-sec leading-relaxed">
          <span className="shrink-0 w-[22px] h-[22px] rounded-full bg-white/[0.08] border border-white/[0.15] flex items-center justify-center text-[11px] font-bold text-accent mt-0.5">
            {i + 1}
          </span>
          <span>{step}</span>
        </li>
      ))}
    </ol>
  );
}

export function PlaybookView({ playbook, onBack }: PlaybookViewProps) {
  return (
    <section className="rounded-[20px] bg-[rgba(13,17,23,0.82)] backdrop-blur-[14px] border border-white/[0.08] p-8">
      {/* ── Header ── */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="font-serif text-[28px] font-semibold text-pri">Your Playbook</h2>
        <button
          onClick={onBack}
          className="
            flex items-center gap-2 px-4 py-2.5 rounded-full
            bg-white/[0.08] border border-white/[0.15] text-sec
            hover:text-pri hover:bg-white/[0.12] hover:border-white/25
            text-[13px] font-medium transition-all duration-150 cursor-pointer
          "
        >
          ← Back to Options
        </button>
      </div>

      {/* ── Two-column steps ── */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <p className="text-[11px] font-bold tracking-[0.1em] uppercase text-mut mb-4">
            Transfer Steps
          </p>
          {playbook.transfer_steps.length > 0 ? (
            <StepList steps={playbook.transfer_steps} />
          ) : (
            <p className="text-[13px] text-mut italic">No transfer steps required.</p>
          )}
        </div>

        <div>
          <p className="text-[11px] font-bold tracking-[0.1em] uppercase text-mut mb-4">
            Booking Steps
          </p>
          {playbook.booking_steps.length > 0 ? (
            <StepList steps={playbook.booking_steps} />
          ) : (
            <p className="text-[13px] text-mut italic">No booking steps available.</p>
          )}
        </div>
      </div>

      {/* ── Warnings ── */}
      {playbook.warnings?.length > 0 && (
        <div className="mt-6 p-4 rounded-[12px] bg-deal-fair/[0.08] border border-deal-fair/20">
          <p className="text-[11px] font-bold tracking-[0.1em] uppercase text-deal-fair mb-2">
            Heads Up
          </p>
          <ul className="space-y-1">
            {playbook.warnings.map((w, i) => (
              <li key={i} className="text-[13px] text-deal-fair/80">• {w}</li>
            ))}
          </ul>
        </div>
      )}

      {/* ── Fallbacks ── */}
      {playbook.fallbacks?.length > 0 && (
        <div className="mt-4 p-4 rounded-[12px] bg-white/[0.04] border border-white/[0.08]">
          <p className="text-[11px] font-bold tracking-[0.1em] uppercase text-mut mb-2">
            Fallback Options
          </p>
          <ul className="space-y-1">
            {playbook.fallbacks.map((f, i) => (
              <li key={i} className="text-[13px] text-sec">• {f}</li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
