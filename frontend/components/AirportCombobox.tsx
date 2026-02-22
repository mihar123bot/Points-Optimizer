'use client';

import { useMemo, useState } from 'react';
import { Tag } from './ui/Tag';
import { AIRPORTS } from '@/lib/constants';

interface AirportComboboxProps {
  label: string;
  selected: string[];
  onChange: (codes: string[]) => void;
  placeholder?: string;
}

export function AirportCombobox({
  label,
  selected,
  onChange,
  placeholder = 'City or airport…',
}: AirportComboboxProps) {
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

  return (
    <div className="relative">
      <div className="text-[11px] font-semibold tracking-[0.08em] uppercase text-mut mb-2">
        {label}
      </div>

      {/* Tag + text input row */}
      <div className="pp-airport-wrap">
        {selected.map((code) => (
          <Tag
            key={code}
            label={code}
            onRemove={() => onChange(selected.filter((c) => c !== code))}
          />
        ))}
        <input
          className="flex-1 bg-transparent border-none outline-none text-pri font-sans text-[14px] min-w-[80px] placeholder:text-mut"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setOpen(true);
          }}
          onFocus={() => setOpen(true)}
          onBlur={() => setTimeout(() => setOpen(false), 150)}
          placeholder={selected.length === 0 ? placeholder : ''}
        />
      </div>

      {/* Dropdown */}
      {open && filtered.length > 0 && (
        <div className="absolute top-[calc(100%+6px)] left-0 right-0 bg-[#1a2233] border border-white/[0.15] rounded-[12px] shadow-dropdown z-50 overflow-hidden">
          {filtered.map((a) => (
            <button
              key={a.code}
              type="button"
              onMouseDown={() => select(a.code)}
              className={`flex items-center gap-2.5 w-full px-3.5 py-2.5 bg-transparent border-none cursor-pointer text-left transition-colors font-sans
                hover:bg-white/[0.07] ${selected.includes(a.code) ? 'bg-white/[0.07]' : ''}`}
            >
              <span className="text-[14px] font-bold text-accent min-w-[36px]">{a.code}</span>
              <span className="text-[12px] text-sec truncate">
                {a.name} · {a.city}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
