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
          @axis-moved="onAxisMoved"
        />
      </div>

      <!-- General Commands -->
      <div class="commands-section">
        <GeneralCommands
          :axis-uid="axisUid"
          @command-executed="onCommandExecuted"
        />
      </div>

      <!-- Location Shortcuts -->
      <div class="shortcuts-section">
        <LocationShortcuts
          :axis-uid="axisUid"
          @shortcut-executed="onShortcutExecuted"
          @shortcut-configured="onShortcutConfigured"
        />
      </div>

      <!-- Feedrate and State -->
      <div class="feedrate-section">
        <FeedrateState
          :axis-uid="axisUid"
          :feedrate="selectedFeedrate"
          :connection-status="webSocketState"
          @feedrate-changed="onFeedrateChanged"
          @reconnect-requested="reconnectToWs"
        />
      </div>

      <!-- Steps Control -->
      <div class="steps-section">
        <StepsControl
          :selected-steps="selectedSteps"
          @steps-changed="onStepsChanged"
        />
      </div>

      <!-- Terminal Console -->
      <div class="terminal-section">
        <TerminalConsole
          :axis-uid="axisUid"
          :terminal-history="ugsTerminalHistory"
          @command-sent="onTerminalCommand"
          @terminal-cleared="onTerminalCleared"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed } from "vue";
import { useStore } from "vuex";
import { ipAddress, port } from "../../url";

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
    const store = useStore();

    // Reactive state
    const selectedFeedrate = ref(100);
    const selectedSteps = ref(1);
    const ugsTerminalHistory = ref("");
    const webSocketState = ref("Disconnected");

    // WebSocket connection
    let socket = null;

    // Computed properties
    const pos = computed(() => store.getters["cnc/pos"](props.axisUid));

    // Lifecycle hooks
    onMounted(() => {
      initializeComponent();
    });

    onUnmounted(() => {
      cleanup();
    });

    // Initialization
    async function initializeComponent() {
      try {
        // Add position data to store
        store.dispatch("cnc/addPositionData", {
          uid: props.axisUid
        });

        // Connect to WebSocket
        connectToWs();

        // Fetch locations
        await store.dispatch("cnc/fetchLocations", props.axisUid);

      } catch (error) {
        console.error("Failed to initialize CNC component:", error);
      }
    }

    // Cleanup
    function cleanup() {
      disconnectFromWs();
    }

    // WebSocket Management
    function connectToWs() {
      try {
        socket = new WebSocket(`ws://${ipAddress}:${port}/cnc/${props.axisUid}/ws`);

        socket.addEventListener("open", onCncSocketOpen);
        socket.addEventListener("close", onCncSocketClose);
        socket.addEventListener("error", onCncSocketError);
        socket.addEventListener("message", onCncSocketMsgRecv);

      } catch (error) {
        console.error("Failed to connect to WebSocket:", error);
        webSocketState.value = "Error";
      }
    }

    function reconnectToWs() {
      disconnectFromWs();
      setTimeout(() => {
        connectToWs();
      }, 1000);
    }

    async function disconnectFromWs() {
      try {
        await store.dispatch("cnc/closeStateSocket", {
          uid: props.axisUid
        });

        if (socket) {
          socket.removeEventListener("open", onCncSocketOpen);
          socket.removeEventListener("close", onCncSocketClose);
          socket.removeEventListener("error", onCncSocketError);
          socket.removeEventListener("message", onCncSocketMsgRecv);

          socket.close();
          socket = null;
        }

      } catch (error) {
        console.error("Error during WebSocket cleanup:", error);
      }
    }

    // WebSocket Event Handlers
    function onCncSocketOpen() {
      webSocketState.value = "Connected";
      if (socket) {
        socket.send("eses");
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
          store.dispatch("cnc/setCNCState", {
            uid: props.axisUid,
            state: msg.message
          });
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

        default:
          console.log("Unhandled WebSocket message:", msg);
      }
    }

    function handleStateUpdate(msg) {
      store.dispatch("cnc/setMPos", {
        uid: props.axisUid,
        x: msg.mPos[0],
        y: msg.mPos[1],
        z: msg.mPos[2]
      });

      store.dispatch("cnc/setWPos", {
        uid: props.axisUid,
        x: msg.wPos[0],
        y: msg.wPos[1],
        z: msg.wPos[2]
      });

      store.dispatch("cnc/setPos", {
        uid: props.axisUid
      });

      store.dispatch("cnc/setCNCState", {
        uid: props.axisUid,
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
      ugsTerminalHistory.value += `[${timestamp}] ${message}\n`;
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
      ugsTerminalHistory.value = "";
    }

    return {
      // State
      selectedFeedrate,
      selectedSteps,
      ugsTerminalHistory,
      webSocketState,
      
      // Computed
      pos,
      
      // Methods
      reconnectToWs,
      
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
      onTerminalCleared
    };
  }
};
</script>

<style scoped>
.cnc-container {
  margin: 1rem;
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
  grid-template-columns: repeat(16, 1fr);
  grid-template-rows: repeat(8, 1fr);
  align-content: normal;
  gap: 5px;
  width: 100%;
  min-height: 600px;
}

/* Grid Layout */
.positions-section {
  grid-column: 1/5;
  grid-row: 2/5;
}

.save-section {
  grid-column: 1;
  grid-row: 5/8;
}

.movement-section {
  grid-column: 2/5;
  grid-row: 5/8;
  display: flex;
}

.commands-section {
  grid-column: 5/9;
  grid-row: 2/5;
}

.shortcuts-section {
  grid-column: 9/14;
  grid-row: 5/8;
}

.feedrate-section {
  grid-column: 9/14;
  grid-row: 2/5;
}

.steps-section {
  grid-column: 5/9;
  grid-row: 5/8;
}

.terminal-section {
  grid-column: 14/17;
  grid-row: 2/8;
}

/* Responsive Design */
@media (max-width: 1200px) {
  .wrapper {
    grid-template-columns: repeat(12, 1fr);
    grid-template-rows: repeat(10, 1fr);
  }
  
  .positions-section {
    grid-column: 1/7;
    grid-row: 1/3;
  }
  
  .save-section {
    grid-column: 7/9;
    grid-row: 1/3;
  }
  
  .movement-section {
    grid-column: 9/13;
    grid-row: 1/3;
  }
  
  .commands-section {
    grid-column: 1/7;
    grid-row: 3/5;
  }
  
  .shortcuts-section {
    grid-column: 7/13;
    grid-row: 3/5;
  }
  
  .feedrate-section {
    grid-column: 1/5;
    grid-row: 5/7;
  }
  
  .steps-section {
    grid-column: 5/9;
    grid-row: 5/7;
  }
  
  .terminal-section {
    grid-column: 9/13;
    grid-row: 5/10;
  }
}

@media (max-width: 768px) {
  .wrapper {
    grid-template-columns: 1fr;
    grid-template-rows: auto;
    gap: 1rem;
  }
  
  .positions-section,
  .save-section,
  .movement-section,
  .commands-section,
  .shortcuts-section,
  .feedrate-section,
  .steps-section,
  .terminal-section {
    grid-column: 1;
    grid-row: auto;
  }
  
  .cnc-container {
    margin: 0.5rem;
  }
}
</style>

