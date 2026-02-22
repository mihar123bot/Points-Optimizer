'use client';

interface TagProps {
  label: string;
  onRemove: () => void;
}

/** Removable airport code pill — e.g. "IAD ×" */
export function Tag({ label, onRemove }: TagProps) {
  return (
    <span className="inline-flex items-center gap-1.5 bg-white/[0.12] text-tagtext border border-white/10 rounded-[6px] px-2 py-0.5 text-[13px] font-medium">
      {label}
      <button
        type="button"
        onClick={onRemove}
        className="text-mut hover:text-pri transition-colors leading-none"
        aria-label={`Remove ${label}`}
      >
        ×
      </button>
    </span>
  );
}
