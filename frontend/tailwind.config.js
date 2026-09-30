const { activeTheme } = require('./config/theme');

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './hooks/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-be-vietnam-pro)', 'Inter', 'sans-serif'],
      },
      colors: {
        unicorn: activeTheme.unicorn,
        brand: activeTheme.brand,
        fit: activeTheme.fit,
      },
      borderRadius: {
        '14': '14px',
        '16': '16px',
        '20': '20px',
        '28': '28px',
      },
      boxShadow: activeTheme.shadows,
    },
  },
  plugins: [],
};