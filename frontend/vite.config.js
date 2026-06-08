import { defineConfig } from 'vite';
import viteCompression from 'vite-plugin-compression';

export default defineConfig({
  resolve: {
    alias: {
      'react': 'preact/compat',
      'react-dom': 'preact/compat',
      'react-dom/test-utils': 'preact/compat/test-utils',
      'react/jsx-runtime': 'preact/jsx-runtime'
    }
  },
  plugins: [
    viteCompression({
      algorithm: 'brotliCompress',
      ext: '.br'
    })
  ]
});
