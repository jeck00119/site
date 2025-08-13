import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// https://vitejs.dev/config/
export default defineConfig(() => {
  const backendPort = 8000; // Always use port 8000 for backend
  
  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
    server: {
      proxy: {
        '/api': {
          target: `http://127.0.0.1:${backendPort}`,
          changeOrigin: true,
          secure: false,      
          ws: true,
        },
      },
    },
    build: {
      // Bundle optimization settings
      rollupOptions: {
        output: {
          // Manual chunk splitting for better caching
          manualChunks: {
            // Vendor libraries
            'vendor-vue': ['vue', 'vue-router', 'vuex'],
            'vendor-ui': ['@coreui/vue', '@fortawesome/fontawesome-svg-core', '@fortawesome/free-solid-svg-icons', '@fortawesome/vue-fontawesome'],
            'vendor-icons': ['oh-vue-icons'],
            'vendor-utils': ['vue3-uuid', '@imengyu/vue3-context-menu', 'exceljs', 'fabric'],
            
            // Application modules
            'cnc-module': [
              './src/components/cnc/CNCRefactored.vue',
              './src/components/pages/tools/CNCMachine.vue',
              './src/store/cnc/index.js'
            ],
            'camera-module': [
              './src/components/camera/CameraScene.vue',
              './src/store/camera_settings/index.js'
            ],
            'auth-module': [
              './src/components/pages/auth/UserLogin.vue',
              './src/components/pages/auth/UserSignup.vue',
              './src/store/auth/index.js'
            ]
          }
        }
      },
      // Optimize chunk size warnings
      chunkSizeWarningLimit: 1000,
      // Enable source maps for debugging
      sourcemap: process.env.NODE_ENV === 'development'
    },
    // Optimize dependencies
    optimizeDeps: {
      include: [
        'vue',
        'vue-router', 
        'vuex',
        '@coreui/vue',
        '@fortawesome/fontawesome-svg-core',
        '@fortawesome/free-solid-svg-icons',
        '@fortawesome/vue-fontawesome'
      ]
    }
  }
})



