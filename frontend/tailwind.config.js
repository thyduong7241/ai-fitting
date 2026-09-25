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
        brand: {
          teal: '#16ABAD',
          'teal-hover': '#1AB8B8',
          'teal-subtle': '#DBF7F5',
          'teal-match': '#1F9C7A',
          navy: '#183247',
          'navy-deep': '#0E1F2E',
          slate: '#425C75',
          muted: '#5C738C',
          subtle: '#708AA5',
          border: '#DFEBEF',
          canvas: '#F6FBFA',
          card: '#FFFFFF',
        },
        fit: {
          perfect: '#1F9C7A',
          tight: '#F59E0B',
          loose: '#0EA5E9',
          extreme: '#EF4444',
        },
      },
      borderRadius: {
        '14': '14px',
        '16': '16px',
        '20': '20px',
        '28': '28px',
      },
      boxShadow: {
        widget: '0 20px 40px -15px rgba(24, 50, 71, 0.15)',
        card: '0 2px 10px rgba(24, 50, 71, 0.04)',
        modal: '0 25px 50px -12px rgba(14, 31, 46, 0.25)',
      },
    },
  },
  plugins: [],
};