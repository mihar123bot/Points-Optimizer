'use client';

interface TabOption {
  value: string;
  label: string;
}

interface TabGroupProps {
  tabs: TabOption[];
  value: string;
  onChange: (value: string) => void;
  /** 'purple' uses purple highlight for the active tab (payment mode) */
  variant?: 'default' | 'purple';
}

/** Pill-shaped tab switcher. variant='purple' for the payment mode row. */
export function TabGroup({ tabs, value, onChange, variant = 'default' }: TabGroupProps) {
  return (
    <div className="flex bg-white/[0.07] rounded-full p-1 gap-0.5 border border-white/10">
      {tabs.map((tab) => {
        const isActive = tab.value === value;
        let activeClass = 'bg-white/[0.15] text-pri shadow-[0_1px_4px_rgba(0,0,0,0.3)]';
        if (isActive && variant === 'purple') {
          activeClass = 'bg-purple text-white shadow-[0_1px_4px_rgba(0,0,0,0.3)]';
        }
        return (
          <button
            key={tab.value}
            type="button"
            onClick={() => onChange(tab.value)}
            className={`px-[18px] py-[7px] rounded-full text-[14px] font-medium transition-all duration-150 border-none cursor-pointer font-sans
              ${isActive ? activeClass : 'bg-transparent text-sec hover:text-pri'}`}
          >
            {tab.label}
          </button>
        );
      })}
    </div>
  );
}
