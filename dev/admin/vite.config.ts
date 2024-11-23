import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const target = "http://localhost:5000"
// https://vite.dev/config/
export default defineConfig({
  base: "/admin",
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target: target + "/api",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      "/static": {
        target: target + '/static',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/static/,'')
      },
      "/admin/login": {
        target: target + "/admin/login",
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/admin\/login/,'')
      },
      "/admin/singin": {
        target: target + "/admin/singin",
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/admin\/singin/,'')
      },
      "/admin/singout": {
        target: target + "/admin/singout",
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/admin\/singout/,'')
      }
    }
  }
})
