<template>
  <div class="terminal-grid">
    <div class="terminal-output-container">
      <textarea 
        ref="terminalOutput"
        readonly 
        :value="terminalHistory"
        class="terminal-output custom-scrollbar"
        @scroll="handleScroll"
      ></textarea>
      
      <div v-if="!isAtBottom" class="scroll-indicator">
        <button @click="scrollToBottom" class="scroll-button">
          <font-awesome-icon icon="chevron-down" />
          New messages
        </button>
      </div>
    </div>
    
    <div class="terminal-control">
      <input
        ref="commandInput"
        type="text"
        v-model="commandLine"
        @keyup.enter="sendCommand"
        @keyup.up="navigateHistory(-1)"
        @keyup.down="navigateHistory(1)"
        class="terminal-input"
        :placeholder="isConnected ? 'Enter command...' : 'CNC not connected'"
        :disabled="isSending || !isConnected"
      />
      
      <button
        @click="sendCommand"
        class="button-wide small-button"
        :disabled="isSending || !commandLine.trim() || !isConnected"
      >
        <v-icon 
          :name="isSending ? 'fa-spinner' : 'io-send-sharp'" 
          scale="0.7"
          :spin="isSending"
        />
      </button>
      
      <button
        @click="clearTerminal"
        class="button-wide small-button clear-button"
        title="Clear terminal"
      >
        <font-awesome-icon icon="trash" scale="0.7" />
      </button>
    </div>
  </div>
</template>

<script>
import { ref, nextTick, watch, onMounted, onUnmounted } from "vue";
import { useCncStore } from '@/composables/useStore';
import { logger } from '@/utils/logger';
import { handleApiError } from '@/utils/errorHandler';

export default {
  name: "TerminalConsole",
  props: {
    axisUid: {
      type: String,
      required: true
    },
    terminalHistory: {
      type: String,
      default: ""
    },
    isConnected: {
      type: Boolean,
      default: false
    }
  },
  emits: ['command-sent', 'terminal-cleared'],
  setup(props, { emit }) {
    const cncStore = useCncStore();
    
    const commandLine = ref("");
    const commandHistory = ref([]);
    const historyIndex = ref(-1);
    const isSending = ref(false);
    const isAtBottom = ref(true);
    
    const terminalOutput = ref(null);
    const commandInput = ref(null);

    // Auto-scroll to bottom when new content is added
    watch(() => props.terminalHistory, async () => {
      if (isAtBottom.value) {
        await nextTick();
        scrollToBottom();
      }
    });

    onMounted(() => {
      loadCommandHistory();
      focusInput();
    });

    onUnmounted(() => {
      saveCommandHistory();
    });

    function loadCommandHistory() {
      const saved = localStorage.getItem(`cnc-command-history-${props.axisUid}`);
      if (saved) {
        try {
          commandHistory.value = JSON.parse(saved);
        } catch (error) {
          logger.error("Failed to load command history:", error);
          handleApiError(error, 'Failed to load command history');
        }
      }
    }

    function saveCommandHistory() {
      // Keep only last 50 commands
      const historyToSave = commandHistory.value.slice(-50);
      localStorage.setItem(`cnc-command-history-${props.axisUid}`, JSON.stringify(historyToSave));
    }

    function focusInput() {
      if (commandInput.value) {
        commandInput.value.focus({ preventScroll: true });
      }
    }

    async function sendCommand() {
      if (isSending.value || !commandLine.value.trim() || !props.isConnected) return;
      
      const command = commandLine.value.trim();
      
      try {
        isSending.value = true;
        
        // Handle special commands
        if (command.toLowerCase() === "clear") {
          clearTerminal();
          commandLine.value = "";
          return;
        }
        
        // Add to history
        if (command && !commandHistory.value.includes(command)) {
          commandHistory.value.push(command);
          saveCommandHistory();
        }
        
        // Send command to store
        await cncStore.terminalCommand({
          cncUid: props.axisUid,
          command: command,
        });
        
        emit('command-sent', { command, timestamp: new Date() });
        
        // Clear input and reset history navigation
        commandLine.value = "";
        historyIndex.value = -1;
        
      } catch (error) {
        logger.error("Failed to send command:", error);
        handleApiError(error, 'Failed to send command');
        
      } finally {
        isSending.value = false;
        focusInput();
      }
    }

    function clearTerminal() {
      emit('terminal-cleared');
    }

    function navigateHistory(direction) {
      if (commandHistory.value.length === 0) return;
      
      const newIndex = historyIndex.value + direction;
      
      if (newIndex >= 0 && newIndex < commandHistory.value.length) {
        historyIndex.value = newIndex;
        commandLine.value = commandHistory.value[commandHistory.value.length - 1 - newIndex];
      } else if (newIndex < 0) {
        historyIndex.value = -1;
        commandLine.value = "";
      }
    }

    function handleScroll() {
      if (!terminalOutput.value) return;
      
      const element = terminalOutput.value;
      const threshold = 50; // pixels from bottom
      
      isAtBottom.value = (
        element.scrollHeight - element.scrollTop - element.clientHeight < threshold
      );
    }

    function scrollToBottom() {
      if (terminalOutput.value) {
        terminalOutput.value.scrollTop = terminalOutput.value.scrollHeight;
        isAtBottom.value = true;
      }
    }

    return {
      commandLine,
      isSending,
      isAtBottom,
      terminalOutput,
      commandInput,
      sendCommand,
      clearTerminal,
      navigateHistory,
      handleScroll,
      scrollToBottom,
      focusInput
    };
  }
};
</script>

<style scoped>
.terminal-grid {
  color: white;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.terminal-output-container {
  position: relative;
  flex: 1;
  margin-bottom: 0.5rem;
}

.terminal-output {
  background-color: black;
  color: white;
  width: 100%;
  height: 100%;
  border: none;
  border-radius: 4px;
  padding: 0.5rem;
  font-family: 'Courier New', monospace;
  font-size: 0.8rem;
  resize: none;
  overflow-y: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.terminal-output:focus {
  outline: none;
}

.scroll-indicator {
  position: absolute;
  bottom: 10px;
  right: 10px;
  z-index: 10;
}

.scroll-button {
  background-color: rgba(204, 161, 82, 0.9);
  color: black;
  border: none;
  border-radius: 20px;
  padding: 0.5rem 1rem;
  font-size: 0.7rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  transition: all 0.2s ease;
}

.scroll-button:hover {
  background-color: rgb(204, 161, 82);
  transform: scale(1.05);
}

.terminal-control {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.terminal-input {
  flex: 1;
  background-color: rgb(41, 41, 41);
  border: none;
  color: white;
  padding: 0.5rem;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

.terminal-input:focus {
  outline: 2px solid rgb(204, 161, 82);
  background-color: rgb(51, 51, 51);
}

.terminal-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.button-wide {
  background: rgb(41, 41, 41);
  color: #ffffff;
  border-radius: 8px;
  box-shadow: rgb(41, 41, 41) 0 3px 5px -3px;
  box-sizing: border-box;
  cursor: pointer;
  border: 0;
  transition: all 0.2s ease;
}

.button-wide:hover:not(:disabled) {
  box-shadow: rgba(255, 255, 255, 0.2) 0 3px 15px inset,
    rgba(0, 0, 0, 0.1) 0 3px 5px, rgba(0, 0, 0, 0.1) 0 10px 13px;
  transform: scale(1.05);
}

.button-wide:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.small-button {
  width: 32px; /* Reduced from 40px */
  height: 36px; /* Increased height for better proportion */
  display: flex;
  align-items: center;
  justify-content: center;
}

.clear-button {
  background-color: rgb(139, 69, 19);
}

.clear-button:hover:not(:disabled) {
  background-color: rgb(160, 82, 45);
}

</style>

