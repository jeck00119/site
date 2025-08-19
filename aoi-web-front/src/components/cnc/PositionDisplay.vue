<template>
  <div class="positions-grid">
    <div class="axis-info">
      <h3>{{ axisName }}</h3>
      <button 
        class="cnc-setup-button"
        @click="showCncSetup = true"
        title="CNC Setup & 3D Viewer"
      >
        <font-awesome-icon icon="cog" />
        Setup 3D
      </button>
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

    <!-- 3D Viewer -->
    <CncViewer3D 
      v-if="show3DViewer"
      :cnc-config="cncConfig"
      :axis-uid="axisUid"
      :current-pos="simulatedPos"
      :is-cnc-connected="isCncConnected"
      @close="show3DViewer = false"
      @moveTo="handleMoveTo"
      @simulateMoveTo="handleSimulateMoveTo"
    />

    <!-- CNC Setup Modal -->
    <div v-if="showCncSetup" class="modal-overlay" @click="closeCncSetupModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>CNC Setup & 3D Digital Twin</h3>
          <button class="close-button" @click="closeCncSetupModal">×</button>
        </div>
        
        <div class="modal-body">
          <div class="setup-form">
            <h4>CNC Rig Parameters</h4>
            
            <!-- Manual Axis Selection -->
            <div class="axis-selection">
              <h5>Select Your CNC Axes</h5>
              <div class="axis-checkboxes">
                <div class="axis-checkbox">
                  <input type="checkbox" id="enable-x" v-model="selectedAxes.x" />
                  <label for="enable-x">X-Axis (Linear)</label>
                </div>
                <div class="axis-checkbox">
                  <input type="checkbox" id="enable-y" v-model="selectedAxes.y" />
                  <label for="enable-y">Y-Axis (Linear)</label>
                </div>
                <div class="axis-checkbox">
                  <input type="checkbox" id="enable-z" v-model="selectedAxes.z" />
                  <label for="enable-z">Z-Axis (Linear)</label>
                </div>
                <div class="axis-checkbox">
                  <input type="checkbox" id="enable-a" v-model="selectedAxes.a" />
                  <label for="enable-a">A-Axis (Rotary)</label>
                </div>
                <div class="axis-checkbox">
                  <input type="checkbox" id="enable-b" v-model="selectedAxes.b" />
                  <label for="enable-b">B-Axis (Rotary)</label>
                </div>
                <div class="axis-checkbox">
                  <input type="checkbox" id="enable-c" v-model="selectedAxes.c" />
                  <label for="enable-c">C-Axis (Rotary)</label>
                </div>
              </div>
              <p class="axis-summary">{{ selectedAxesCount }} axes selected: {{ selectedAxesList }}</p>
            </div>

            <!-- Dynamic axis configuration based on selection -->
            <div class="axis-config">
              <h5>Axis Configuration</h5>
              
              <div v-if="selectedAxes.x" class="form-group">
                <label>X-Axis Length (mm):</label>
                <input 
                  type="number" 
                  v-model.number="cncConfig.xAxisLength" 
                  min="1" 
                  max="10000"
                  placeholder="e.g. 300"
                />
              </div>
              
              <div v-if="selectedAxes.y" class="form-group">
                <label>Y-Axis Length (mm):</label>
                <input 
                  type="number" 
                  v-model.number="cncConfig.yAxisLength" 
                  min="1" 
                  max="10000"
                  placeholder="e.g. 300"
                />
              </div>
              
              <div v-if="selectedAxes.z" class="form-group">
                <label>Z-Axis Length (mm):</label>
                <input 
                  type="number" 
                  v-model.number="cncConfig.zAxisLength" 
                  min="1" 
                  max="1000"
                  placeholder="e.g. 100"
                />
              </div>
              
              <div v-if="selectedAxes.a" class="form-group">
                <label>A-Axis Range (degrees):</label>
                <input 
                  type="number" 
                  v-model.number="cncConfig.aAxisRange" 
                  min="0" 
                  max="360"
                  placeholder="e.g. 360"
                />
              </div>
              
              <div v-if="selectedAxes.b" class="form-group">
                <label>B-Axis Range (degrees):</label>
                <input 
                  type="number" 
                  v-model.number="cncConfig.bAxisRange" 
                  min="0" 
                  max="360"
                  placeholder="e.g. 180"
                />
              </div>
              
              <div v-if="selectedAxes.c" class="form-group">
                <label>C-Axis Range (degrees):</label>
                <input 
                  type="number" 
                  v-model.number="cncConfig.cAxisRange" 
                  min="0" 
                  max="360"
                  placeholder="e.g. 360"
                />
              </div>
            </div>

            <!-- Working Zone Configuration (only for selected linear axes) -->
            <div v-if="hasSelectedLinearAxes" class="working-zone-config">
              <h5>Working Zone</h5>
              
              <div v-if="selectedAxes.x" class="form-group">
                <label>Working Zone X (mm):</label>
                <input 
                  type="number" 
                  v-model.number="cncConfig.workingZoneX" 
                  min="1" 
                  :max="cncConfig.xAxisLength"
                  placeholder="e.g. 250"
                />
              </div>
              
              <div v-if="selectedAxes.y" class="form-group">
                <label>Working Zone Y (mm):</label>
                <input 
                  type="number" 
                  v-model.number="cncConfig.workingZoneY" 
                  min="1" 
                  :max="cncConfig.yAxisLength"
                  placeholder="e.g. 250"
                />
              </div>
              
              <div v-if="selectedAxes.z" class="form-group">
                <label>Working Zone Z (mm):</label>
                <input 
                  type="number" 
                  v-model.number="cncConfig.workingZoneZ" 
                  min="1" 
                  :max="cncConfig.zAxisLength"
                  placeholder="e.g. 80"
                />
              </div>
            </div>
            
            <!-- Machine Type (simplified to 3 main types) -->
            <div class="form-group">
              <label>CNC Type:</label>
              <select v-model="cncConfig.cncType">
                <option v-if="selectedAxes.x && selectedAxes.y" value="cartesian">Cartesian</option>
                <option v-if="selectedAxes.x && selectedAxes.y" value="corexy">CoreXY</option>
                <option v-if="selectedAxes.x && selectedAxes.y" value="delta">Delta</option>
              </select>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="cancel-button" @click="closeCncSetupModal">Cancel</button>
          <button class="save-button" @click="saveCncConfigAndOpen3D">
            Generate 3D Model
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, onMounted, ref, watch } from "vue";
import { useCncStore } from '@/composables/useStore';
import { useCncMovement } from '@/composables/useCncMovement';
import { logger } from '@/utils/logger';
import CncViewer3D from './CncViewer3D.vue';

export default {
  name: "PositionDisplay",
  components: {
    CncViewer3D
  },
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
    
    // Use centralized CNC store composable
    const { pos, cncState } = useCncStore(props.axisUid);
    
    // Use CNC movement composable for click-to-move functionality
    const { executeMovementToPosition, isMoving } = useCncMovement(props.axisUid);
    
    // CNC Setup Modal state
    const showCncSetup = ref(false);
    
    // 3D Viewer state
    const show3DViewer = ref(false);
    
    // Simulated position for testing (starts with real position)
    const simulatedPos = ref({ ...pos.value });
    
    // Default CNC configuration
    const defaultCncConfig = {
      xAxisLength: 300,
      yAxisLength: 300,
      zAxisLength: 100,
      aAxisRange: 360,
      bAxisRange: 180,
      cAxisRange: 360,
      workingZoneX: 250,
      workingZoneY: 250,
      workingZoneZ: 80,
      cncType: 'cartesian'
    };
    
    const cncConfig = ref({ ...defaultCncConfig });
    
    // Load saved configuration if available
    const configKey = `cnc-3d-config-${props.axisUid}`;
    const loadCncConfig = () => {
      try {
        const saved = localStorage.getItem(configKey);
        if (saved) {
          const parsed = JSON.parse(saved);
          cncConfig.value = { ...defaultCncConfig, ...parsed };
          
          // Load selected axes if saved
          if (parsed.selectedAxes) {
            selectedAxes.value = { ...selectedAxes.value, ...parsed.selectedAxes };
          }
        }
      } catch (error) {
        logger.warn('Failed to load CNC 3D config:', error);
      }
    };
    
    // Save configuration to localStorage
    const saveCncConfig = () => {
      try {
        const configToSave = {
          ...cncConfig.value,
          selectedAxes: selectedAxes.value
        };
        localStorage.setItem(configKey, JSON.stringify(configToSave));
        logger.info('CNC 3D configuration saved:', configToSave);
      } catch (error) {
        logger.error('Failed to save CNC 3D config:', error);
      }
    };
    
    // Modal functions
    const closeCncSetupModal = () => {
      showCncSetup.value = false;
    };
    
    // Enhanced validation for selected axes
    const validateConfiguration = () => {
      const errors = [];
      
      // Check if at least one axis is selected
      if (selectedAxesCount.value === 0) {
        errors.push('Please select at least one axis');
        return errors;
      }
      
      // Validate required linear axes
      if (selectedAxes.value.x && (!cncConfig.value.xAxisLength || cncConfig.value.xAxisLength <= 0)) {
        errors.push('X-axis length is required and must be greater than 0');
      }
      if (selectedAxes.value.y && (!cncConfig.value.yAxisLength || cncConfig.value.yAxisLength <= 0)) {
        errors.push('Y-axis length is required and must be greater than 0');
      }
      if (selectedAxes.value.z && (!cncConfig.value.zAxisLength || cncConfig.value.zAxisLength <= 0)) {
        errors.push('Z-axis length is required and must be greater than 0');
      }
      
      // Validate rotary axes ranges
      if (selectedAxes.value.a && (!cncConfig.value.aAxisRange || cncConfig.value.aAxisRange <= 0 || cncConfig.value.aAxisRange > 360)) {
        errors.push('A-axis range must be between 1 and 360 degrees');
      }
      if (selectedAxes.value.b && (!cncConfig.value.bAxisRange || cncConfig.value.bAxisRange <= 0 || cncConfig.value.bAxisRange > 360)) {
        errors.push('B-axis range must be between 1 and 360 degrees');
      }
      if (selectedAxes.value.c && (!cncConfig.value.cAxisRange || cncConfig.value.cAxisRange <= 0 || cncConfig.value.cAxisRange > 360)) {
        errors.push('C-axis range must be between 1 and 360 degrees');
      }
      
      // Validate working zones don't exceed axis lengths
      if (selectedAxes.value.x && cncConfig.value.workingZoneX > cncConfig.value.xAxisLength) {
        errors.push('X working zone cannot exceed X-axis length');
      }
      if (selectedAxes.value.y && cncConfig.value.workingZoneY > cncConfig.value.yAxisLength) {
        errors.push('Y working zone cannot exceed Y-axis length');
      }
      if (selectedAxes.value.z && cncConfig.value.workingZoneZ > cncConfig.value.zAxisLength) {
        errors.push('Z working zone cannot exceed Z-axis length');
      }
      
      return errors;
    };
    
    // Main function to save config and open 3D viewer
    const saveCncConfigAndOpen3D = () => {
      // Validate configuration based on selected axes
      const validationErrors = validateConfiguration();
      if (validationErrors.length > 0) {
        alert(`Configuration errors:\n${validationErrors.join('\n')}`);
        return;
      }
      
      // Save configuration including selected axes
      saveCncConfig();
      
      // Close modal
      closeCncSetupModal();
      
      // Open 3D viewer in new window
      open3DViewer();
    };
    
    // Function to open 3D viewer
    const open3DViewer = () => {
      logger.info('Opening 3D CNC viewer with config:', cncConfig.value);
      show3DViewer.value = true;
    };
    
    // Manual axis selection
    const selectedAxes = ref({
      x: true,  // Default to XYZ for common 3-axis machines
      y: true,
      z: true,
      a: false,
      b: false,
      c: false
    });
    
    // Computed properties for manual selection
    const selectedAxesCount = computed(() => {
      return Object.values(selectedAxes.value).filter(Boolean).length;
    });
    
    const selectedAxesList = computed(() => {
      return Object.entries(selectedAxes.value)
        .filter(([axis, selected]) => selected)
        .map(([axis]) => axis.toUpperCase())
        .join(', ');
    });
    
    const hasSelectedLinearAxes = computed(() => {
      return selectedAxes.value.x || selectedAxes.value.y || selectedAxes.value.z;
    });
    
    const hasSelectedRotaryAxes = computed(() => {
      return selectedAxes.value.a || selectedAxes.value.b || selectedAxes.value.c;
    });
    
    const isSelectedCartesian = computed(() => {
      return selectedAxes.value.x && selectedAxes.value.y && selectedAxes.value.z && !hasSelectedRotaryAxes.value;
    });
    
    // Check if CNC is connected and ready for movement
    const isCncConnected = computed(() => {
      const state = cncState?.value;
      // CNC is considered connected if it has a valid state (not null/undefined/'UNKNOWN')
      return state && state.toUpperCase() !== 'UNKNOWN' && state.toUpperCase() !== 'ALARM';
    });
    
    // Handle click-to-move from 3D viewer
    const handleMoveTo = async (targetPosition) => {
      try {
        logger.info('3D Viewer click-to-move request:', targetPosition);
        
        // Check if CNC is connected first
        if (!isCncConnected.value) {
          logger.warn('CNC not connected, ignoring click-to-move request');
          logger.info('Current CNC state:', cncState?.value);
          return;
        }
        
        if (isMoving.value) {
          logger.warn('CNC is already moving, ignoring click-to-move request');
          return;
        }
        
        // Execute movement using the composable
        await executeMovementToPosition({
          x: targetPosition.x,
          y: targetPosition.y,
          z: targetPosition.z,
          name: '3D Click Target',
          feedrate: 1500 // Default feedrate for click-to-move
        });
        
        logger.info('Click-to-move completed successfully');
      } catch (error) {
        logger.error('Click-to-move failed:', error);
        // Could add a notification here for user feedback
      }
    };
    
    // Handle simulation click-to-move (updates local position without real CNC command)
    const handleSimulateMoveTo = (targetPosition) => {
      logger.info('Simulation: Moving to position', targetPosition);
      simulatedPos.value = {
        x: targetPosition.x,
        y: targetPosition.y,
        z: targetPosition.z
      };
    };
    
    // Watch for real position changes to update simulated position
    watch(pos, (newPos) => {
      if (newPos) {
        simulatedPos.value = { ...newPos };
      }
    }, { deep: true });
    
    onMounted(() => {
      logger.lifecycle('mounted', 'PositionDisplay component mounted', { axisUid: props.axisUid });
      loadCncConfig();
    });

    return {
      pos,
      showCncSetup,
      show3DViewer,
      cncConfig,
      closeCncSetupModal,
      saveCncConfigAndOpen3D,
      handleMoveTo,
      handleSimulateMoveTo,
      isMoving,
      isCncConnected,
      simulatedPos,
      // Manual axis selection
      selectedAxes,
      selectedAxesCount,
      selectedAxesList,
      hasSelectedLinearAxes,
      hasSelectedRotaryAxes,
      isSelectedCartesian
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
  gap: var(--space-3);
}

.position-section h4 {
  margin: 0 0 var(--space-2) 0;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
  text-align: center;
  text-transform: uppercase;
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

.boxed.target {
  background-color: var(--color-warning-light);
  color: var(--color-warning-dark);
  border-color: var(--color-warning);
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

.cnc-setup-button {
  margin-top: var(--space-2);
  background-color: var(--color-primary);
  color: var(--color-text-on-primary);
  border: none;
  border-radius: var(--border-radius-lg);
  padding: var(--space-2) var(--space-3);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: var(--transition-hover);
  display: flex;
  align-items: center;
  gap: var(--space-1);
  min-height: var(--touch-target-min);
}

.cnc-setup-button:hover {
  background-color: var(--color-primary-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-base);
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: var(--color-bg-primary);
  border-radius: var(--border-radius-card);
  box-shadow: var(--shadow-lg);
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  border: var(--border-width-1) solid var(--color-border-primary);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4);
  border-bottom: var(--border-width-1) solid var(--color-border-secondary);
  background-color: var(--color-bg-secondary);
  border-top-left-radius: var(--border-radius-card);
  border-top-right-radius: var(--border-radius-card);
}

.modal-header h3 {
  margin: 0;
  color: var(--color-text-primary);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
}

.close-button {
  background: none;
  border: none;
  font-size: var(--font-size-xl);
  color: var(--color-text-secondary);
  cursor: pointer;
  padding: var(--space-1);
  border-radius: var(--border-radius-base);
  min-height: var(--touch-target-min);
  min-width: var(--touch-target-min);
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-button:hover {
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-primary);
}

.modal-body {
  padding: var(--space-4);
}

.setup-form h4 {
  margin: 0 0 var(--space-4) 0;
  color: var(--color-primary);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-bold);
}

.form-group {
  margin-bottom: var(--space-3);
}

.form-group label {
  display: block;
  margin-bottom: var(--space-1);
  color: var(--color-text-primary);
  font-weight: var(--font-weight-medium);
  font-size: var(--font-size-sm);
}

.form-group input,
.form-group select {
  width: 100%;
  padding: var(--space-2);
  border: var(--border-width-1) solid var(--color-border-secondary);
  border-radius: var(--border-radius-base);
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
  min-height: var(--touch-target-min);
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(var(--color-primary-rgb), 0.2);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  padding: var(--space-4);
  border-top: var(--border-width-1) solid var(--color-border-secondary);
  background-color: var(--color-bg-secondary);
  border-bottom-left-radius: var(--border-radius-card);
  border-bottom-right-radius: var(--border-radius-card);
}

.cancel-button {
  padding: var(--space-2) var(--space-4);
  border: var(--border-width-1) solid var(--color-border-secondary);
  border-radius: var(--border-radius-base);
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-primary);
  cursor: pointer;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  min-height: var(--touch-target-min);
  transition: var(--transition-hover);
}

.cancel-button:hover {
  background-color: var(--color-bg-quaternary);
  border-color: var(--color-border-primary);
}

.save-button {
  padding: var(--space-2) var(--space-4);
  border: none;
  border-radius: var(--border-radius-base);
  background-color: var(--color-primary);
  color: var(--color-text-on-primary);
  cursor: pointer;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  min-height: var(--touch-target-min);
  transition: var(--transition-hover);
}

.save-button:hover {
  background-color: var(--color-primary-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-base);
}

/* Manual Axis Selection Styles */
.axis-selection {
  margin-bottom: var(--space-4);
  padding: var(--space-3);
  border: var(--border-width-1) solid var(--color-border-secondary);
  border-radius: var(--border-radius-base);
  background-color: var(--color-bg-tertiary);
}

.axis-selection h5 {
  margin: 0 0 var(--space-3) 0;
  color: var(--color-primary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
}

.axis-checkboxes {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-2);
  margin-bottom: var(--space-3);
}

.axis-checkbox {
  display: flex;
  align-items: center;
  padding: var(--space-2);
  border-radius: var(--border-radius-base);
  background-color: var(--color-bg-quaternary);
  border: var(--border-width-1) solid var(--color-border-tertiary);
  transition: var(--transition-hover);
  gap: var(--space-2);
}

.axis-checkbox:hover {
  background-color: var(--color-bg-secondary);
  border-color: var(--color-primary);
}

.axis-checkbox input[type="checkbox"] {
  accent-color: var(--color-primary);
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.axis-checkbox label {
  font-weight: var(--font-weight-medium);
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  cursor: pointer;
  flex: 1;
}

.axis-summary {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  text-align: center;
  padding: var(--space-2);
  background-color: var(--color-bg-quaternary);
  border-radius: var(--border-radius-base);
}

/* Axis Configuration Styles */
.axis-config {
  margin-bottom: var(--space-4);
}

.axis-config h5 {
  margin: 0 0 var(--space-3) 0;
  color: var(--color-primary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
}

/* Working Zone Configuration Styles */
.working-zone-config {
  margin-bottom: var(--space-4);
}

.working-zone-config h5 {
  margin: 0 0 var(--space-3) 0;
  color: var(--color-primary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
}
</style>

