/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Trade Watcher theme colors (with purple tint for cohesion)
        'dark-bg': '#0f1115',
        'card-bg': '#1a1d26',
        'text-main': '#e0e0e0',
        'text-muted': '#9ca3b4',
        'accent-green': '#00c853',
        'accent-red': '#ff3d00',
        'accent-gold': '#ffd700',
        'border-color': '#3b3654',
      },
      fontFamily: {
        sans: ['Segoe UI', 'Roboto', 'Helvetica', 'Arial', 'sans-serif'],
        mono: ['Consolas', 'Monaco', 'monospace'],
      },
    },
  },
  plugins: [],
}
