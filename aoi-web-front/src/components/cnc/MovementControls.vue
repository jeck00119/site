<template>
  <div class="movement-controls">
    <div class="move-x-grid">
      <div class="axis-control">
        <div>
          <button
            class="button-up"
            @click="increaseAxis('x')"
          >
            <font-awesome-icon icon="plus" />
          </button>
        </div>
        <label>X</label>
        <div>
          <button
            class="button-down"
            @click="decreaseAxis('x')"
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
          >
            <font-awesome-icon icon="plus" />
          </button>
        </div>
        <label>Y</label>
        <div>
          <button
            class="button-down"
            @click="decreaseAxis('y')"
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
          >
            <font-awesome-icon icon="plus" />
          </button>
        </div>
        <label>Z</label>
        <div>
          <button
            class="button-down"
            @click="decreaseAxis('z')"
          >
            <font-awesome-icon icon="minus" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useStore } from "vuex";

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
    }
  },
  emits: ['axis-moved'],
  setup(props, { emit }) {
    const store = useStore();

    function increaseAxis(axis) {
      store.dispatch("cnc/api_increaseAxis", {
        cncUid: props.axisUid,
        axis: axis,
        step: props.selectedSteps,
        feedrate: props.selectedFeedrate,
      });
      
      emit('axis-moved', { axis, direction: 'increase', step: props.selectedSteps });
    }

    function decreaseAxis(axis) {
      store.dispatch("cnc/api_decreaseAxis", {
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
  padding: 1rem;
}

.axis-control {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.axis-control label {
  font-size: 1.2rem;
  font-weight: bold;
  color: white;
}

.button-down,
.button-up {
  background: rgb(41, 41, 41);
  color: #ffffff;
  width: 60px;
  height: 60px;
  border-radius: 8px;
  box-shadow: rgb(41, 41, 41) 0 3px 5px -3px;
  box-sizing: border-box;
  cursor: pointer;
  border: 0;
  font-size: 1.2rem;
  margin: 1%;
  transition: all 0.2s ease;
}

.button-down:hover,
.button-up:hover {
  box-shadow: rgba(255, 255, 255, 0.2) 0 3px 15px inset,
    rgba(0, 0, 0, 0.1) 0 3px 5px, rgba(0, 0, 0, 0.1) 0 10px 13px;
  transform: scale(1.05);
  border: 1px solid rgb(61, 59, 59);
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

