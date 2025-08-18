<template>
  <div class="page-container">
    <div class="nav-container">
      <the-navigator @visibility-changed="onNavVisibilityChanged"></the-navigator>
    </div>
    <div class="body-container" ref="bodyContainer">
      <div class="route-wrapper">
        <router-view v-slot="slotProps">
          <transition name="route" mode="out-in">
            <component :is="slotProps.Component"></component>
          </transition>
        </router-view>
      </div>
    </div>
    <div class="error-list-wrapper">
      <the-footer :nav-is-open="navIsOpen"></the-footer>
    </div>
  </div>
</template>


<script>
import { computed, onMounted, onUnmounted, watch, ref, nextTick } from 'vue';
import { useRouter } from 'vue-router'; 
import { v4 as uuidv4 } from 'uuid';
import { useWebSocket, useAuthStore, useConfigurationsStore, useAlgorithmsStore, useImageSourcesStore, useComponentsStore } from '@/composables/useStore';
import { logger } from '@/utils/logger';
import { addErrorToStore } from '@/utils/errorHandler';

import TheNavigator from './components/layout/TheNavigator.vue';
import TheFooter from './components/layout/TheFooter.vue';
import { ipAddress, port } from "./url.js";
export default {
  components: {
    TheNavigator,
    TheFooter
  },

  setup() {
    const router = useRouter();
    const route = router.currentRoute;
    const navIsOpen = ref(false);
    const bodyContainer = ref(null);
    
    // Use centralized store composables
    const { isAuthenticated, tryLogin, didAutoLogout } = useAuthStore();
    const { 
      currentConfiguration,
      tryLoadConfiguration,
      setCurrentConfiguration,
      dispatch: dispatchConfig
    } = useConfigurationsStore();
    const { loadAlgorithms, loadReferenceAlgorithms, loadConfiguredAlgorithms, loadBasicAlgorithms } = useAlgorithmsStore();
    const { loadImageSources } = useImageSourcesStore();
    const { loadComponents } = useComponentsStore();

    let configurationSocket = null; // Will hold the WebSocket composable instance
    let ws_uid = null;

    // didAutoLogout now comes from useAuthStore composable
    
    // For error handling until errors store is fully migrated
    const { store } = useAuthStore();

    watch(didAutoLogout, (current, old) => {
      if(current && current !== old)
      {
        logger.info('Auto logout detected, redirecting to login');
        router.replace('/login');
      }
    });

    function connectToSocket() {
      try {
        ws_uid = uuidv4();
        // Use secure WebSocket protocol based on current page protocol
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${ipAddress}:${port}/configurations/configuration_changes/${ws_uid}/ws`;
        
        logger.webSocket('connecting', { url: wsUrl, uid: ws_uid });
        
        // Use centralized WebSocket composable
        configurationSocket = useWebSocket(wsUrl, {
          autoConnect: true,
          reconnectAttempts: 5,
          reconnectInterval: 3000,
          onOpen: onConfigurationSocketOpen,
          onMessage: configurationChanged
        });
      } catch (error) {
        logger.error('Failed to connect to configuration socket', error);
        addErrorToStore(store, 'Connection Error', error);
      }
    }

    function disconnectFromSocket() {
      try {
        if(configurationSocket)
        {
          logger.webSocket('disconnecting', { uid: ws_uid });
          
          dispatchConfig("configurations/closeConfigurationChangedSocket", {
            uid: ws_uid
          });
          
          configurationSocket.disconnect();
          configurationSocket = null;
          ws_uid = null;
          
          logger.webSocket('disconnected');
        }
      } catch (error) {
        logger.warn('Error during socket disconnection', error);
      }
    }

    function onConfigurationSocketOpen() {
      if(configurationSocket && configurationSocket.isConnected.value) {
        logger.webSocket('open', { uid: ws_uid });
        configurationSocket.send('eses');
      }
    }

    async function configurationChanged(event) {
      try {
        let msg = JSON.parse(event.data);
        logger.webSocket('message', { type: 'configuration_changed', data: msg });
        setCurrentConfiguration(msg.configuration);
        
        // Reload configuration-specific data when configuration changes
        logger.debug('Configuration changed, reloading algorithms and data');
        await loadConfigurationData();
      } catch (error) {
        logger.error('Failed to process configuration change message', error);
      }
    }

    async function loadConfigurationData() {
      try {
        logger.debug('Loading all data for selected configuration');
        
        // Load all configuration-specific data in parallel
        logger.debug('Starting to load components with authentication...');
        const promises = [
          loadAlgorithms().catch(err => logger.error('Failed to load algorithms:', err)),
          loadReferenceAlgorithms().catch(err => logger.error('Failed to load reference algorithms:', err)),
          loadImageSources().catch(err => logger.error('Failed to load image sources:', err)),
          loadConfiguredAlgorithms().catch(err => logger.error('Failed to load configured algorithms:', err)),
          loadBasicAlgorithms().catch(err => logger.error('Failed to load basic algorithms:', err)),
          // Load components for all types (component, reference, etc.)
          loadComponents({ type: 'component' }).then(() => logger.debug('Components loaded successfully')).catch(err => logger.error('Failed to load components:', err)),
          loadComponents({ type: 'reference' }).then(() => logger.debug('Reference components loaded successfully')).catch(err => logger.error('Failed to load reference components:', err))
        ];
        // Loading data promises - debug removed to reduce log spam
        await Promise.all(promises);
        
        logger.info('All data loaded successfully for configuration');
        
        // Connect to WebSocket for configuration changes if not already connected
        if (!configurationSocket) {
          connectToSocket();
        }
      } catch (error) {
        logger.error('Failed to load configuration data', error);
        addErrorToStore(store, 'Configuration Load Error', error);
      }
    }

    async function onLoad() {
      try {
        logger.lifecycle('loading', 'Starting application initialization');
        
        // Only try to load configuration if user is authenticated
        if (isAuthenticated.value) {
          logger.debug('User is authenticated, attempting to load any saved configuration');
          await tryLoadConfiguration();
          // Temporarily disabled due to CORS issues - will re-enable after backend fix
          // store.dispatch("log/loadEvents");

          const configuration = currentConfiguration.value;

          if(configuration) {
            logger.debug('Found saved configuration, loading associated data');
            await loadConfigurationData();
          } else {
            logger.debug('No saved configuration found, user will need to select one manually');
          }
        } else {
          logger.debug('User not authenticated, skipping configuration and WebSocket setup');
        }
        
        logger.lifecycle('loaded', 'Application initialization completed');
      } catch (error) {
        logger.error('Failed to initialize application', error);
        addErrorToStore(store, 'Initialization Error', error);
      }
    }

    function onNavVisibilityChanged(isVisible) {
      navIsOpen.value = isVisible;
      // Navigation visibility changed - debug removed to reduce log spam
    }

    tryLogin();

    function adjustBodyHeight() {
      const bodyContainerEl = bodyContainer.value || document.querySelector('.body-container');
      const routeWrapper = document.querySelector('.route-wrapper');
      const footer = document.querySelector('.error-list-wrapper');
      
      if (bodyContainerEl && routeWrapper && footer) {
        // Reset padding to measure natural content
        routeWrapper.style.paddingBottom = '0';
        
        // Get the natural content height and viewport info
        const contentHeight = routeWrapper.scrollHeight;
        const viewportHeight = window.innerHeight;
        const footerHeight = footer.offsetHeight;
        
        // Calculate how much space we need
        let bottomPadding = 0;
        
        if (contentHeight <= viewportHeight - footerHeight) {
          // Short content - only need minimal clearance
          bottomPadding = Math.max(20, footerHeight * 0.3); // 20px minimum or 30% of footer
        } else {
          // Long content - need enough space to scroll past footer
          bottomPadding = footerHeight + 20; // Footer height + 20px buffer
        }
        
        // Modern scrollbar solution: let scrollbar-gutter handle space reservation
        // No need to dynamically hide/show scrollbars - prevents layout shifts
        
        // Apply the calculated padding
        routeWrapper.style.paddingBottom = `${bottomPadding}px`;
        
        // Set body container height to match content + padding
        const totalHeight = Math.max(contentHeight + bottomPadding, viewportHeight);
        bodyContainerEl.style.minHeight = `${totalHeight}px`;
        
        // Layout adjusted - debug removed to reduce log spam
      }
    }

    // Watch for route changes to adjust height and scroll to top
    watch(route, () => {
      // Scroll to top immediately when route changes
      window.scrollTo({
        top: 0,
        left: 0,
        behavior: 'smooth' // Smooth scroll to top
      });
      
      nextTick(() => {
        setTimeout(adjustBodyHeight, 100); // Small delay to let content render
      });
    });

    onMounted(() => {
      // App component mounted - debug removed to reduce log spam
      onLoad();
      
      // Adjust height initially and on resize
      setTimeout(adjustBodyHeight, 200); // Initial delay for content to load
      
      // Adjust height when window resizes
      window.addEventListener('resize', adjustBodyHeight);
      
      // Also adjust when content changes (but with throttling to avoid infinite loops)
      let adjustTimeout;
      const observer = new ResizeObserver(() => {
        clearTimeout(adjustTimeout);
        adjustTimeout = setTimeout(adjustBodyHeight, 150);
      });
      observer.observe(document.body);
      
    });

    onUnmounted(() => {
      try {
        logger.lifecycle('unmounting', 'App component unmounting');
        disconnectFromSocket();
        logger.lifecycle('unmounted', 'App component unmounted');
      } catch (error) {
        logger.warn('Error during component unmounting', error);
      }
    });

    return {
      navIsOpen,
      onNavVisibilityChanged,
      bodyContainer
    };
  }
}
</script>

<style src="vue-multiselect/dist/vue-multiselect.css"></style>

<style scoped>
.page-container {
  width: 100%;
  min-height: 100vh;
  padding: 0;
  position: relative;
}

.body-container {
  width: 100%;
  min-height: 100vh;
  padding: 0;
  background-color: rgb(53, 53, 53); /* Match body background */
}

.route-wrapper {
  width: 95%;
  margin: 0 0 0 4%; /* Adjusted to 4% - middle ground between 3% and 5% */
  padding: 0; /* JavaScript will set bottom padding dynamically */
  overflow: visible;
  box-sizing: border-box;
}

.error-list-wrapper {
  position: fixed;
  bottom: 0;
  left: 0;
  height: 7vh;
  width: 100%;
  background-color: black;
  color: white;
  z-index: 1000;
}

.route-enter-from {
  opacity: 0;
  transform: translateY(-30px);
}

.route-leave-to {
  opacity: 0;
  transform: translateY(30px);
}

.route-enter-to,
.route-leave-from {
  opacity: 1;
  transform: translateY(0);
}

.route-enter-active {
  transition: all 0.3s ease-out;
}

.route-leave-active {
  transition: all 0.3s ease-in;
}
</style>
