<template>
  <div class="page-container">
    <div class="nav-container">
      <the-navigator></the-navigator>
    </div>
    <div class="body-container">
      <div style="align-self: center" class="route-wrapper">
        <router-view v-slot="slotProps">
          <transition name="route" mode="out-in">
            <component :is="slotProps.Component"></component>
          </transition>
        </router-view>
      </div>
      <div style="align-self: flex-end" class="error-list-wrapper">
        <the-footer></the-footer>
      </div>
    </div>
  </div>
</template>


<script>
import { computed, onMounted, onUnmounted, watch } from 'vue';
import { useRouter } from 'vue-router'; 
import { uuid } from 'vue3-uuid';
import { useWebSocket, useAuthStore, useConfigurationsStore, useAlgorithmsStore, useImageSourcesStore, useComponentsStore } from '@/composables/useStore';
import { createLogger } from '@/utils/logger';
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
    const logger = createLogger('App');
    
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
        ws_uid = uuid.v4();
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
        logger.debug('All promises created, waiting for resolution...');
        
        logger.debug('Waiting for all data loading promises to resolve...');
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

    tryLogin();

    onMounted(() => {
      logger.lifecycle('mounted', 'App component mounted');
      onLoad();
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
  }
}
</script>

<style src="vue-multiselect/dist/vue-multiselect.css"></style>

<style scoped>
.page-container {
  display: flex;
  flex-direction: column;
  width: 100vw;
  padding: 0;
}

.body-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding: 0;
}

.route-wrapper {
  height: 93vh;
  padding: 0;
  width: 95%;
  margin-left: 3%;
}

.error-list-wrapper {
  height: 7vh;
  width: 100vw;
  background-color: black;
  color: white;
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
