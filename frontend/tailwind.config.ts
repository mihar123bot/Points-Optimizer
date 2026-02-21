import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          500: '#3B82F6',
          600: '#2563EB'
        }
      }
    }
  },
  plugins: []
};

export default config;
