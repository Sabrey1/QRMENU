import vue from '@vitejs/plugin-vue'
import { defineConfig, loadEnv } from 'vite'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig(({ mode }) => {
  const { API_PROXY_TARGET } = loadEnv(mode, process.cwd(), 'API_PROXY_TARGET')
  return {
    plugins: [tailwindcss(), vue()],
    server: {
      proxy: API_PROXY_TARGET ? { '/v1/api': { target: API_PROXY_TARGET, changeOrigin: false } } : {},
    },
  }
})
