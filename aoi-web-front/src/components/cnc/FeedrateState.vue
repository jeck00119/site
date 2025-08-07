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
import { ref, computed, watch } from "vue";
import { useStore } from "vuex";

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
    const store = useStore();
    const isConnecting = ref(false);

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
      const state = store.getters["cnc/cncState"](props.axisUid);
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
      console.log(`CNC ${props.axisUid} firmware: ${newType}`);
    });


    async function toggleConnection() {
      if (isConnecting.value) return;
      
      try {
        isConnecting.value = true;
        
        if (isConnected.value) {
          // Disconnect
          emit('disconnect-requested');
        } else {
          // Connect
          emit('connect-requested');
        }
        
        // Add a delay to show the connecting state
        await new Promise(resolve => setTimeout(resolve, 1000));
        
      } finally {
        isConnecting.value = false;
      }
    }

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
  color: white;
  justify-content: space-around;
  align-items: center;
  display: flex;
  flex-direction: column;
  width: 100%;
  border-radius: 8px;
  padding: 0.5rem;
}


.state {
  font-size: 1.3rem;
  font-weight: bold;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  text-align: center;
}

.state-section {
  display: flex;
  justify-content: center;
  width: 100%;
  padding: 0.5rem;
}

.connection-section {
  display: flex;
  justify-content: center;
  width: 100%;
  padding: 0.5rem;
}

.section-divider {
  border: none;
  height: 1px;
  background-color: rgba(255, 255, 255, 0.2);
  margin: 0.5rem 0;
  width: 100%;
}

.connection-controls {
  display: flex;
  justify-content: center;
  align-items: center;
}




.button-connect {
  background-color: rgb(61, 61, 61);
  color: white;
  border: 1px solid rgb(81, 81, 81);
  border-radius: 8px;
  padding: 0.8rem 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 1.1rem;
  font-weight: bold;
  min-width: 120px;
  height: 45px;
}

.button-connect:hover:not(:disabled) {
  background-color: rgb(71, 71, 71);
  transform: translateY(-1px);
}

.button-connect.connected {
  background-color: #F44336;
  border-color: #d32f2f;
}

.button-connect.connected:hover:not(:disabled) {
  background-color: #d32f2f;
}

.button-connect:not(.connected):hover:not(:disabled) {
  background-color: #4CAF50;
  border-color: #45a049;
}

.button-connect:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.firmware-section {
  display: flex;
  flex-direction: column;
  width: 100%;
  gap: 0.5rem;
}

.firmware-info {
  display: flex;
  align-items: center;
  padding: 0 0.5rem;
  gap: 0.5rem;
}

.firmware-version {
  display: flex;
  align-items: center;
  padding: 0 0.5rem;
  gap: 0.5rem;
}

.firmware-label {
  font-weight: bold;
  font-size: 1rem;
  white-space: nowrap;
}

.firmware-value {
  font-weight: bold;
  color: rgb(224, 181, 102);
  font-size: 1.1rem;
}

.version-label {
  font-size: 0.9rem;
  white-space: nowrap;
}

.version-value {
  font-weight: bold;
  color: rgb(204, 161, 82);
  font-size: 0.9rem;
}

/* CNC State Colors */
.state-idle {
  color: #4CAF50 !important; /* Green - Ready */
}

.state-running {
  color: #2196F3 !important; /* Blue - Active */
}

.state-hold {
  color: #FF9800 !important; /* Orange - Paused */
}

.state-jog {
  color: #9C27B0 !important; /* Purple - Manual movement */
}

.state-alarm {
  color: #F44336 !important; /* Red - Error/Alarm */
}

.state-door {
  color: #FF5722 !important; /* Deep Orange - Safety door */
}

.state-check {
  color: #FFEB3B !important; /* Yellow - Check mode */
}

.state-home {
  color: #00BCD4 !important; /* Cyan - Homing */
}

.state-sleep {
  color: #9E9E9E !important; /* Gray - Sleep mode */
}

.state-unknown {
  color: #795548 !important; /* Brown - Unknown state */
}


/* Pulsing animation for connecting status */
@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}
</style>

