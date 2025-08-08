/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // X.com inspired dark mode palette
        'tm-bg': '#000000',
        'tm-bg-elevated': '#16181c',
        'tm-surface': '#202327',
        'tm-text': '#e7e9ea',
        'tm-text-muted': '#71767b',
        'tm-text-secondary': '#536471',
        'tm-primary': '#e11d48',
        'tm-primary-700': '#9f1239',
        'tm-accent': '#ffffff',
        'tm-border': '#2f3336',
        'tm-border-light': 'rgba(255,255,255,0.08)',
        'tm-hover': 'rgba(231,233,234,0.03)',
        'tm-hover-accent': 'rgba(29,155,240,0.1)',
        'tm-success': '#00ba7c',
        'tm-warning': '#ffd400',
      },
      fontFamily: {
        'inter': ['Inter', 'system-ui', 'sans-serif'],
      },
      backdropBlur: {
        'xs': '2px',
      }
    },
  },
  plugins: [],
}