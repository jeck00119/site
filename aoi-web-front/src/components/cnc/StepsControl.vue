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
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from "vue";

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
    }
  },
  emits: ['steps-changed', 'feedrate-changed'],
  setup(props, { emit }) {
    const predefinedSteps = [1, 5, 10, 20, 30, 50, 100, 200];
    const customStep = ref("");

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

    return {
      predefinedSteps,
      customStep,
      isPredefinedStep,
      isCustomActive,
      updateSteps,
      updateCustomStep,
      validateCustomStep,
      updateFeedrate,
      validateFeedrate
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
</style>

