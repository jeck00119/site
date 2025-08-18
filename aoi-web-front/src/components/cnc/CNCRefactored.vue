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
          :selected-steps="selectedSteps"
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

      <!-- Location Tabs (Shortcuts & Sequence) -->
      <div class="location-tabs-section">
        <div class="tabs-inner-container">
          <LocationTabs
            :axis-uid="axisUid"
            :is-connected="isConnected"
            @shortcut-executed="onShortcutExecuted"
            @shortcut-configured="onShortcutConfigured"
            @sequence-executed="onSequenceExecuted"
            @sequence-paused="onSequencePaused"
            @sequence-stopped="onSequenceStopped"
            @tab-changed="onTabChanged"
          />
        </div>
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
import { logger } from '@/utils/logger';
import { handleApiError, addErrorToStore } from '@/utils/errorHandler';


// Import child components
import PositionDisplay from "./PositionDisplay.vue";
import LocationManagement from "./LocationManagement.vue";
import MovementControls from "./MovementControls.vue";
import GeneralCommands from "./GeneralCommands.vue";
import LocationTabs from "./LocationTabs.vue";
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
    LocationTabs,
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
    const connectionReady = ref(false);  // Track if CNC is ready for commands
    
    // Cross-platform port error dialog state
    const showPortErrorDialog = ref(false);
    const portErrorData = ref({});
    
    // Tab state tracking
    const isSequenceTabActive = ref(false);

    // WebSocket connection
    let socketInstance = null;

    // Computed properties from CNC store
    const { pos, mPos, wPos, cncState, feedrate } = cncStore;
    
    // Computed property for connection state
    const isConnected = computed(() => webSocketState.value === "Connected");
    const isReadyForCommands = computed(() => isConnected.value && connectionReady.value);

    // Lifecycle hooks
    onMounted(() => {
      initializeComponent();
    });

    onUnmounted(() => {
      try {
        cleanup();
      } catch (error) {
        logger.warn('Error during CNCRefactored component unmounting:', error);
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
        logger.error("Failed to initialize CNC component:", error);
        handleApiError(error, 'Failed to initialize CNC component');
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
        logger.error("Failed to connect to WebSocket:", error);
        handleApiError(error, 'Failed to connect to WebSocket');
        webSocketState.value = "Error";
      }
    }

    async function reconnectToWs() {
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
        logger.error("Error during WebSocket cleanup:", error);
      }
    }

    // WebSocket Event Handlers
    function onCncSocketOpen() {
      // WebSocket is connected, but hardware might not be
      // Don't set state to "Connected" here - wait for hardware confirmation
      logger.info("WebSocket connection opened for CNC:", props.axisUid);
      if (socketInstance) {
        socketInstance.send("eses");
      }
    }

    function onCncSocketClose() {
      webSocketState.value = "Disconnected";
      connectionReady.value = false;  // Reset ready state on disconnect
    }

    function onCncSocketError() {
      webSocketState.value = "Error";
      connectionReady.value = false;  // Reset ready state on error
    }

    function onCncSocketMsgRecv(event) {
      try {
        const msg = JSON.parse(event.data);
        handleSingleMessage(msg);
      } catch (error) {
        logger.error("Failed to parse WebSocket message:", error);
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
          // Handle batched messages atomically
          if (msg.messages && Array.isArray(msg.messages)) {
            handleBatchedMessages(msg.messages);
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

        case "on_job_completed":
          addToConsole("Job completed");
          break;

        case "on_feed_change":
          if (msg.feed_rate) {
            addToConsole(`Feed rate changed: ${msg.feed_rate}`);
          }
          break;

        case "on_boot":
          addToConsole("CNC controller booted");
          break;

        case "on_connection_ready":
          addToConsole("CNC initialization completed - ready for commands");
          connectionReady.value = true;
          break;

        case "on_movement":
          // Movement in progress - no console spam, just debug log
          logger.debug("CNC movement in progress", { uid: props.axisUid });
          break;

        case "on_standstill":
          // Movement stopped - no console spam, just debug log
          logger.debug("CNC movement stopped", { uid: props.axisUid });
          break;

        default:
          logger.debug("Unhandled WebSocket message:", msg);
      }
    }


    function handleStateUpdate(msg) {
      cncStore.updateCncData(props.axisUid, {
        mPos: msg.mPos,
        wPos: msg.wPos,
        state: msg.state
      });
    }

    function handleBatchedMessages(messages) {
      // Process batched messages atomically with error recovery
      const stateUpdates = [];
      const consoleMessages = [];
      let hasError = false;
      
      try {
        // First pass: collect all updates without applying them
        for (const batchedMsg of messages) {
          switch (batchedMsg.event) {
            case "on_stateupdate":
              stateUpdates.push(batchedMsg);
              break;
            case "on_read":
              consoleMessages.push(batchedMsg.message);
              break;
            case "on_idle":
              stateUpdates.push({ event: "set_state", state: batchedMsg.message });
              break;
            case "on_error":
              consoleMessages.push(`Error: ${batchedMsg.message}`);
              break;
            case "on_job_completed":
              consoleMessages.push("Job completed");
              break;
            case "on_feed_change":
              if (batchedMsg.feed_rate) {
                consoleMessages.push(`Feed rate changed: ${batchedMsg.feed_rate}`);
              }
              break;
            case "on_boot":
              consoleMessages.push("CNC controller booted");
              break;
            case "on_connection_ready":
              consoleMessages.push("CNC initialization completed - ready for commands");
              connectionReady.value = true;
              break;
            case "on_movement":
            case "on_standstill":
              // Skip movement events in batches to reduce noise
              break;
            default:
              // Handle other messages individually
              handleSingleMessage(batchedMsg);
              break;
          }
        }
        
        // Second pass: apply all updates atomically
        if (stateUpdates.length > 0) {
          // Apply the most recent state update only
          const latestUpdate = stateUpdates[stateUpdates.length - 1];
          if (latestUpdate.event === "on_stateupdate") {
            handleStateUpdate(latestUpdate);
          } else if (latestUpdate.event === "set_state") {
            cncStore.setCncState(props.axisUid, latestUpdate.state);
          }
        }
        
        // Add console messages in order
        consoleMessages.forEach(message => addToConsole(message));
        
      } catch (error) {
        logger.error("Failed to process batched messages atomically:", error);
        // Fallback to individual processing on error
        messages.forEach(msg => {
          try {
            handleSingleMessage(msg);
          } catch (msgError) {
            logger.error("Failed to process individual message in batch:", msgError);
          }
        });
      }
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
      connectionReady.value = false;  // Reset ready state
      
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
      logger.debug(`Axis ${data.axis} moved ${data.direction} by ${data.step}`);
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
      logger.debug("Shortcut configured:", data);
    }

    function onSequenceExecuted(data) {
      if (data.completed) {
        addToConsole(`Sequence completed: ${data.steps} positions executed`);
      } else {
        addToConsole(`Sequence execution started`);
      }
    }

    function onSequencePaused(data) {
      addToConsole(`Sequence paused at step ${data.currentStep + 1}`);
    }

    function onSequenceStopped() {
      addToConsole(`Sequence stopped`);
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
    
    function onTabChanged(tabIndex) {
      isSequenceTabActive.value = tabIndex === 1; // 1 is the sequence tab
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
        logger.error("Failed to initialize CNC:", error);
        handleApiError(error, 'Failed to initialize CNC');
        addToConsole(`Connection failed: ${error.message}`);
        // Set state to disconnected on error
        webSocketState.value = "Disconnected";
        connectionReady.value = false;  // Reset ready state
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
        logger.error("Failed to disconnect and deinitialize CNC:", error);
        handleApiError(error, 'Failed to disconnect and deinitialize CNC');
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
      isSequenceTabActive,
      
      // Computed from CNC store
      pos,
      mPos,
      wPos,
      cncState,
      feedrate,
      
      // Connection state
      isConnected,
      isReadyForCommands,
      connectionReady,
      
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
      onSequenceExecuted,
      onSequencePaused,
      onSequenceStopped,
      onLocationSaved,
      onLocationDeleted,
      onTerminalCommand,
      onTerminalCleared,
      onTabChanged,
    };
  }
};
</script>

<style scoped>
.cnc-container {
  margin: 1rem 0.5rem; /* Balanced margins to prevent border cutoff */
  width: 100%; /* Full container width without overflow */
  max-width: 100%;
  border-radius: 6px; /* Reduced from 12px to 6px - less rounded corners */
  box-shadow: 0 2px 8px black;
  padding: 0.7rem; /* Increased padding for more internal space */
  text-align: center;
  background-color: #515151;
  font-family: "Droid Serif";
  font-size: 1rem;
  font-weight: 700;
  display: flex;
  box-sizing: border-box;
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
  grid-column: 1/3; /* Made wider by spanning 2 columns instead of 1 */
  grid-row: 5/8;
  color: white;
  background-color: #161616;
  border-radius: 8px;
  overflow: hidden;
  padding: 0.5rem;
}

.movement-section {
  grid-column: 3/5; /* Adjusted to start from column 3 to make room for wider save-section */
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

.location-tabs-section {
  grid-column: 10/15;
  grid-row: 4/8;  /* Changed from 5/8 to 4/8 - takes more vertical space */
  color: white;
  background-color: #161616;
  border-radius: 8px;
  overflow: hidden;
  padding: 0.5rem;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tabs-inner-container {
  width: 100%;
  height: 100%;
  max-width: 320px;  /* Align with LocationTabs container width */
  max-height: 360px;  /* Increased from 280px to accommodate taller section */
  display: flex;
  align-items: center;
  justify-content: center;
}



.feedrate-section {
  grid-column: 10/15;
  grid-row: 2/4;  /* Changed from 2/5 to 2/4 - takes less vertical space */
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
  grid-column: 15/19; /* Extended from 15/18 to 15/19 for more width */
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

