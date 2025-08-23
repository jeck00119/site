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
      
      
      <!-- Keyboard Control Row -->
      <div class="keyboard-control-row">
        <div class="keyboard-control">
          <div class="checkbox-container">
            <input 
              type="checkbox" 
              id="keyboard-control"
              v-model="keyboardControlEnabled"
              @change="toggleKeyboardControl"
            />
            <label for="keyboard-control">
              <font-awesome-icon icon="keyboard" /> Keyboard Control
            </label>
          </div>
          <button 
            class="gear-button"
            :class="{ 'hidden-button': !keyboardControlEnabled }"
            @click="showKeyboardSettings = true"
            title="Keyboard Settings"
            :disabled="!keyboardControlEnabled"
          >
            <font-awesome-icon icon="gear" />
          </button>
        </div>
      </div>
    </div>
    
    <!-- Keyboard Settings Modal -->
    <div v-if="showKeyboardSettings" class="modal-overlay" @click="closeSettingsModal">
      <div class="settings-modal" @click.stop>
        <div class="modal-header">
          <h3>Keyboard Control Settings</h3>
          <button class="close-button" @click="closeSettingsModal">×</button>
        </div>
        <div class="modal-body">
          <div class="setting-group">
            <label>Movement Keys:</label>
            <div class="key-mappings">
              <div class="key-mapping">
                <span>X+ (Right):</span>
                <input type="text" v-model="keyboardSettings.xPlus" @keydown="captureKey($event, 'xPlus')" readonly />
              </div>
              <div class="key-mapping">
                <span>X- (Left):</span>
                <input type="text" v-model="keyboardSettings.xMinus" @keydown="captureKey($event, 'xMinus')" readonly />
              </div>
              <div class="key-mapping">
                <span>Y+ (Up):</span>
                <input type="text" v-model="keyboardSettings.yPlus" @keydown="captureKey($event, 'yPlus')" readonly />
              </div>
              <div class="key-mapping">
                <span>Y- (Down):</span>
                <input type="text" v-model="keyboardSettings.yMinus" @keydown="captureKey($event, 'yMinus')" readonly />
              </div>
              <div class="key-mapping">
                <span>Z+ (Up):</span>
                <input type="text" v-model="keyboardSettings.zPlus" @keydown="captureKey($event, 'zPlus')" readonly />
              </div>
              <div class="key-mapping">
                <span>Z- (Down):</span>
                <input type="text" v-model="keyboardSettings.zMinus" @keydown="captureKey($event, 'zMinus')" readonly />
              </div>
            </div>
          </div>
          <div class="setting-group">
            <label for="movement-step">Movement Step Size:</label>
            <input 
              type="number" 
              id="movement-step"
              v-model="keyboardSettings.stepSize"
              min="1"
              step="1"
            />
          </div>
          <div class="setting-group">
            <label for="movement-feedrate">Movement Feedrate:</label>
            <input 
              type="number" 
              id="movement-feedrate"
              v-model="keyboardSettings.feedrate"
              min="1"
              step="1"
            />
          </div>
        </div>
        <div class="modal-footer">
          <button class="reset-button" @click="resetToDefaults">Reset to Defaults</button>
          <button class="save-button" @click="saveSettings">Save Settings</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from "vue";
import { useCncStore } from '@/composables/useStore';
import { logger } from '@/utils/logger';
import { handleApiError } from '@/utils/errorHandler';
import { library } from '@fortawesome/fontawesome-svg-core';
import { faKeyboard, faGear } from '@fortawesome/free-solid-svg-icons';

library.add(faKeyboard, faGear);

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
    
    // Keyboard control state
    const keyboardControlEnabled = ref(false);
    const showKeyboardSettings = ref(false);
    
    // Default keyboard settings
    const defaultKeyboardSettings = {
      xPlus: 'ArrowRight',
      xMinus: 'ArrowLeft', 
      yPlus: 'ArrowUp',
      yMinus: 'ArrowDown',
      zPlus: 'PageUp',
      zMinus: 'PageDown',
      stepSize: 1,
      feedrate: 1500
    };
    
    const keyboardSettings = ref({ ...defaultKeyboardSettings });
    
    // Load settings from localStorage for this specific CNC
    const settingsKey = `cnc-keyboard-${props.axisUid}`;
    const loadSettings = () => {
      const saved = localStorage.getItem(settingsKey);
      if (saved) {
        try {
          const parsed = JSON.parse(saved);
          keyboardSettings.value = { ...defaultKeyboardSettings, ...parsed };
          keyboardControlEnabled.value = parsed.enabled || false;
        } catch (e) {
          logger.warn('Failed to load keyboard settings:', e);
        }
      }
    };
    
    const saveSettingsToStorage = () => {
      localStorage.setItem(settingsKey, JSON.stringify({
        ...keyboardSettings.value,
        enabled: keyboardControlEnabled.value
      }));
    };

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
        logger.error(`Failed to execute command ${command}:`, error);
        handleApiError(error, `Failed to execute command ${command}`);
        emit('command-executed', { command, success: false, error });
        
      } finally {
        // Reduced delay for faster user interaction
        setTimeout(() => {
          isExecuting.value = false;
        }, 100);
      }
    }

    // Keyboard control functions
    const handleKeydown = (event) => {
      if (!keyboardControlEnabled.value || !props.isConnected) return;
      
      // Prevent default behavior for our mapped keys
      const keyMappings = {
        [keyboardSettings.value.xPlus]: { axis: 'x', direction: 'plus' },
        [keyboardSettings.value.xMinus]: { axis: 'x', direction: 'minus' },
        [keyboardSettings.value.yPlus]: { axis: 'y', direction: 'plus' },
        [keyboardSettings.value.yMinus]: { axis: 'y', direction: 'minus' },
        [keyboardSettings.value.zPlus]: { axis: 'z', direction: 'plus' },
        [keyboardSettings.value.zMinus]: { axis: 'z', direction: 'minus' }
      };
      
      const mapping = keyMappings[event.code];
      if (mapping) {
        event.preventDefault();
        event.stopPropagation();
        
        // Use CNC store actions for movement
        if (mapping.direction === 'plus') {
          cncStore.increaseAxis({
            cncUid: props.axisUid,
            axis: mapping.axis,
            step: keyboardSettings.value.stepSize,
            feedrate: keyboardSettings.value.feedrate
          });
        } else {
          cncStore.decreaseAxis({
            cncUid: props.axisUid,
            axis: mapping.axis,
            step: keyboardSettings.value.stepSize,
            feedrate: keyboardSettings.value.feedrate
          });
        }
        
        emit('command-executed', { 
          command: `keyboard_${mapping.axis}_${mapping.direction}`, 
          success: true 
        });
      }
    };
    
    const toggleKeyboardControl = () => {
      if (keyboardControlEnabled.value) {
        document.addEventListener('keydown', handleKeydown);
      } else {
        document.removeEventListener('keydown', handleKeydown);
      }
      saveSettingsToStorage();
    };
    
    // Settings modal functions
    const closeSettingsModal = () => {
      showKeyboardSettings.value = false;
    };
    
    const captureKey = (event, action) => {
      event.preventDefault();
      keyboardSettings.value[action] = event.code;
    };
    
    const resetToDefaults = () => {
      keyboardSettings.value = { ...defaultKeyboardSettings };
    };
    
    const saveSettings = () => {
      saveSettingsToStorage();
      showKeyboardSettings.value = false;
    };
    
    // Lifecycle hooks
    onMounted(() => {
      loadSettings();
      if (keyboardControlEnabled.value) {
        document.addEventListener('keydown', handleKeydown);
      }
    });
    
    onUnmounted(() => {
      document.removeEventListener('keydown', handleKeydown);
    });

    return {
      executeCommand,
      isExecuting,
      // Keyboard control
      keyboardControlEnabled,
      showKeyboardSettings,
      keyboardSettings,
      toggleKeyboardControl,
      closeSettingsModal,
      captureKey,
      resetToDefaults,
      saveSettings
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
  padding: 0.1rem 0.5rem 0.5rem 0.5rem;
}

.title {
  background-color: rgb(41, 41, 41);
  border-radius: 20px;
  font-size: 1.5rem;
  width: 100%;
  padding: 0.5rem;
  text-align: center;
  margin-bottom: 1rem;
  margin-top: -1rem;
}

.actions-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  gap: 0.5rem;
  margin-top: -2rem;
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

/* Keyboard Control Styles */
.keyboard-control-row {
  margin-top: 1.25rem;
  padding-top: 0.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.keyboard-control {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 90%;
  margin: auto;
}

.checkbox-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.checkbox-container input[type="checkbox"] {
  accent-color: rgb(204, 161, 82);
  transform: scale(1.2);
}

.checkbox-container label {
  color: white;
  font-weight: bold;
  cursor: pointer;
  font-size: 1.1rem;
}

.gear-button {
  background: rgb(41, 41, 41);
  border: 1px solid rgb(204, 161, 82);
  color: rgb(204, 161, 82);
  border-radius: 4px;
  padding: 0.25rem 0.5rem;
  cursor: pointer;
  font-size: 1.2rem;
  transition: all 0.2s ease;
}

.gear-button:hover {
  background: rgb(204, 161, 82);
  color: rgb(41, 41, 41);
}

.hidden-button {
  visibility: hidden;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%; /* Use container width instead of viewport */
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.settings-modal {
  background-color: rgb(41, 41, 41);
  border-radius: 12px;
  width: 500px;
  max-width: 90%; /* Use container width instead of viewport */
  max-height: 80vh;
  overflow-y: auto;
  color: white;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header h3 {
  margin: 0;
  color: rgb(204, 161, 82);
  font-size: 1.3rem;
}

.close-button {
  background: none;
  border: none;
  color: white;
  font-size: 2rem;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-button:hover {
  color: rgb(204, 161, 82);
}

.modal-body {
  padding: 1rem;
}

.setting-group {
  margin-bottom: 1.5rem;
}

.setting-group label {
  display: block;
  font-weight: bold;
  margin-bottom: 0.5rem;
  color: rgb(204, 161, 82);
}

.key-mappings {
  display: grid;
  gap: 0.5rem;
}

.key-mapping {
  display: grid;
  grid-template-columns: 120px 1fr;
  align-items: center;
  gap: 1rem;
}

.key-mapping span {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
}

.key-mapping input {
  background-color: rgb(51, 51, 51);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 0.5rem;
  border-radius: 4px;
  text-align: center;
  cursor: pointer;
}

.key-mapping input:focus {
  outline: 2px solid rgb(204, 161, 82);
  border-color: rgb(204, 161, 82);
}

.setting-group input[type="number"] {
  background-color: rgb(51, 51, 51);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 0.5rem;
  border-radius: 4px;
  width: 100px;
}

.setting-group input[type="number"]:focus {
  outline: 2px solid rgb(204, 161, 82);
  border-color: rgb(204, 161, 82);
}

.modal-footer {
  padding: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.reset-button, .save-button {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.2s ease;
}

.reset-button {
  background-color: rgba(255, 107, 107, 0.8);
  color: white;
}

.reset-button:hover {
  background-color: rgb(255, 107, 107);
}

.save-button {
  background-color: rgb(204, 161, 82);
  color: rgb(41, 41, 41);
}

.save-button:hover {
  background-color: rgb(224, 181, 102);
}
</style>

