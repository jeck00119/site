import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Function to discover backend port for proxy
async function discoverBackendPort() {
  const possiblePorts = [8000, 8001, 8002, 8003, 8004];
  
  for (const port of possiblePorts) {
    try {
      const response = await fetch(`http://127.0.0.1:${port}/health`, {
        method: 'GET',
        signal: AbortSignal.timeout(1000)
      });
      if (response.ok) {
        console.log(`✅ Backend discovered on port ${port} for Vite proxy`);
        return port;
      }
    } catch (error) {
      // Port not available, try next
    }
  }
  
  console.warn('⚠️ Could not discover backend port for proxy, using default 8000');
  return 8000;
}

// https://vitejs.dev/config/
export default defineConfig(async () => {
  const backendPort = process.env.NODE_ENV === 'development' ? await discoverBackendPort() : 8000;
  
  return {
    plugins: [vue()],
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
              './src/components/cnc/CNC.vue',
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



