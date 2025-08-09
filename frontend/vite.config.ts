import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      onwarn(warning, warn) {
        // Ignore TypeScript warnings during build for deployment
        if (warning.code === 'UNRESOLVED_IMPORT' || warning.message.includes('TS')) return;
        warn(warning);
      }
    }
  }
})
