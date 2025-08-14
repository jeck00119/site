<template>
  <div class="movement-controls">
    <div class="move-x-grid">
      <div class="axis-control">
        <div>
          <button
            class="button-up"
            @click="increaseAxis('x')"
            :disabled="!isConnected"
          >
            <font-awesome-icon icon="plus" />
          </button>
        </div>
        <label>X</label>
        <div>
          <button
            class="button-down"
            @click="decreaseAxis('x')"
            :disabled="!isConnected"
          >
            <font-awesome-icon icon="minus" />
          </button>
        </div>
      </div>
    </div>

    <div class="move-y-grid">
      <div class="axis-control">
        <div>
          <button
            class="button-up"
            @click="increaseAxis('y')"
            :disabled="!isConnected"
          >
            <font-awesome-icon icon="plus" />
          </button>
        </div>
        <label>Y</label>
        <div>
          <button
            class="button-down"
            @click="decreaseAxis('y')"
            :disabled="!isConnected"
          >
            <font-awesome-icon icon="minus" />
          </button>
        </div>
      </div>
    </div>

    <div class="move-z-grid">
      <div class="axis-control">
        <div>
          <button
            class="button-up"
            @click="increaseAxis('z')"
            :disabled="!isConnected"
          >
            <font-awesome-icon icon="plus" />
          </button>
        </div>
        <label>Z</label>
        <div>
          <button
            class="button-down"
            @click="decreaseAxis('z')"
            :disabled="!isConnected"
          >
            <font-awesome-icon icon="minus" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useCncStore } from '@/composables/useStore';

export default {
  name: "MovementControls",
  props: {
    axisUid: {
      type: String,
      required: true
    },
    selectedSteps: {
      type: [String, Number],
      required: true
    },
    selectedFeedrate: {
      type: [String, Number],
      required: true
    },
    isConnected: {
      type: Boolean,
      default: false
    }
  },
  emits: ['axis-moved'],
  setup(props, { emit }) {
    const cncStore = useCncStore();

    function increaseAxis(axis) {
      cncStore.increaseAxis({
        cncUid: props.axisUid,
        axis: axis,
        step: props.selectedSteps,
        feedrate: props.selectedFeedrate,
      });
      
      emit('axis-moved', { axis, direction: 'increase', step: props.selectedSteps });
    }

    function decreaseAxis(axis) {
      cncStore.decreaseAxis({
        cncUid: props.axisUid,
        axis: axis,
        step: props.selectedSteps,
        feedrate: props.selectedFeedrate,
      });
      
      emit('axis-moved', { axis, direction: 'decrease', step: props.selectedSteps });
    }

    return {
      increaseAxis,
      decreaseAxis
    };
  }
};
</script>

<style scoped>
.movement-controls {
  display: flex;
  gap: 5px;
  width: 100%;
}

.move-x-grid,
.move-y-grid,
.move-z-grid {
  color: white;
  background-color: #161616;
  justify-content: center;
  align-items: center;
  display: grid;
  flex: 1;
  border-radius: 8px;
  padding: 0.7rem;
}

.axis-control {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.axis-control label {
  font-size: 1rem;
  font-weight: bold;
  color: white;
}

.button-down,
.button-up {
  background: rgb(41, 41, 41);
  color: #ffffff;
  width: 50px;
  height: 50px;
  border-radius: 8px;
  box-shadow: rgb(41, 41, 41) 0 3px 5px -3px;
  box-sizing: border-box;
  cursor: pointer;
  border: 0;
  font-size: 1.1rem;
  margin: 1%;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.button-down:hover:not(:disabled),
.button-up:hover:not(:disabled) {
  box-shadow: rgba(255, 255, 255, 0.2) 0 3px 15px inset,
    rgba(0, 0, 0, 0.1) 0 3px 5px, rgba(0, 0, 0, 0.1) 0 10px 13px;
  transform: scale(1.05);
  border: 1px solid rgb(61, 59, 59);
}

.button-down:disabled,
.button-up:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.button-up {
  border-bottom-right-radius: 0;
  border-bottom-left-radius: 0;
}

.button-down {
  border-top-left-radius: 0;
  border-top-right-radius: 0;
}
</style>

