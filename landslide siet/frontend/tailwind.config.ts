import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./app/**/*.{js,ts,jsx,tsx,mdx}', './components/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eef7ff',
          500: '#0f766e',
          700: '#115e59',
        },
        risk: {
          low: '#22c55e',
          watch: '#facc15',
          high: '#f97316',
          critical: '#ef4444',
        },
      },
    },
  },
  plugins: [],
};

export default config;
