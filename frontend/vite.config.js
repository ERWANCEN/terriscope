import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    proxy: {
      '^/api/adresses/(?:\\?|$)': {
        target: 'https://data.geopf.fr',
        changeOrigin: true,
        rewrite: chemin => chemin.replace('/api/adresses/', '/geocodage/search'),
        proxyTimeout: 8000,
        configure(proxy) {
          proxy.on('proxyReq', requete => {
            requete.removeHeader('cookie')
            requete.removeHeader('authorization')
            requete.removeHeader('referer')
          })
        },
      },
      '/api': { target: 'http://backend:8000', changeOrigin: true },
    },
    watch: { usePolling: true },
  },
})
