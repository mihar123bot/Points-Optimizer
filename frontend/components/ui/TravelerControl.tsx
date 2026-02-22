'use client';

interface TravelerControlProps {
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
}

/** ± traveler counter pill */
export function TravelerControl({ value, onChange, min = 1, max = 9 }: TravelerControlProps) {
  return (
    <div className="flex items-center gap-2.5 bg-white/[0.07] border border-white/10 rounded-full px-3.5 py-[6px]">
      <button
        type="button"
        onClick={() => onChange(Math.max(min, value - 1))}
        className="w-6 h-6 rounded-full border border-white/20 bg-white/[0.11] text-pri text-base cursor-pointer flex items-center justify-center leading-none hover:bg-white/20 transition-colors"
        aria-label="Remove traveler"
      >
        −
      </button>
      <span className="text-[14px] font-medium text-pri min-w-[70px] text-center">
        {value} Traveler{value > 1 ? 's' : ''}
      </span>
      <button
        type="button"
        onClick={() => onChange(Math.min(max, value + 1))}
        className="w-6 h-6 rounded-full border border-white/20 bg-white/[0.11] text-pri text-base cursor-pointer flex items-center justify-center leading-none hover:bg-white/20 transition-colors"
        aria-label="Add traveler"
      >
        +
      </button>
    </div>
  );
}
