/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Deep premium compliancy branding
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
      }
    },
  },
  plugins: [],
}
