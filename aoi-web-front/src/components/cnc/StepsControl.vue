<template>
  <div class="steps-grid">
    <div class="title">
      Steps
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
            :checked="selectedSteps == step"
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
            :checked="selectedSteps == step"
            @change="updateSteps"
          />
          <label :for="`step-${step}`">{{ step }}</label>
        </div>
      </div>
      
      <div class="flex-row">
        <div class="form-control spaced">
          <label for="custom-step">Value:</label>
          <input 
            type="number" 
            id="custom-step" 
            :value="customStep"
            @input="updateCustomStep"
            @blur="validateCustomStep"
            min="0.001"
            step="0.001"
            placeholder="Custom"
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
    }
  },
  emits: ['steps-changed'],
  setup(props, { emit }) {
    const predefinedSteps = [1, 5, 10, 20, 30, 50, 100, 200];
    const customStep = ref("");

    // Check if current step is a predefined value
    const isPredefinedStep = computed(() => {
      return predefinedSteps.includes(Number(props.selectedSteps));
    });

    // Update custom step field when selectedSteps changes
    watch(() => props.selectedSteps, (newValue) => {
      if (!isPredefinedStep.value) {
        customStep.value = newValue;
      } else {
        customStep.value = "";
      }
    }, { immediate: true });

    function updateSteps(event) {
      const value = Number(event.target.value);
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

    return {
      predefinedSteps,
      customStep,
      isPredefinedStep,
      updateSteps,
      updateCustomStep,
      validateCustomStep
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

.spaced {
  justify-content: space-between;
  width: 90%;
  margin: auto;
  gap: 1rem;
}

.spaced label {
  white-space: nowrap;
  font-weight: bold;
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
</style>

