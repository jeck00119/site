<template>
  <div class="positions-grid">
    <div class="axis-info">
      <h3>Axis: {{ axisName }}</h3>
    </div>

    <div class="col-container">
      <div class="axis">
        <div>Axis</div>
        <div>X</div>
        <div>Y</div>
        <div>Z</div>
      </div>

      <div class="position">
        <div>Position</div>
        <div class="boxed">{{ pos.x.toFixed(3) }}</div>
        <div class="boxed">{{ pos.y.toFixed(3) }}</div>
        <div class="boxed">{{ pos.z.toFixed(3) }}</div>
      </div>

      <div class="m-position">
        <div>Position(M)</div>
        <div class="boxed">{{ mPos.x.toFixed(3) }}</div>
        <div class="boxed">{{ mPos.y.toFixed(3) }}</div>
        <div class="boxed">{{ mPos.z.toFixed(3) }}</div>
      </div>

      <div class="w-position">
        <div>Position(W)</div>
        <div class="boxed">{{ wPos.x.toFixed(3) }}</div>
        <div class="boxed">{{ wPos.y.toFixed(3) }}</div>
        <div class="boxed">{{ wPos.z.toFixed(3) }}</div>
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
      pos: computed(() => store.getters["cnc/pos"](props.axisUid)),
      mPos: computed(() => store.getters["cnc/mPos"](props.axisUid)),
      wPos: computed(() => store.getters["cnc/wPos"](props.axisUid))
    };
  }
};
</script>

<style scoped>
.positions-grid {
  color: white;
  background-color: #161616;
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  justify-content: space-around;
  margin: auto;
  border-radius: 8px;
  padding: 1rem;
}

.col-container {
  display: flex;
  justify-content: center;
  width: 95%;
  margin: 0 auto;
}

.axis {
  display: flex;
  flex-direction: column;
  width: 50%;
  flex-grow: 1;
  height: 100%;
}

.position {
  display: flex;
  flex-direction: column;
  width: 100%;
  flex-grow: 2;
  height: 100%;
}

.m-position {
  display: flex;
  flex-direction: column;
  width: 100%;
  flex-grow: 2;
}

.w-position {
  display: flex;
  flex-direction: column;
  width: 100%;
  flex-grow: 2;
}

.boxed {
  height: 100%;
  width: 100%;
  background-color: rgb(41, 41, 41);
  border-radius: 4px;
  padding: 0.5rem;
  margin: 2px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.axis-info {
  text-align: center;
  margin-bottom: 1rem;
}

.axis-info h3 {
  margin: 0;
  color: #ffffff;
  font-size: 1.2rem;
}
</style>

