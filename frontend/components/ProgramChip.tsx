'use client';

interface ProgramChipProps {
  id: string;
  label: string;
  color: string;
  selected: boolean;
  balance: string;
  onToggle: () => void;
  onBalanceChange: (v: string) => void;
}

/**
 * Loyalty program chip — matches HTML reference pill design.
 * When active, shows a balance input beneath the label.
 */
export function ProgramChip({
  label,
  color,
  selected,
  balance,
  onToggle,
  onBalanceChange,
}: ProgramChipProps) {
  return (
    <div
      onClick={onToggle}
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '6px',
        padding: selected ? '8px 14px 10px' : '8px 16px',
        borderRadius: '99px',
        border: selected ? `1px solid ${color}` : '1px solid rgba(255,255,255,0.1)',
        background: selected ? `${color}22` : 'rgba(255,255,255,0.07)',
        cursor: 'pointer',
        transition: 'all 0.2s',
        userSelect: 'none',
      }}
    >
      {/* Label row */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '7px' }}>
        <span
          style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            flexShrink: 0,
            background: selected ? color : 'rgba(255,255,255,0.2)',
            transition: 'background 0.2s',
          }}
        />
        <span
          style={{
            fontSize: '13px',
            fontWeight: 500,
            color: selected ? color : '#8fa3c0',
            transition: 'color 0.2s',
          }}
        >
          {label}
        </span>
      </div>

      {/* Balance input — only when selected */}
      {selected && (
        <input
          type="number"
          placeholder="0 pts"
          value={balance}
          onChange={(e) => {
            e.stopPropagation();
            onBalanceChange(e.target.value);
          }}
          onClick={(e) => e.stopPropagation()}
          style={{
            background: 'rgba(255,255,255,0.1)',
            border: 'none',
            borderRadius: '6px',
            color: '#f0f4ff',
            fontSize: '12px',
            padding: '4px 8px',
            width: '100%',
            outline: 'none',
            fontFamily: 'inherit',
          }}
        />
      )}
    </div>
  );
}
