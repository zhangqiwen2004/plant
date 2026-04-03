import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const backendTarget = env.VITE_BACKEND_ORIGIN || 'http://127.0.0.1:8000'

  return {
    plugins: [vue()],
    server: {
      port: 3000,
      proxy: {
        '/api': {
          target: backendTarget,
          changeOrigin: true,
        },
        '/media': {
          target: backendTarget,
          changeOrigin: true,
        }
      }
    }
  }
})
