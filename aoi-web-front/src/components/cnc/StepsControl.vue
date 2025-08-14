<template>
  <div class="steps-grid">
    <div class="title">
      Movement Settings
    </div>
    <div class="actions-container">
      <div class="flex-row">
        <div 
          v-for="step in predefinedSteps.slice(0, 4)" 
          :key="step"
          class="form-control"
        >
          <input 
            type="radio" 
            :value="step" 
            :id="`step-${step}`" 
            :checked="selectedSteps == step && !isCustomActive"
            @change="updateSteps"
          />
          <label :for="`step-${step}`">{{ step }}</label>
        </div>
      </div>
      
      <div class="flex-row">
        <div 
          v-for="step in predefinedSteps.slice(4, 8)" 
          :key="step"
          class="form-control"
        >
          <input 
            type="radio" 
            :value="step" 
            :id="`step-${step}`" 
            :checked="selectedSteps == step && !isCustomActive"
            @change="updateSteps"
          />
          <label :for="`step-${step}`">{{ step }}</label>
        </div>
      </div>
      
      <div class="flex-row">
        <div class="form-control spaced">
          <label for="custom-step">Steps:</label>
          <input 
            type="number" 
            id="custom-step" 
            :value="customStep"
            :class="{ 'custom-active': isCustomActive }"
            @input="updateCustomStep"
            @blur="validateCustomStep"
            min="0.001"
            step="0.001"
            placeholder="Custom"
          />
        </div>
      </div>
      
      <!-- Feedrate Control -->
      <div class="flex-row feedrate-row">
        <div class="form-control spaced">
          <label for="feedrate-input">Feedrate:</label>
          <input 
            type="number" 
            id="feedrate-input" 
            :value="feedrate"
            @input="updateFeedrate"
            @blur="validateFeedrate"
            min="1"
            step="1"
            placeholder="1500"
          />
        </div>
      </div>
      
      <!-- Keyboard Control -->
      <div class="flex-row keyboard-row">
        <div class="keyboard-control">
          <div class="checkbox-container">
            <input 
              type="checkbox" 
              id="keyboard-control"
              v-model="keyboardControlEnabled"
              @change="toggleKeyboardControl"
            />
            <label for="keyboard-control">Keyboard Control</label>
          </div>
          <button 
            v-if="keyboardControlEnabled"
            class="gear-button"
            @click="showKeyboardSettings = true"
            title="Keyboard Settings"
          >
            ⚙️
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
              min="0.001"
              step="0.001"
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
import { ref, computed, watch, onMounted, onUnmounted } from "vue";

export default {
  name: "StepsControl",
  props: {
    selectedSteps: {
      type: [String, Number],
      required: true
    },
    feedrate: {
      type: [String, Number],
      required: true
    },
    axisUid: {
      type: String,
      required: true
    },
    isConnected: {
      type: Boolean,
      default: false
    }
  },
  emits: ['steps-changed', 'feedrate-changed', 'keyboard-move'],
  setup(props, { emit }) {
    const predefinedSteps = [1, 5, 10, 20, 30, 50, 100, 200];
    const customStep = ref("");
    
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
          console.warn('Failed to load keyboard settings:', e);
        }
      }
    };
    
    const saveSettingsToStorage = () => {
      localStorage.setItem(settingsKey, JSON.stringify({
        ...keyboardSettings.value,
        enabled: keyboardControlEnabled.value
      }));
    };

    // Check if current step is a predefined value
    const isPredefinedStep = computed(() => {
      return predefinedSteps.includes(Number(props.selectedSteps));
    });

    // Check if custom field is active (has a value)
    const isCustomActive = computed(() => {
      return customStep.value !== "" && customStep.value !== null;
    });

    // Update custom step field when selectedSteps changes from parent
    watch(() => props.selectedSteps, (newValue) => {
      // Only update custom field if it's not a predefined step and custom field is empty
      if (!isPredefinedStep.value && !isCustomActive.value) {
        customStep.value = newValue;
      }
    }, { immediate: true });

    function updateSteps(event) {
      const value = Number(event.target.value);
      // Clear custom field when selecting a predefined step
      customStep.value = "";
      emit('steps-changed', value);
    }

    function updateCustomStep(event) {
      const value = event.target.value;
      customStep.value = value;
      
      // Update steps if it's a valid number
      const numValue = parseFloat(value);
      if (!isNaN(numValue) && numValue > 0) {
        emit('steps-changed', numValue);
      }
    }

    function validateCustomStep(event) {
      const value = parseFloat(event.target.value);
      
      if (isNaN(value) || value <= 0) {
        // Reset to previous valid value or default
        if (isPredefinedStep.value) {
          customStep.value = "";
        } else {
          customStep.value = props.selectedSteps;
          event.target.value = props.selectedSteps;
        }
      } else {
        // Ensure reasonable bounds
        const clampedValue = Math.max(0.001, Math.min(10000, value));
        if (clampedValue !== value) {
          customStep.value = clampedValue;
          event.target.value = clampedValue;
          emit('steps-changed', clampedValue);
        }
      }
    }

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
        
        // Emit keyboard move event to parent
        emit('keyboard-move', {
          cncUid: props.axisUid,
          axis: mapping.axis,
          direction: mapping.direction,
          step: keyboardSettings.value.stepSize,
          feedrate: keyboardSettings.value.feedrate
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
      predefinedSteps,
      customStep,
      isPredefinedStep,
      isCustomActive,
      updateSteps,
      updateCustomStep,
      validateCustomStep,
      updateFeedrate,
      validateFeedrate,
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
.steps-grid {
  color: white;
  justify-content: space-around;
  align-items: center;
  display: flex;
  flex-direction: column;
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
  margin-bottom: 0.75rem;
}

.actions-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  gap: 0.3rem;
}

.flex-row {
  display: flex;
  gap: 0.5rem;
  justify-content: space-around;
}

.form-control {
  display: flex;
  flex-direction: row;
  background-color: inherit;
  border: none;
  color: white;
  justify-content: center;
  align-items: center;
  gap: 0.25rem;
  flex: 1;
}

.form-control input[type="radio"] {
  margin: 0;
  accent-color: rgb(204, 161, 82);
}

.form-control label {
  cursor: pointer;
  font-size: 0.9rem;
  user-select: none;
}

.form-control input[type="number"] {
  background-color: rgb(41, 41, 41);
  border: none;
  color: white;
  text-align: center;
  border-radius: 4px;
  padding: 0.25rem;
  width: 80px;
  font-size: 0.9rem;
}

.form-control input[type="number"]:focus {
  outline: 2px solid rgb(204, 161, 82);
  background-color: rgb(51, 51, 51);
}

.form-control input[type="number"].custom-active {
  background-color: rgb(224, 181, 102);
  color: rgb(41, 41, 41);
  font-weight: bold;
}

.form-control input[type="number"].custom-active:focus {
  background-color: rgb(234, 191, 112);
  outline: 2px solid rgb(244, 201, 122);
}

.spaced {
  display: grid;
  grid-template-columns: 80px 1fr;
  width: 90%;
  margin: auto;
  gap: 0.5rem;
  align-items: center;
}

.spaced label {
  white-space: nowrap;
  font-weight: bold;
  text-align: left;
  font-size: 1.1rem;
}

/* Radio button styling */
.form-control input[type="radio"]:checked + label {
  color: rgb(204, 161, 82);
  font-weight: bold;
}

.form-control:hover label {
  color: rgb(220, 220, 220);
}

.form-control input[type="radio"]:checked:hover + label {
  color: rgb(224, 181, 102);
}

/* Feedrate row styling */
.feedrate-row {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

#feedrate-input {
  background-color: rgb(41, 41, 41);
  border: none;
  color: white;
  text-align: center;
  border-radius: 4px;
  padding: 0.25rem;
  width: 80px;
  font-size: 0.9rem;
}

#feedrate-input:focus {
  outline: 2px solid rgb(204, 161, 82);
  background-color: rgb(51, 51, 51);
}

/* Keyboard Control Styles */
.keyboard-row {
  margin-top: 0.5rem;
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

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
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
  max-width: 90vw;
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

