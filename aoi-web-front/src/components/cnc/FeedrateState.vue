<template>
  <div class="feedrate-grid">
    <!-- Firmware Section -->
    <div class="firmware-section">
      <div class="firmware-info">
        <div class="firmware-label">Firmware:</div>
        <div class="firmware-value">
          {{ firmwareType }}
        </div>
      </div>
      
      <div class="firmware-version" v-if="firmwareVersion">
        <div class="version-label">Version:</div>
        <div class="version-value">
          {{ firmwareVersion }}
        </div>
      </div>
    </div>

    <!-- Horizontal Divider -->
    <hr class="section-divider" />
    
    <!-- Connection Controls -->
    <div class="connection-section">
      <div class="connection-controls">
        <button 
          class="button-connect"
          @click="toggleConnection"
          :disabled="isConnecting"
          :class="{ 'connected': isConnected, 'connecting': isConnecting }"
        >
          <font-awesome-icon 
            :icon="getConnectionIcon" 
          />
          {{ getConnectionText }}
        </button>
      </div>
    </div>

    <!-- Horizontal Divider -->
    <hr class="section-divider" />
    
    <!-- State Section -->
    <div class="state-section">
      <div class="state">State: <span :class="stateColorClass">{{ displayState }}</span></div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from "vue";
import { useCncStore } from '@/composables/useStore';
import { logger } from '@/utils/logger';

export default {
  name: "FeedrateState",
  props: {
    axisUid: {
      type: String,
      required: true
    },
    connectionStatus: {
      type: String,
      default: "Disconnected"
    }
  },
  emits: ['connect-requested', 'disconnect-requested'],
  setup(props, { emit }) {
    const isConnecting = ref(false);
    
    // Use centralized CNC store composable
    const { cncState, dispatch } = useCncStore(props.axisUid);
    const { store } = useCncStore(); // For remaining getters

    const isConnected = computed(() => {
      return props.connectionStatus.toLowerCase() === 'connected';
    });

    const getConnectionIcon = computed(() => {
      if (isConnecting.value) return 'clock';
      return isConnected.value ? 'stop' : 'play';
    });

    const getConnectionText = computed(() => {
      if (isConnecting.value) return 'Connecting...';
      return isConnected.value ? 'Disconnect' : 'Connect';
    });
    
    // Firmware information - get actual firmware from CNC configuration
    const firmwareType = computed(() => {
      const cnc = store.getters["cnc/getCNC"](props.axisUid);
      if (cnc && cnc.type) {
        return cnc.type.toUpperCase();
      }
      return 'UNKNOWN';
    });

    const firmwareVersion = computed(() => {
      // This would typically come from CNC settings or status
      // For now returning a placeholder - you can implement actual version detection
      return null; // or return actual version when available
    });

    const displayState = computed(() => {
      const state = cncState?.value;
      return state ? state.toUpperCase() : 'UNKNOWN';
    });

    // Color classes based on CNC state
    const stateColorClass = computed(() => {
      const state = displayState.value;
      switch(state) {
        case 'IDLE':
          return 'state-idle';
        case 'RUN':
        case 'RUNNING':
          return 'state-running';
        case 'HOLD':
        case 'HOLD:0':
        case 'HOLD:1':
          return 'state-hold';
        case 'JOG':
          return 'state-jog';
        case 'ALARM':
          return 'state-alarm';
        case 'DOOR':
        case 'DOOR:0':
        case 'DOOR:1':
        case 'DOOR:2':
        case 'DOOR:3':
          return 'state-door';
        case 'CHECK':
          return 'state-check';
        case 'HOME':
          return 'state-home';
        case 'SLEEP':
          return 'state-sleep';
        default:
          return 'state-unknown';
      }
    });


    // Watch for firmware changes or updates
    watch(firmwareType, (newType) => {
      logger.info('Firmware type changed', { axisUid: props.axisUid, firmwareType: newType });
    });
    
    watch(displayState, (newState) => {
      logger.debug('CNC state changed', { axisUid: props.axisUid, state: newState });
    });


    async function toggleConnection() {
      if (isConnecting.value) return;
      
      try {
        isConnecting.value = true;
        
        if (isConnected.value) {
          logger.debug('Disconnecting CNC', { axisUid: props.axisUid });
          emit('disconnect-requested');
        } else {
          logger.debug('Connecting CNC', { axisUid: props.axisUid });
          emit('connect-requested');
        }
        
        // Add a delay to show the connecting state
        await new Promise(resolve => setTimeout(resolve, 1000));
        
      } catch (error) {
        logger.error('Connection toggle failed', error);
      } finally {
        isConnecting.value = false;
      }
    }
    
    onMounted(() => {
      logger.lifecycle('mounted', 'FeedrateState component mounted', { axisUid: props.axisUid });
    });

    return {
      displayState,
      stateColorClass,
      firmwareType,
      firmwareVersion,
      isConnecting,
      isConnected,
      getConnectionIcon,
      getConnectionText,
      toggleConnection
    };
  }
};
</script>

<style scoped>
.feedrate-grid {
  color: var(--color-text-secondary);
  justify-content: space-around;
  align-items: center;
  display: flex;
  flex-direction: column;
  width: 100%;
  border-radius: var(--border-radius-lg);
  padding: var(--space-2);
  background-color: var(--cnc-position-bg);
  border: var(--border-width-1) solid var(--cnc-position-border);
}


.state {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  text-align: center;
  color: var(--color-text-secondary);
}

.state-section {
  display: flex;
  justify-content: center;
  width: 100%;
  padding: var(--space-2);
}

.connection-section {
  display: flex;
  justify-content: center;
  width: 100%;
  padding: var(--space-2);
}

.section-divider {
  border: var(--border-width-0);
  height: var(--border-width-1);
  background-color: var(--color-border-secondary);
  margin: var(--space-2) var(--space-0);
  width: 100%;
}

.connection-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--space-2);
}




.button-connect {
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-secondary);
  border: var(--border-width-1) solid var(--color-border-secondary);
  border-radius: var(--border-radius-lg);
  padding: var(--space-3) var(--space-6);
  cursor: pointer;
  transition: var(--transition-button);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  min-width: 120px;
  min-height: var(--touch-target-min);
}

.button-connect:hover:not(:disabled) {
  background-color: var(--color-bg-secondary);
  transform: translateY(-1px);
  box-shadow: var(--shadow-button-hover);
}

.button-connect.connected {
  background-color: var(--color-error);
  border-color: var(--color-error-dark);
}

.button-connect.connected:hover:not(:disabled) {
  background-color: var(--color-error-dark);
}

.button-connect:not(.connected):hover:not(:disabled) {
  background-color: var(--color-success);
  border-color: var(--color-success-dark);
}

.button-connect:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-disabled);
}

.firmware-section {
  display: flex;
  flex-direction: column;
  align-items: center; /* Center the firmware content */
  width: 100%;
  gap: var(--space-2);
}

.firmware-info {
  display: flex;
  align-items: center;
  justify-content: center; /* Center the firmware info */
  padding: var(--space-0) var(--space-2);
  gap: var(--space-2);
}

.firmware-version {
  display: flex;
  align-items: center;
  justify-content: center; /* Center the version info */
  padding: var(--space-0) var(--space-2);
  gap: var(--space-2);
}

.firmware-label {
  font-weight: var(--font-weight-bold);
  font-size: var(--font-size-base);
  white-space: nowrap;
  color: var(--color-text-secondary);
}

.firmware-value {
  font-weight: var(--font-weight-bold);
  color: var(--color-primary-light);
  font-size: var(--font-size-lg);
}

.version-label {
  font-size: var(--font-size-sm);
  white-space: nowrap;
  color: var(--color-text-secondary);
}

.version-value {
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
  font-size: var(--font-size-sm);
}

/* CNC State Colors using design tokens */
.state-idle {
  color: var(--color-success) !important;
}

.state-running {
  color: var(--color-info) !important;
}

.state-hold {
  color: var(--color-warning) !important;
}

.state-jog {
  color: var(--color-primary) !important;
}

.state-alarm {
  color: var(--color-error) !important;
}

.state-door {
  color: var(--color-error-light) !important;
}

.state-check {
  color: var(--color-warning-light) !important;
}

.state-home {
  color: var(--color-info-light) !important;
}

.state-sleep {
  color: var(--color-text-muted) !important;
}

.state-unknown {
  color: var(--color-text-tertiary) !important;
}


/* Pulsing animation for connecting status */
@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.button-connect.connecting {
  animation: pulse 2s infinite;
}
</style>

