import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Dev: giao diện ở http://localhost:5173, mọi request /api được chuyển tới backend Python (cổng 8000).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        configure(proxy) {
          proxy.on('error', (_error, _request, response) => {
            if ('writeHead' in response && !response.headersSent) {
              response.writeHead(503, { 'Content-Type': 'application/json; charset=utf-8' });
              response.end(JSON.stringify({ detail: 'Không kết nối được backend ở cổng 8000. Hãy khởi động backend theo hướng dẫn trong README.' }));
            }
          });
        },
      },
    },
  },
});
