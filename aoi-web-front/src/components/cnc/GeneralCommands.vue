<template>
  <div class="commands-grid">
    <div class="title">
      General Commands
    </div>
    <div class="actions-container">
      <div class="flex-row">
        <button
          class="button-wide command-button"
          @click="executeCommand('home')"
          :disabled="isExecuting || !isConnected"
        >
          <div class="button-container">
            <div class="button-icon">
              <font-awesome-icon icon="home" />
            </div>
            <div class="button-text">
              HOME
            </div>
          </div>
        </button>

        <button
          class="button-wide command-button"
          @click="executeCommand('soft_reset')"
          :disabled="isExecuting || !isConnected"
        >
          <div class="button-container">
            <div class="button-icon">
              <font-awesome-icon icon="arrow-rotate-right" />
            </div>
            <div class="button-text">
              SOFT RESET
            </div>
          </div>
        </button>

        <button
          class="button-wide command-button"
          @click="executeCommand('unlock')"
          :disabled="isExecuting || !isConnected"
        >
          <div class="button-container">
            <div class="button-icon">
              <font-awesome-icon icon="lock-open" />
            </div>
            <div class="button-text">
              UNLOCK
            </div>
          </div>
        </button>
      </div>
      
      <div class="flex-row">
        <button
          class="button-wide command-button"
          @click="executeCommand('abort')"
          :disabled="isExecuting || !isConnected"
        >
          <div class="button-container">
            <div class="button-icon">
              <font-awesome-icon icon="stop" />
            </div>
            <div class="button-text">
              ABORT
            </div>
          </div>
        </button>

        <button
          class="button-wide command-button"
          @click="executeCommand('zero_reset')"
          :disabled="isExecuting || !isConnected"
        >
          <div class="button-container">
            <div class="button-icon">
              <font-awesome-icon icon="arrows-rotate" />
            </div>
            <div class="button-text">
              RESET ZERO
            </div>
          </div>
        </button>

        <button
          class="button-wide command-button"
          @click="executeCommand('return_to_zero')"
          :disabled="isExecuting || !isConnected"
        >
          <div class="button-container">
            <div class="button-icon">
              <font-awesome-icon icon="arrow-rotate-left" />
            </div>
            <div class="button-text">
              RETURN ZERO
            </div>
          </div>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from "vue";
import { useCncStore } from '@/composables/useStore';

export default {
  name: "GeneralCommands",
  props: {
    axisUid: {
      type: String,
      required: true
    },
    isConnected: {
      type: Boolean,
      default: false
    }
  },
  emits: ['command-executed'],
  setup(props, { emit }) {
    const cncStore = useCncStore();
    const isExecuting = ref(false);

    async function executeCommand(command) {
      if (isExecuting.value) return;
      
      try {
        isExecuting.value = true;
        
        await cncStore.apiCommand({
          cncUid: props.axisUid,
          command: command,
        });
        
        emit('command-executed', { command, success: true });
        
      } catch (error) {
        console.error(`Failed to execute command ${command}:`, error);
        emit('command-executed', { command, success: false, error });
        
      } finally {
        // Add a small delay to prevent rapid clicking
        setTimeout(() => {
          isExecuting.value = false;
        }, 500);
      }
    }

    return {
      executeCommand,
      isExecuting
    };
  }
};
</script>

<style scoped>
.commands-grid {
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  align-content: center;
  width: 100%;
  height: 100%;
  margin: auto;
  border-radius: 8px;
  padding: 0.5rem;
}

.title {
  background-color: rgb(41, 41, 41);
  border-radius: 20px;
  font-size: 1.5rem;
  width: 100%;
  padding: 0.5rem;
  text-align: center;
  margin-bottom: 1rem;
}

.actions-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  gap: 0.5rem;
}

.flex-row {
  display: flex;
  gap: 0.3rem;
  justify-content: space-between;
}

.button-wide {
  background: rgb(41, 41, 41);
  color: #ffffff;
  border-radius: 20px;
  box-shadow: rgb(41, 41, 41) 0 3px 5px -3px;
  box-sizing: border-box;
  cursor: pointer;
  border: 0;
  font-size: 0.8rem;
  height: 100%;
  margin: 3px;
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

.command-button {
  width: 33%;
  height: 5vh;
  min-height: 60px;
  overflow: hidden;
}

.button-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.15rem;
  height: 100%;
  padding: 0.3rem;
}

.button-icon {
  font-size: 1.2rem;
  flex-shrink: 0;
}

.button-text {
  font-size: 0.7rem;
  font-weight: bold;
  text-align: center;
  line-height: 1.1;
  display: block;
  width: 100%;
}
</style>

