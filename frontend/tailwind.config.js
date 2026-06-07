/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        dark: { 900: '#0a0a0f', 800: '#12121a', 700: '#1a1a2e', 600: '#2a2a3e' },
        green: { 400: '#22c55e', 500: '#16a34a' },
        red: { 400: '#ef4444', 500: '#dc2626' },
      },
    },
  },
  plugins: [],
}
