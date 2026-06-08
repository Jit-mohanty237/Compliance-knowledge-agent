/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: 'var(--background)',
        card: 'var(--card)',
        brand: {
          DEFAULT: 'var(--brand)',
          hover: 'var(--brand-hover)',
          text: 'var(--brand-text)',
        },
        'text-primary': 'var(--text-primary)',
        'text-secondary': 'var(--text-secondary)',
        border: 'var(--border)',
        
        // Keep compliance colors in case they're used by subcomponents
        compliance: {
          50: '#f0f7ff',
          100: '#e0effe',
          200: '#bae2fd',
          300: '#7cc8fc',
          400: '#38a9f8',
          500: '#0e8de6',
          600: '#026fc1',
          700: '#03589c',
          800: '#074b80',
          900: '#0c3f6b',
          950: '#082847',
        }
      },
      boxShadow: {
        soft: 'var(--shadow-soft)',
        elevated: 'var(--shadow-elevated)',
      },
      borderRadius: {
        bubble: 'var(--radius-bubble)',
        chip: 'var(--radius-chip)',
      }
    },
  },
  plugins: [],
}
