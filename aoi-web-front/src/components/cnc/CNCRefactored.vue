<template>
  <div class="cnc-container">
    <div class="wrapper">
      <!-- Position Display -->
      <div class="positions-section">
        <PositionDisplay 
          :axis-name="axisName" 
          :axis-uid="axisUid" 
        />
      </div>

      <!-- Location Management -->
      <div class="save-section">
        <LocationManagement
          :axis-uid="axisUid"
          :current-position="pos"
          :selected-feedrate="selectedFeedrate"
          @location-saved="onLocationSaved"
          @location-deleted="onLocationDeleted"
        />
      </div>

      <!-- Movement Controls -->
      <div class="movement-section">
        <MovementControls
          :axis-uid="axisUid"
          :selected-steps="selectedSteps"
          :selected-feedrate="selectedFeedrate"
          :is-connected="isConnected"
          @axis-moved="onAxisMoved"
        />
      </div>

      <!-- General Commands -->
      <div class="commands-section">
        <GeneralCommands
          :axis-uid="axisUid"
          :is-connected="isConnected"
          @command-executed="onCommandExecuted"
        />
      </div>

      <!-- Location Shortcuts -->
      <div class="shortcuts-section">
        <LocationShortcuts
          :axis-uid="axisUid"
          :is-connected="isConnected"
          @shortcut-executed="onShortcutExecuted"
          @shortcut-configured="onShortcutConfigured"
        />
      </div>

      <!-- Feedrate and State -->
      <div class="feedrate-section">
        <FeedrateState
          :axis-uid="axisUid"
          :connection-status="webSocketState"
          @connect-requested="handleConnect"
          @disconnect-requested="handleDisconnect"
        />
      </div>

      <!-- Steps Control -->
      <div class="steps-section">
        <StepsControl
          :selected-steps="selectedSteps"
          :feedrate="selectedFeedrate"
          :axis-uid="axisUid"
          :is-connected="isConnected"
          @steps-changed="onStepsChanged"
          @feedrate-changed="onFeedrateChanged"
          @keyboard-move="onKeyboardMove"
        />
      </div>

      <!-- Terminal Console -->
      <div class="terminal-section">
        <TerminalConsole
          :axis-uid="axisUid"
          :terminal-history="ugsTerminalHistory"
          :is-connected="isConnected"
          @command-sent="onTerminalCommand"
          @terminal-cleared="onTerminalCleared"
        />
      </div>
    </div>

    <!-- Cross-platform Port Error Dialog -->
    <base-dialog 
      title="CNC Port Configuration Issue" 
      :show="showPortErrorDialog" 
      height="35vh" 
      @close="closePortErrorDialog"
    >
      <template #default>
        <div class="port-error-content">
          <div class="error-icon">
            <div class="warning-symbol">⚠️</div>
          </div>
          <div class="error-message">
            <h3>Incompatible Port Detected</h3>
            <p><strong>CNC:</strong> {{ portErrorData.cncName }} ({{ portErrorData.type }})</p>
            <p><strong>Port:</strong> {{ portErrorData.port }}</p>
            <div class="error-details">
              <p>{{ portErrorData.error }}</p>
            </div>
            <p class="suggestion">Would you like to update the CNC configuration with a compatible port?</p>
          </div>
        </div>
      </template>
      <template #actions>
        <div class="port-error-actions">
          <base-button width="8vw" @click="closePortErrorDialog">Cancel</base-button>
          <base-button width="10vw" mode="flat" @click="handleSystemSettingsRedirect">
            Update CNC Settings
          </base-button>
        </div>
      </template>
    </base-dialog>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed } from "vue";
import { useRouter } from "vue-router";
import api from "../../utils/api.js";
import { useCncStore, useWebSocket, useLoadingState } from '@/composables/useStore';


// Import child components
import PositionDisplay from "./PositionDisplay.vue";
import LocationManagement from "./LocationManagement.vue";
import MovementControls from "./MovementControls.vue";
import GeneralCommands from "./GeneralCommands.vue";
import LocationShortcuts from "./LocationShortcuts.vue";
import FeedrateState from "./FeedrateState.vue";
import StepsControl from "./StepsControl.vue";
import TerminalConsole from "./TerminalConsole.vue";

export default {
  name: "CNCRefactored",
  components: {
    PositionDisplay,
    LocationManagement,
    MovementControls,
    GeneralCommands,
    LocationShortcuts,
    FeedrateState,
    StepsControl,
    TerminalConsole
  },
  props: {
    axisName: {
      type: String,
      required: true
    },
    axisUid: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const router = useRouter();
    const cncStore = useCncStore(props.axisUid);
    const { isLoading, setLoading, withLoading } = useLoadingState();

    // Reactive state
    const selectedFeedrate = ref(1500);
    const selectedSteps = ref(100);
    const terminalMessages = ref([]);
    const ugsTerminalHistory = computed(() => terminalMessages.value.join('\n'));
    const webSocketState = ref("Disconnected");
    
    // Cross-platform port error dialog state
    const showPortErrorDialog = ref(false);
    const portErrorData = ref({});

    // WebSocket connection
    let socketInstance = null;

    // Computed properties from CNC store
    const { pos, mPos, wPos, cncState, feedrate } = cncStore;
    
    // Computed property for connection state
    const isConnected = computed(() => webSocketState.value === "Connected");

    // Lifecycle hooks
    onMounted(() => {
      initializeComponent();
    });

    onUnmounted(() => {
      try {
        cleanup();
      } catch (error) {
        console.warn('Error during CNCRefactored component unmounting:', error);
      }
    });

    // Initialization
    async function initializeComponent() {
      try {
        // Add position data to store using composable
        await cncStore.dispatch('cnc/addPositionData', {
          uid: props.axisUid
        });

        // Fetch locations using composable
        await cncStore.dispatch('cnc/fetchLocations', props.axisUid);

      } catch (error) {
        console.error("Failed to initialize CNC component:", error);
      }
    }

    // Cleanup
    function cleanup() {
      disconnectFromWs();
    }

    // WebSocket Management
    async function connectToWs() {
      try {
        const wsUrl = await api.getFullUrl(`/cnc/${props.axisUid}/ws`);
        const webSocketUrl = wsUrl.replace('http:', 'ws:');
        
        socketInstance = useWebSocket(webSocketUrl, {
          autoConnect: true,
          onOpen: onCncSocketOpen,
          onClose: onCncSocketClose,
          onError: onCncSocketError,
          onMessage: onCncSocketMsgRecv
        });

      } catch (error) {
        console.error("Failed to connect to WebSocket:", error);
        webSocketState.value = "Error";
      }
    }

    function reconnectToWs() {
      disconnectFromWs();
      setTimeout(async () => {
        await connectToWs();
      }, 1000);
    }

    async function disconnectFromWs() {
      try {
        await cncStore.dispatch('cnc/closeStateSocket', {
          uid: props.axisUid
        });

        if (socketInstance) {
          socketInstance.disconnect();
          socketInstance = null;
        }

      } catch (error) {
        console.error("Error during WebSocket cleanup:", error);
      }
    }

    // WebSocket Event Handlers
    function onCncSocketOpen() {
      // WebSocket is connected, but hardware might not be
      // Don't set state to "Connected" here - wait for hardware confirmation
      console.log("WebSocket connection opened for CNC:", props.axisUid);
      if (socketInstance) {
        socketInstance.send("eses");
      }
    }

    function onCncSocketClose() {
      webSocketState.value = "Disconnected";
    }

    function onCncSocketError() {
      webSocketState.value = "Error";
    }

    function onCncSocketMsgRecv(event) {
      try {
        const msg = JSON.parse(event.data);
        handleSingleMessage(msg);
      } catch (error) {
        console.error("Failed to parse WebSocket message:", error);
      }
    }

    function handleSingleMessage(msg) {
      switch (msg.event) {
        case "on_stateupdate":
          handleStateUpdate(msg);
          break;

        case "on_idle":
          cncStore.setCncState(props.axisUid, msg.message);
          break;

        case "on_read":
          addToConsole(msg.message);
          break;

        case "batch":
          // Handle batched messages
          if (msg.messages && Array.isArray(msg.messages)) {
            msg.messages.forEach(batchedMsg => {
              handleSingleMessage(batchedMsg);
            });
          }
          break;

        case "on_settings_downloaded":
          handleSettingsDownloaded(msg);
          break;

        case "on_error":
          addToConsole(`Error: ${msg.message}`);
          break;

        case "connection_error":
          handleConnectionError(msg);
          break;

        case "connection_success":
          addToConsole(`Connection Success: ${msg.message}`);
          webSocketState.value = "Connected";
          break;

        default:
          console.log("Unhandled WebSocket message:", msg);
      }
    }


    function handleStateUpdate(msg) {
      cncStore.updateCncData(props.axisUid, {
        mPos: msg.mPos,
        wPos: msg.wPos,
        state: msg.state
      });
    }

    function handleSettingsDownloaded(msg) {
      for (const prop in msg.message) {
        addToConsole(`$${prop} = ${msg.message[prop].val}`);
      }
    }

    function addToConsole(message) {
      const timestamp = new Date().toLocaleTimeString();
      terminalMessages.value.push(`[${timestamp}] ${message}`);
      
      // Prevent memory leak by limiting terminal history
      if (terminalMessages.value.length > 1000) {
        terminalMessages.value = terminalMessages.value.slice(-500);
      }
    }

    function handleConnectionError(msg) {
      // Log the connection error to console
      addToConsole(`Connection Error: ${msg.message} - ${msg.error}`);
      
      // Set state to disconnected when hardware connection fails
      webSocketState.value = "Disconnected";
      
      // Show cross-platform port error dialog if applicable
      if (msg.is_cross_platform_issue) {
        portErrorData.value = {
          cncName: msg.name,
          port: msg.port,
          type: msg.type,
          error: msg.error.replace('Cross-platform: ', ''),
          cncUid: msg.cnc_uid
        };
        showPortErrorDialog.value = true;
      }
    }

    function handleSystemSettingsRedirect() {
      router.push('/system-settings');
      showPortErrorDialog.value = false;
    }

    function closePortErrorDialog() {
      showPortErrorDialog.value = false;
      portErrorData.value = {};
    }

    // Event Handlers for Child Components
    function onFeedrateChanged(newFeedrate) {
      selectedFeedrate.value = newFeedrate;
    }

    function onStepsChanged(newSteps) {
      selectedSteps.value = newSteps;
    }

    function onAxisMoved(data) {
      console.log(`Axis ${data.axis} moved ${data.direction} by ${data.step}`);
    }

    function onCommandExecuted(data) {
      if (data.success) {
        addToConsole(`Command executed: ${data.command}`);
      } else {
        addToConsole(`Command failed: ${data.command} - ${data.error}`);
      }
    }

    function onShortcutExecuted(data) {
      addToConsole(`Moving to location: ${data.shortcut.name}`);
    }

    function onShortcutConfigured(data) {
      console.log("Shortcut configured:", data);
    }

    function onLocationSaved(data) {
      addToConsole(`Location saved: ${data.name} (${data.type})`);
    }

    function onLocationDeleted(data) {
      addToConsole(`Location deleted: ${data.locationUid}`);
    }

    function onTerminalCommand(data) {
      addToConsole(`>> ${data.command}`);
    }

    function onTerminalCleared() {
      terminalMessages.value = [];
    }
    
    // Keyboard control handler
    async function onKeyboardMove(moveData) {
      try {
        if (moveData.direction === 'plus') {
          await cncStore.dispatch('cnc/api_increaseAxis', {
            cncUid: moveData.cncUid,
            axis: moveData.axis,
            step: moveData.step,
            feedrate: moveData.feedrate
          });
        } else {
          await cncStore.dispatch('cnc/api_decreaseAxis', {
            cncUid: moveData.cncUid,
            axis: moveData.axis,
            step: moveData.step,
            feedrate: moveData.feedrate
          });
        }
        addToConsole(`Keyboard move: ${moveData.axis.toUpperCase()}${moveData.direction === 'plus' ? '+' : '-'} ${moveData.step} @ ${moveData.feedrate}`);
      } catch (error) {
        addToConsole(`Keyboard move failed: ${error.message}`);
      }
    }

    // Connection handling methods
    async function handleConnect() {
      try {
        // First initialize the CNC in the backend service using composable
        await cncStore.dispatch('cnc/initializeCNC', {
          cncUid: props.axisUid
        });
        
        // Then connect to WebSocket
        await connectToWs();
        
        // Wait a bit for connection result through WebSocket
        await new Promise(resolve => setTimeout(resolve, 500));
        
        addToConsole("CNC initialization attempt completed");
        
      } catch (error) {
        console.error("Failed to initialize CNC:", error);
        addToConsole(`Connection failed: ${error.message}`);
        // Set state to disconnected on error
        webSocketState.value = "Disconnected";
      }
    }

    async function handleDisconnect() {
      try {
        // First disconnect WebSocket
        await disconnectFromWs();
        
        // Then deinitialize the CNC in the backend service using composable
        await cncStore.dispatch('cnc/deinitializeCNC', {
          cncUid: props.axisUid
        });
        
        addToConsole("CNC disconnection and deinitialization completed");
        
      } catch (error) {
        console.error("Failed to disconnect and deinitialize CNC:", error);
        addToConsole(`Disconnection failed: ${error.message}`);
      }
    }

    return {
      // State
      selectedFeedrate,
      selectedSteps,
      ugsTerminalHistory,
      webSocketState,
      showPortErrorDialog,
      portErrorData,
      isLoading,
      
      // Computed from CNC store
      pos,
      mPos,
      wPos,
      cncState,
      feedrate,
      
      // Connection state
      isConnected,
      
      // Methods
      connectToWs,
      disconnectFromWs,
      reconnectToWs,
      handleConnect,
      handleDisconnect,
      handleSystemSettingsRedirect,
      closePortErrorDialog,
      
      // Event handlers
      onFeedrateChanged,
      onStepsChanged,
      onAxisMoved,
      onCommandExecuted,
      onShortcutExecuted,
      onShortcutConfigured,
      onLocationSaved,
      onLocationDeleted,
      onTerminalCommand,
      onTerminalCleared,
      onKeyboardMove
    };
  }
};
</script>

<style scoped>
.cnc-container {
  margin: 1rem 1rem;
  width: 100%;
  border-radius: 12px;
  box-shadow: 0 2px 8px black;
  padding: 0.5rem;
  text-align: center;
  background-color: #515151;
  font-family: "Droid Serif";
  font-size: 1rem;
  font-weight: 700;
  display: flex;
}

.wrapper {
  display: grid;
  align-content: normal;
  gap: 5px;
  width: 100%;
  overflow: hidden;
}

/* Grid Layout - Match original CNC.vue positioning */
.positions-section {
  grid-column: 1/5;
  grid-row: 2/5;
  color: white;
  background-color: #161616;
  border-radius: 8px;
  overflow: hidden;
  padding: 0.5rem;
}

.save-section {
  grid-column: 1;
  grid-row: 5/8;
  color: white;
  background-color: #161616;
  border-radius: 8px;
  overflow: hidden;
  padding: 0.5rem;
}

.movement-section {
  grid-column: 2/5;
  grid-row: 5/8;
  display: flex;
  gap: 5px;
}

.commands-section {
  grid-column: 5/10;
  grid-row: 2/5;
  color: white;
  background-color: #161616;
  border-radius: 8px;
  overflow: hidden;
  padding: 0.5rem;
}

.shortcuts-section {
  grid-column: 10/15;
  grid-row: 5/8;
  color: white;
  background-color: #161616;
  border-radius: 8px;
  overflow: hidden;
  padding: 0.5rem;
}

.feedrate-section {
  grid-column: 10/15;
  grid-row: 2/5;
  color: white;
  background-color: #161616;
  border-radius: 8px;
  overflow: hidden;
  padding: 0.5rem;
}

.steps-section {
  grid-column: 5/10;
  grid-row: 5/8;
  color: white;
  background-color: #161616;
  border-radius: 8px;
  overflow: hidden;
  padding: 0.5rem;
}

.terminal-section {
  grid-column: 15/18;
  grid-row: 2/8;
  color: white;
  background-color: #161616;
  border-radius: 8px;
  overflow: hidden;
  padding: 0.5rem;
}

/* Responsive Design - Match original CNC.vue breakpoints */
@media screen and (max-width: 1300px) {
  .feedrate-section {
    grid-column: 1/5;
    grid-row: 8/11;
  }
  
  .shortcuts-section {
    grid-column: 5/10;
    grid-row: 8/11;
  }
  
  .terminal-section {
    grid-column: 10/14;
    grid-row: 2/11;
  }
}

@media screen and (max-width: 950px) {
  .feedrate-section {
    grid-column: 1/5;
    grid-row: 8/11;
  }
  
  .shortcuts-section {
    grid-column: 5/10;
    grid-row: 8/11;
  }
  
  .terminal-section {
    grid-column: 1/10;
    grid-row: 11/12;
  }
}

/* Port Error Dialog Styles */
.port-error-content {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  color: white;
}

.error-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.warning-symbol {
  font-size: 2.5rem;
  line-height: 1;
}

.error-message {
  flex: 1;
}

.error-message h3 {
  margin: 0 0 1rem 0;
  color: #ff6b6b;
  font-size: 1.2rem;
}

.error-message p {
  margin: 0.5rem 0;
  line-height: 1.4;
}

.error-details {
  background-color: rgba(255, 107, 107, 0.1);
  border-left: 3px solid #ff6b6b;
  padding: 0.75rem;
  margin: 1rem 0;
  border-radius: 4px;
}

.error-details p {
  margin: 0;
  font-style: italic;
}

.suggestion {
  font-weight: bold;
  color: #ffd93d !important;
}

.port-error-actions {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  width: 100%;
  padding: 0 1rem;
}
</style>

