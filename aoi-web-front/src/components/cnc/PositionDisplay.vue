<template>
  <div class="positions-grid">
    <div class="axis-info">
      <h3>{{ axisName }}</h3>
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
import { computed, onMounted } from "vue";
import { useCncStore } from '@/composables/useStore';
import { createLogger } from '@/utils/logger';

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
    const logger = createLogger('PositionDisplay');
    
    // Use centralized CNC store composable
    const { pos } = useCncStore(props.axisUid);
    
    onMounted(() => {
      logger.lifecycle('mounted', 'PositionDisplay component mounted', { axisUid: props.axisUid });
    });

    return {
      pos
    };
  }
};
</script>

<style scoped>
.positions-grid {
  color: var(--color-text-secondary);
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  justify-content: space-around;
  margin: auto;
  background-color: var(--cnc-position-bg);
  border: var(--border-width-1) solid var(--cnc-position-border);
  border-radius: var(--border-radius-card);
  padding: var(--space-4);
}

.position-layout {
  display: flex;
  flex-direction: column;
  width: 95%;
  margin: 0 auto;
  gap: var(--space-1);
}

.data-row {
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.axis-label {
  width: 30%;
  font-weight: var(--font-weight-bold);
  font-size: var(--font-size-2xl);
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: var(--touch-target-min);
}

.boxed {
  width: 70%;
  background-color: var(--color-bg-tertiary);
  border-radius: var(--border-radius-lg);
  padding: var(--space-4);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  font-family: var(--font-family-mono);
  min-height: var(--touch-target-min);
  box-sizing: border-box;
  color: var(--color-primary-light);
  border: var(--border-width-1) solid var(--color-border-secondary);
  transition: var(--transition-hover);
}

.boxed:hover {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-base);
}

.axis-info {
  text-align: center;
  margin-bottom: var(--space-4);
}

.axis-info h3 {
  margin: var(--space-0);
  color: var(--color-text-secondary);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
}
</style>

