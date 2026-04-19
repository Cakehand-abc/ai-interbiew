import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    // 设置路径别名，'@' 将永远指向 'src' 目录
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  css: {
    preprocessorOptions: {
      scss: {
        // 全局注入变量文件
        additionalData: `@use "@/styles/main.scss" as *;`
      }
    }
  },
  server: {
    proxy: {
      '/admin': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      },
      '/static': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      },
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  }
});
