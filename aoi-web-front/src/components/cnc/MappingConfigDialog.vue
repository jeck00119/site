<template>
  <!-- Modal overlay matching the 3D CNC setup pattern -->
  <div v-if="show" 
       class="modal-overlay" 
       @click.self="$emit('close')">
    <div class="modal-content">
      <!-- Modal Header -->
      <div class="modal-header">
        <h3>Map Working Area Configuration</h3>
        <button @click="$emit('close')" class="close-btn" aria-label="Close">
          ✕
        </button>
      </div>

      <!-- Modal Body -->
      <div class="modal-body">
        <div class="mapping-config">
          <!-- Validation Errors at the top -->
          <div v-if="validationErrors.length > 0" class="validation-errors">
            <h4>Configuration Issues:</h4>
            <ul>
              <li v-for="error in validationErrors" :key="error">{{ error }}</li>
            </ul>
          </div>
          
          <div class="config-section">
        <h3>Grid Settings</h3>
        
        <div class="form-row">
          <div class="form-group">
            <label for="stepSizeX">X Step Size (mm):</label>
            <input
              id="stepSizeX"
              v-model.number="config.stepSize.x"
              type="number"
              min="1"
              max="50"
              step="1"
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label for="stepSizeY">Y Step Size (mm):</label>
            <input
              id="stepSizeY"
              v-model.number="config.stepSize.y"
              type="number"
              min="1"
              max="50"
              step="1"
              class="form-input"
            />
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label for="zHeight">Camera Height (mm):</label>
            <input
              id="zHeight"
              v-model.number="config.zHeight"
              type="number"
              min="5"
              max="100"
              step="0.5"
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label for="overlap">Overlap (%):</label>
            <input
              id="overlap"
              v-model.number="config.overlapPercent"
              type="number"
              min="20"
              max="60"
              step="5"
              class="form-input"
            />
          </div>
        </div>
      </div>

      <div class="config-section">
        <h3>Working Area</h3>
        <div class="area-info">
          <div class="area-bounds">
            <span>X: 0 → {{ workingAreaBounds.x }}mm</span>
            <span>Y: 0 → {{ workingAreaBounds.y }}mm</span>
          </div>
          <div class="grid-preview">
            <span>Estimated grid points: {{ estimatedGridPoints }}</span>
            <span>Estimated time: {{ estimatedTime }}</span>
          </div>
        </div>
      </div>

      <div class="config-section">
        <h3>Movement Pattern</h3>
        <div class="pattern-selection">
          <label class="radio-option">
            <input
              v-model="config.pattern"
              type="radio"
              value="zigzag"
            />
            <span>Zigzag (Efficient)</span>
          </label>
          <label class="radio-option">
            <input
              v-model="config.pattern"
              type="radio"
              value="raster"
            />
            <span>Raster (Predictable)</span>
          </label>
        </div>
      </div>
      
      <!-- Mapping Progress -->
      <div v-if="isMappingInProgress" class="mapping-progress">
        <h4>Mapping in Progress</h4>
        <div class="progress-info">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: `${mappingProgress}%` }"></div>
          </div>
          <div class="progress-stats">
            <span class="progress-percentage">{{ mappingProgress }}%</span>
            <span v-if="totalGridPoints > 0" class="progress-points">
              {{ completedPoints }} / {{ totalGridPoints }} points
            </span>
          </div>
        </div>
        <div class="progress-status">{{ mappingStatus }}</div>
        <div v-if="currentGridPosition.x !== undefined" class="current-position">
          Current: ({{ currentGridPosition.x.toFixed(1) }}, {{ currentGridPosition.y.toFixed(1) }})
        </div>
        </div>
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="modal-footer">
        <button 
          @click="startMapping" 
          :disabled="!isConfigValid"
          class="btn-primary"
        >
          Start Mapping
        </button>
        <button @click="$emit('close')" class="btn-secondary">
          Cancel
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { getWorkingZoneBounds, formatCoordinate } from '@/utils/validation';
import type { CncConfig } from '@/utils/validation';

export interface MappingConfig {
  stepSize: {
    x: number;
    y: number;
  };
  zHeight: number;
  overlapPercent: number;
  pattern: 'zigzag' | 'raster';
}

export interface Props {
  show: boolean;
  cncConfig: CncConfig | null;
  isMappingInProgress?: boolean;
  mappingProgress?: number;
  mappingStatus?: string;
  currentGridPosition?: { x: number; y: number };
  totalGridPoints?: number;
  completedPoints?: number;
}

interface Emits {
  close: [];
  startMapping: [config: MappingConfig];
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

// Default configuration
const config = ref<MappingConfig>({
  stepSize: {
    x: 10,
    y: 10
  },
  zHeight: 20,
  overlapPercent: 30,
  pattern: 'zigzag'
});

// Working area bounds from CNC config
const workingAreaBounds = computed(() => {
  if (!props.cncConfig) return { x: 0, y: 0, z: 0 };
  return getWorkingZoneBounds(props.cncConfig, false);
});

// Estimated grid points calculation
const estimatedGridPoints = computed(() => {
  const bounds = workingAreaBounds.value;
  if (!bounds.x || !bounds.y) return 0;
  
  const pointsX = Math.ceil(bounds.x / config.value.stepSize.x) + 1;
  const pointsY = Math.ceil(bounds.y / config.value.stepSize.y) + 1;
  
  return pointsX * pointsY;
});

// Estimated time calculation (assuming 3 seconds per point)
const estimatedTime = computed(() => {
  const totalPoints = estimatedGridPoints.value;
  const timePerPoint = 3; // seconds per capture + movement
  const totalSeconds = totalPoints * timePerPoint;
  
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  
  if (minutes > 0) {
    return `${minutes}m ${seconds}s`;
  }
  return `${seconds}s`;
});

// Validation
const validationErrors = computed(() => {
  const errors: string[] = [];
  
  if (config.value.stepSize.x < 1 || config.value.stepSize.x > 50) {
    errors.push('X step size must be between 1-50mm');
  }
  
  if (config.value.stepSize.y < 1 || config.value.stepSize.y > 50) {
    errors.push('Y step size must be between 1-50mm');
  }
  
  if (config.value.zHeight < 5 || config.value.zHeight > 100) {
    errors.push('Camera height must be between 5-100mm');
  }
  
  if (config.value.overlapPercent < 20 || config.value.overlapPercent > 60) {
    errors.push('Overlap must be between 20-60%');
  }
  
  if (estimatedGridPoints.value > 1000) {
    errors.push('Grid too dense - reduce step size or working area');
  }
  
  if (!props.cncConfig || !workingAreaBounds.value.x || !workingAreaBounds.value.y) {
    errors.push('Invalid CNC configuration - working area not defined');
  }
  
  return errors;
});

const isConfigValid = computed(() => validationErrors.value.length === 0);

// Start mapping action
const startMapping = () => {
  if (isConfigValid.value) {
    emit('startMapping', { ...config.value });
  }
};
</script>

<style scoped>
/* Modal overlay matching 3D CNC setup pattern */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
  z-index: 9999;
  overflow: hidden;
}

.modal-content {
  background-color: var(--color-bg-primary, #1a1a1a);
  border-radius: var(--border-radius-card, 8px);
  box-shadow: var(--shadow-lg, 0 4px 20px rgba(0, 0, 0, 0.5));
  width: 90%;
  max-width: 600px;
  height: auto;
  max-height: 95vh;
  display: flex;
  flex-direction: column;
  border: var(--border-width-1, 1px) solid var(--color-border-primary, #333);
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4, 1rem);
  background-color: var(--color-bg-secondary, #222);
  border-bottom: 1px solid var(--color-border-primary, #333);
  border-top-left-radius: var(--border-radius-card, 8px);
  border-top-right-radius: var(--border-radius-card, 8px);
}

.modal-header h3 {
  margin: 0;
  color: var(--color-text-primary, #ffffff);
  font-size: var(--font-size-lg, 1.3rem);
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: var(--color-text-primary, #ffffff);
  padding: 0.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: rgb(204, 161, 82);
}

.modal-body {
  padding: var(--space-4, 1rem);
  flex: 1;
  overflow-y: auto;
  max-height: calc(95vh - 120px);
}

.modal-footer {
  display: flex;
  justify-content: center;
  gap: var(--space-3, 0.75rem);
  padding: var(--space-4, 1rem);
  border-top: 1px solid var(--color-border-primary, #333);
  background-color: var(--color-bg-secondary, #222);
}

.mapping-config {
  color: var(--text-primary, #ffffff);
}

.config-section {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-light, #333);
}

.config-section:last-child {
  border-bottom: none;
}

.config-section h3 {
  margin: 0 0 1rem 0;
  color: var(--color-primary, rgb(204, 161, 82));
  font-size: 1.1rem;
}

.form-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-group {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 0.25rem;
  font-size: 0.9rem;
  color: var(--text-secondary, #ccc);
}

.form-input {
  padding: 0.5rem;
  border: 1px solid var(--border-light, #333);
  border-radius: 0.25rem;
  background-color: var(--bg-secondary, #222);
  color: var(--text-primary, #fff);
  font-size: 0.9rem;
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary, rgb(204, 161, 82));
}

.area-info {
  background-color: var(--bg-secondary, #222);
  padding: 1rem;
  border-radius: 0.5rem;
  border: 1px solid var(--border-light, #333);
}

.area-bounds {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.5rem;
  font-family: 'Consolas', monospace;
}

.area-bounds span {
  color: var(--color-success, #51cf66);
}

.grid-preview {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.9rem;
  color: var(--text-muted, #888);
}

.pattern-selection {
  display: flex;
  gap: 1rem;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.radio-option input[type="radio"] {
  margin: 0;
}

.radio-option:hover {
  color: var(--color-primary, rgb(204, 161, 82));
}

.validation-errors {
  background-color: rgba(255, 71, 87, 0.15);
  border: 1px solid rgba(255, 71, 87, 0.5);
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 1rem;
}

.validation-errors h4 {
  margin: 0 0 0.5rem 0;
  color: #ff4757;
  font-size: 1rem;
  font-weight: 600;
}

.validation-errors ul {
  margin: 0;
  padding-left: 1.2rem;
  list-style-position: outside;
}

.validation-errors li {
  color: #ff6b7a;
  font-size: 0.9rem;
  line-height: 1.4;
  margin-bottom: 0.3rem;
  text-align: left;
}

.btn-secondary,
.btn-primary {
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  margin-left: 0.5rem;
}

.btn-secondary {
  background-color: var(--bg-secondary, #333);
  color: var(--text-primary, #fff);
  border: 1px solid var(--border-light, #666);
}

.btn-secondary:hover {
  background-color: var(--bg-tertiary, #444);
}

.btn-primary {
  background-color: var(--color-primary, rgb(204, 161, 82));
  color: var(--text-on-primary, #000);
}

.btn-primary:hover:not(:disabled) {
  background-color: var(--color-primary-dark, rgb(184, 141, 62));
}

.btn-primary:disabled {
  background-color: var(--bg-muted, #666);
  color: var(--text-muted, #999);
  cursor: not-allowed;
}

.mapping-progress {
  background-color: var(--bg-secondary, #222);
  border: 1px solid var(--color-primary, rgb(204, 161, 82));
  border-radius: 0.5rem;
  padding: 1rem;
  margin-top: 1rem;
}

.mapping-progress h4 {
  margin: 0 0 1rem 0;
  color: var(--color-primary, rgb(204, 161, 82));
  font-size: 1.1rem;
}

.progress-info {
  margin-bottom: 1rem;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background-color: var(--bg-tertiary, #333);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-fill {
  height: 100%;
  background-color: var(--color-primary, rgb(204, 161, 82));
  transition: width 0.3s ease;
}

.progress-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
}

.progress-percentage {
  font-weight: bold;
  color: var(--color-primary, rgb(204, 161, 82));
}

.progress-points {
  color: var(--text-secondary, #ccc);
}

.progress-status {
  color: var(--text-primary, #fff);
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.current-position {
  color: var(--color-success, #51cf66);
  font-family: 'Consolas', monospace;
  font-size: 0.9rem;
}

/* Responsive adjustments matching modal pattern */
@media (max-height: 600px) {
  .modal-overlay {
    padding-top: 2vh;
    padding-bottom: 100px;
  }
  
  .modal-content {
    max-height: calc(100vh - 150px);
  }
}

@media (max-width: 768px) {
  .modal-overlay {
    padding-top: 2vh;
    padding-left: var(--space-2, 0.5rem);
    padding-right: var(--space-2, 0.5rem);
  }
  
  .modal-content {
    width: 95%;
    max-width: none;
  }
  
  .modal-body {
    padding: var(--space-3, 0.75rem);
  }
  
  .modal-header,
  .modal-footer {
    padding: var(--space-3, 0.75rem);
  }
  
  .form-row {
    flex-direction: column;
  }
  
  .area-bounds {
    flex-direction: column;
  }
  
  .pattern-selection {
    flex-direction: column;
  }
}
</style>