/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Core neutral surface system (near-black, faint cool tint)
        'dark-bg': '#08090c',
        'ink': '#08090c',
        'surface': '#0f1116',
        'surface-2': '#161922',
        'card-bg': '#101319',
        'border-color': 'rgba(255,255,255,0.08)',
        'line': 'rgba(255,255,255,0.08)',
        // Text
        'text-main': '#ededf0',
        'text-muted': '#9aa0ad',
        'text-faint': '#616773',
        // Accents (refined, less neon)
        'accent-green': '#34d399',
        'accent-red': '#f87171',
        'accent-gold': '#f5b544',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'Consolas', 'monospace'],
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.5rem',
      },
      boxShadow: {
        'card': '0 1px 0 0 rgba(255,255,255,0.04) inset, 0 12px 40px -12px rgba(0,0,0,0.6)',
        'lift': '0 1px 0 0 rgba(255,255,255,0.06) inset, 0 24px 60px -18px rgba(0,0,0,0.75)',
        'glow-gold': '0 0 0 1px rgba(245,181,68,0.25), 0 18px 50px -20px rgba(245,181,68,0.35)',
      },
      keyframes: {
        fadeUp: {
          '0%': { opacity: '0', transform: 'translateY(14px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        floatSlow: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-8px)' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.35' },
        },
      },
      animation: {
        'fade-up': 'fadeUp 0.6s cubic-bezier(0.22,1,0.36,1) forwards',
        'shimmer': 'shimmer 2.2s linear infinite',
        'float-slow': 'floatSlow 6s ease-in-out infinite',
        'pulse-soft': 'pulseSoft 2.4s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
