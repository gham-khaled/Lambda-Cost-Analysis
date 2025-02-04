import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Load environment variables based on the mode
  loadEnv(mode, process.cwd());
  return {
    plugins: [react()],
    define: {
      'VITE_API_URL': env.VITE_API_URL,
    }
  }
})
