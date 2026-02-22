import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // Core palette (from HTML reference design)
        bg:      '#0d1117',
        surface: '#161c26',
        accent:  '#7ec8f4',
        purple:  '#a78bfa',
        // Text hierarchy
        pri:     '#f0f4ff',
        sec:     '#8fa3c0',
        mut:     '#556070',
        tagtext: '#d0e4ff',
        // Loyalty program dot colors
        'dot-chase':  '#2563eb',
        'dot-amex':   '#0ea5e9',
        'dot-cap':    '#8b5cf6',
        'dot-delta':  '#c2410c',
        'dot-united': '#1d4ed8',
        'dot-hyatt':  '#0f766e',
        // Deal rating colors
        'deal-excellent': '#4ade80',
        'deal-good':      '#60a5fa',
        'deal-fair':      '#fb923c',
        'deal-poor':      '#9ca3af',
      },
      fontFamily: {
        sans:  ['var(--font-dm-sans)', '"DM Sans"', 'sans-serif'],
        serif: ['var(--font-playfair)', '"Playfair Display"', 'serif'],
      },
      borderRadius: {
        card: '20px',
        DEFAULT: '12px',
        sm:   '8px',
      },
      boxShadow: {
        card:     '0 0 0 1px rgba(255,255,255,0.04), 0 24px 64px rgba(0,0,0,0.6), 0 4px 16px rgba(0,0,0,0.4)',
        explore:  '0 4px 20px rgba(126,200,244,0.25)',
        result:   '0 8px 32px rgba(0,0,0,0.4)',
        dropdown: '0 16px 40px rgba(0,0,0,0.6)',
      },
      backgroundImage: {
        'gradient-explore': 'linear-gradient(135deg, #7ec8f4 0%, #5baee8 100%)',
      },
    },
  },
  plugins: [],
};

export default config;
