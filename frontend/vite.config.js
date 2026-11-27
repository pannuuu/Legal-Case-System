import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const BACKEND_PROXY = {
  '/api': {
    target: 'http://127.0.0.1:8000',
    changeOrigin: true,
  },
  '/health': {
    target: 'http://127.0.0.1:8000',
    changeOrigin: true,
  },
};

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: BACKEND_PROXY,
  },
  preview: {
    port: 4173,
    proxy: BACKEND_PROXY,
  },
});
