import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/websites/', // GitHub Pages subdirectory
  build: {
    outDir: 'dist',
    emptyOutDir: true
  }
})
