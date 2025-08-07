<template>
  <div class="positions-grid">
    <div class="axis-info">
      <h3>Axis: {{ axisName }}</h3>
    </div>

    <div class="position-layout">
      <div class="data-row">
        <div class="axis-label">X</div>
        <div class="boxed">{{ pos.x.toFixed(3) }}</div>
      </div>
      
      <div class="data-row">
        <div class="axis-label">Y</div>
        <div class="boxed">{{ pos.y.toFixed(3) }}</div>
      </div>
      
      <div class="data-row">
        <div class="axis-label">Z</div>
        <div class="boxed">{{ pos.z.toFixed(3) }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from "vue";
import { useStore } from "vuex";

export default {
  name: "PositionDisplay",
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

    return {
      pos: computed(() => store.getters["cnc/pos"](props.axisUid))
    };
  }
};
</script>

<style scoped>
.positions-grid {
  color: white;
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  justify-content: space-around;
  margin: auto;
}

.position-layout {
  display: flex;
  flex-direction: column;
  width: 95%;
  margin: 0 auto;
  gap: 3px;
}

.data-row {
  display: flex;
  align-items: center;
  gap: 3px;
}

.axis-label {
  width: 30%;
  font-weight: bold;
  font-size: 1.6rem;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 60px;
}

.boxed {
  width: 70%;
  background-color: rgb(41, 41, 41);
  border-radius: 8px;
  padding: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.6rem;
  font-weight: bold;
  font-family: monospace;
  height: 60px;
  box-sizing: border-box;
  color: rgb(224, 181, 102);
}



.axis-info {
  text-align: center;
  margin-bottom: 1rem;
}

.axis-info h3 {
  margin: 0;
  color: #ffffff;
  font-size: 1.4rem;
  font-weight: bold;
}
</style>

