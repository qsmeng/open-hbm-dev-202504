import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import compression from 'vite-plugin-compression';
import path from 'path';

export default defineConfig({
  plugins: [
    vue(),
    compression({
      algorithm: 'gzip',
      ext: '.gz',
      deleteOriginFile: false
    })
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    },
    extensions: ['.ts', '.js', '.vue', '.json']
  },
  optimizeDeps: {
    include: [
      'vue',
      'vue-router',
      'axios',
      'fast-deep-equal',
      'dayjs'
    ]
  },
  build: {
    chunkSizeWarningLimit: 1000,
    rollupOptions: {
      output: {
        manualChunks: {
          'vue-core': ['vue', 'vue-router'],
          'axios': ['axios'],
          'utils': ['fast-deep-equal', 'dayjs']
        }
      }
    }
  }
});