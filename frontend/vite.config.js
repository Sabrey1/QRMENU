import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    tailwindcss(),
    vue()
  ],
  server: {
    proxy: { '/v1/api': 'http://127.0.0.1:8000' },
  },
})
