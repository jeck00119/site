<template>
  <div class="feedrate-grid">
    <div class="state-wrapper">
      <div class="state">State: {{ displayState }}</div>
      <div class="connection-status">
        {{ connectionStatus }}
        <button 
          class="button-websocket"
          @click="reconnectWebSocket"
          :disabled="isReconnecting"
        >
          <div>
            <font-awesome-icon 
              :icon="isReconnecting ? 'spinner' : 'arrows-rotate'" 
              :spin="isReconnecting"
            />
          </div>
        </button>
      </div>
    </div>
    
    <div class="feedrate-section">
      <div class="feedrate-control">
        <div class="feedrate-label">Feedrate:</div>
        <div class="feedrate-input">
          <input
            id="feedrate"
            type="number"
            min="1"
            step="1"
            :value="feedrate"
            @input="updateFeedrate"
            @blur="validateFeedrate"
          />
        </div>
      </div>
      
      <div class="feedrate-info">
        <div class="max-feedrate-label">
          Max X/Y/Z feedrate:
        </div>
        <div class="max-feedrate-val">
          {{ maxFeedrate || '-' }}
        </div>
      </div>
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
    feedrate: {
      type: [String, Number],
      required: true
    },
    connectionStatus: {
      type: String,
      default: "Disconnected"
    }
  },
  emits: ['feedrate-changed', 'reconnect-requested'],
  setup(props, { emit }) {
    const store = useStore();
    const isReconnecting = ref(false);
    const maxFeedrate = ref(null);

    const displayState = computed(() => {
      const state = store.getters["cnc/cncState"](props.axisUid);
      return state ? state.toUpperCase() : 'UNKNOWN';
    });

    // Watch for state changes to update max feedrate
    watch(displayState, (newState) => {
      if (newState === 'IDLE') {
        // Could fetch max feedrate from CNC settings here
        // For now, using a placeholder
        maxFeedrate.value = "1000";
      }
    });

    function updateFeedrate(event) {
      const value = parseInt(event.target.value);
      if (!isNaN(value) && value > 0) {
        emit('feedrate-changed', value);
      }
    }

    function validateFeedrate(event) {
      const value = parseInt(event.target.value);
      if (isNaN(value) || value < 1) {
        // Reset to previous valid value
        event.target.value = props.feedrate;
      } else if (value > 10000) {
        // Cap at reasonable maximum
        event.target.value = 10000;
        emit('feedrate-changed', 10000);
      }
    }

    async function reconnectWebSocket() {
      if (isReconnecting.value) return;
      
      try {
        isReconnecting.value = true;
        emit('reconnect-requested');
        
        // Add a delay to show the spinner
        await new Promise(resolve => setTimeout(resolve, 1000));
        
      } finally {
        isReconnecting.value = false;
      }
    }

    return {
      displayState,
      maxFeedrate,
      isReconnecting,
      updateFeedrate,
      validateFeedrate,
      reconnectWebSocket
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

.state-wrapper {
  display: flex;
  width: 100%;
  margin-bottom: 1rem;
  align-items: center;
}

.state {
  display: flex;
  width: 70%;
  justify-content: flex-start;
  margin-left: 5%;
  font-size: 1.2rem;
  font-weight: bold;
  align-items: center;
  overflow: hidden;
  white-space: nowrap;
}

.connection-status {
  display: flex;
  width: 30%;
  justify-content: flex-end;
  align-items: center;
  font-size: 0.6rem;
  gap: 0.2rem;
  flex-shrink: 0;
  overflow: hidden;
}

.button-websocket {
  background-color: rgb(41, 41, 41);
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.2rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
  height: 28px;
  flex-shrink: 0;
  font-size: 0.8rem;
}

.button-websocket:hover:not(:disabled) {
  background-color: rgb(61, 61, 61);
  transform: scale(1.05);
}

.button-websocket:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.feedrate-section {
  display: flex;
  flex-direction: column;
  width: 100%;
  gap: 1rem;
}

.feedrate-control {
  display: flex;
  justify-content: space-around;
  align-items: center;
}

.feedrate-info {
  display: flex;
  justify-content: space-around;
  align-items: center;
}

.feedrate-label {
  width: 40%;
  margin-left: 10%;
  display: flex;
  justify-content: flex-start;
  font-weight: bold;
}

.feedrate-input {
  width: 50%;
}

#feedrate {
  width: 90%;
  background-color: rgb(41, 41, 41);
  border: none;
  color: white;
  text-align: center;
  border-radius: 4px;
  padding: 0.5rem;
  font-size: 1rem;
}

#feedrate:focus {
  outline: 2px solid rgb(204, 161, 82);
  background-color: rgb(51, 51, 51);
}

.max-feedrate-label {
  width: 40%;
  margin-left: 10%;
  display: flex;
  justify-content: flex-start;
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.max-feedrate-val {
  width: 50%;
  text-align: center;
  font-weight: bold;
  color: rgb(204, 161, 82);
}
</style>

