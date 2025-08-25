<template>
  <div class="positions-grid">
    <div class="axis-info">
      <h3>{{ axisName }}</h3>
    </div>

    <div class="position-layout">
      <div class="data-row">
        <div class="axis-label">X</div>
        <div class="boxed">{{ formatCoordinate(pos.x) }}</div>
      </div>
      
      <div class="data-row">
        <div class="axis-label">Y</div>
        <div class="boxed">{{ formatCoordinate(pos.y) }}</div>
      </div>
      
      <div class="data-row">
        <div class="axis-label">Z</div>
        <div class="boxed">{{ formatCoordinate(pos.z) }}</div>
      </div>
    </div>

    <!-- 3D Viewer -->
    <CncViewer3D 
      ref="cncViewer3D"
      v-if="show3DViewer"
      :cnc-config="cncConfig"
      :axis-uid="axisUid"
      :current-pos="simulatedPos"
      :is-cnc-connected="isCncConnected"
      @close="show3DViewer = false"
      @moveTo="handleMoveTo"
      @simulateMoveTo="handleSimulateMoveTo"
      @simulationModeChanged="handleSimulationModeChanged"
      @initSuccess="on3DViewerSuccess"
      @initFailure="on3DViewerFailure"
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
            
            <!-- Validation Errors Display -->
            <div v-if="currentValidationErrors.length > 0" class="validation-errors">
              <div class="error-header">
                <font-awesome-icon icon="exclamation-triangle" />
                <span>Please fix the following issues:</span>
              </div>
              <ul class="error-list">
                <li v-for="error in currentValidationErrors" :key="error" class="error-item">
                  {{ error }}
                </li>
              </ul>
            </div>
            
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
            
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="cancel-button" @click="closeCncSetupModal">Cancel</button>
          <button 
            class="save-button" 
            @click="saveCncConfigAndOpen3D"
            :disabled="currentValidationErrors.length > 0"
            :class="{ 'disabled': currentValidationErrors.length > 0 }"
          >
            Generate 3D Model
          </button>
        </div>
      </div>
    </div>
    
    <!-- 3D Control Buttons -->
    <div class="button-group button-group-bottom">
      <button 
        class="cnc-3d-button gear-style-button"
        @click="handle3DCNCClick"
        title="3D CNC Viewer"
        :disabled="!hasConfig"
      >
        <font-awesome-icon icon="cube" /> 3D CNC
      </button>
      <button 
        class="cnc-setup-button gear-style-button"
        @click="handleSetup3DClick"
        title="Setup 3D Configuration"
      >
        <font-awesome-icon icon="gear" /> Setup
      </button>
    </div>
  </div>
</template>

<script>
import { computed, onMounted, ref, watch, nextTick } from "vue";
import { useCncStore } from '@/composables/useStore';
import { useCncMovement } from '@/composables/useCncMovement';
import { formatCoordinate, validateCnc3DConfig, requires3DSetup, get3DSetupMessage } from '@/utils/validation';
import { logger } from '@/utils/logger';
import { formatValidationError } from '@/utils/errorHandler';
import { CncMessages, NotificationType, createNotification } from '@/constants/notifications';
import useNotification from '@/hooks/notifications';
import CncViewer3D from './CncViewer3D.vue';
import { library } from '@fortawesome/fontawesome-svg-core';
import { faGear, faCube, faExclamationTriangle } from '@fortawesome/free-solid-svg-icons';

library.add(faGear, faCube, faExclamationTriangle);

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
    const { pos, cncState, cncs, saveCNC3DConfig } = useCncStore(props.axisUid);
    
    // Use CNC movement composable for click-to-move functionality
    const { executeMovementToPosition, isMoving } = useCncMovement(props.axisUid);
    
    // Use centralized notification system
    const { setTypedNotification } = useNotification();
    
    // Default CNC configuration - now defaults to 0 to force user setup
    const defaultCncConfig = {
      xAxisLength: 0,
      yAxisLength: 0,
      zAxisLength: 0,
      workingZoneX: 0,
      workingZoneY: 0,
      workingZoneZ: 0
    };
    
    // CNC Setup Modal state
    const showCncSetup = ref(false);
    const lastSavedConfig = ref({ ...defaultCncConfig });
    const lastSavedSelectedAxes = ref({ x: true, y: true, z: true });
    
    // 3D Viewer state
    const show3DViewer = ref(false);
    const cncViewer3D = ref(null);
    
    // Simulated position for testing (starts with real position)
    const simulatedPos = ref({ ...pos.value });
    
    const cncConfig = ref({ ...defaultCncConfig });
    
    // Load saved configuration from database only (not localStorage)
    const loadCncConfig = () => {
      try {
        // Only load from backend CNC configuration (database)
        const currentCnc = cncs.value?.find(cnc => cnc.uid === props.axisUid);
        
        // Check if backend has valid 3D config (values > 0)
        const hasValidBackendConfig = currentCnc && (
          (currentCnc.xAxisLength > 0 || currentCnc.x_axis_length > 0) ||
          (currentCnc.yAxisLength > 0 || currentCnc.y_axis_length > 0) ||
          (currentCnc.zAxisLength > 0 || currentCnc.z_axis_length > 0)
        );
        
        if (hasValidBackendConfig) {
          // Load from backend CNC config - handle both camelCase and snake_case
          const loadedConfig = {
            xAxisLength: currentCnc.xAxisLength || currentCnc.x_axis_length || 0,
            yAxisLength: currentCnc.yAxisLength || currentCnc.y_axis_length || 0,
            zAxisLength: currentCnc.zAxisLength || currentCnc.z_axis_length || 0,
            workingZoneX: currentCnc.workingZoneX || currentCnc.working_zone_x || 0,
            workingZoneY: currentCnc.workingZoneY || currentCnc.working_zone_y || 0,
            workingZoneZ: currentCnc.workingZoneZ || currentCnc.working_zone_z || 0
          };
          
          // Handle selected axes
          const loadedSelectedAxes = currentCnc.selectedAxes || currentCnc.selected_axes || { x: true, y: true, z: true };
          
          // Set both current and last saved (since this came from database)
          cncConfig.value = { ...loadedConfig };
          selectedAxes.value = { ...loadedSelectedAxes };
          lastSavedConfig.value = { ...loadedConfig };
          lastSavedSelectedAxes.value = { ...loadedSelectedAxes };
          
          logger.info('CNC 3D config loaded from database:', loadedConfig);
        } else {
          // No valid config in database, use defaults
          cncConfig.value = { ...defaultCncConfig };
          selectedAxes.value = { x: true, y: true, z: true };
          lastSavedConfig.value = { ...defaultCncConfig };
          lastSavedSelectedAxes.value = { x: true, y: true, z: true };
          
          logger.info('No valid CNC 3D config in database, using defaults');
        }
        
      } catch (error) {
        logger.warn('Failed to load CNC 3D config:', error);
        
        // Fallback to defaults on error
        cncConfig.value = { ...defaultCncConfig };
        selectedAxes.value = { x: true, y: true, z: true };
        lastSavedConfig.value = { ...defaultCncConfig };
        lastSavedSelectedAxes.value = { x: true, y: true, z: true };
      }
    };
    
    // Save configuration to database only (no localStorage persistence)
    const saveCncConfig = async () => {
      const configToSave = {
        xAxisLength: cncConfig.value.xAxisLength,
        yAxisLength: cncConfig.value.yAxisLength,
        zAxisLength: cncConfig.value.zAxisLength,
        workingZoneX: cncConfig.value.workingZoneX,
        workingZoneY: cncConfig.value.workingZoneY,
        workingZoneZ: cncConfig.value.workingZoneZ,
        selectedAxes: selectedAxes.value
      };
      
      // Save only to backend CNC configuration (database)
      const result = await saveCNC3DConfig(props.axisUid, configToSave);
      
      if (result.success) {
        logger.info('CNC 3D configuration saved to database:', configToSave);
      } else {
        // Throw error to be caught by caller - don't save to localStorage as fallback
        const error = new Error('Failed to save CNC 3D configuration to database');
        logger.error(error.message, result);
        throw error;
      }
    };
    
    // Modal functions
    const closeCncSetupModal = () => {
      showCncSetup.value = false;
      
      // Reset form to last saved configuration (don't remember unsaved changes)
      cncConfig.value = { ...lastSavedConfig.value };
      selectedAxes.value = { ...lastSavedSelectedAxes.value };
      
      logger.info('Setup modal closed, form reset to last saved configuration', lastSavedConfig.value);
    };
    
    // Use centralized validation from utils
    const validateConfiguration = () => {
      const configToValidate = {
        ...cncConfig.value,
        selectedAxes: selectedAxes.value
      };
      
      const validation = validateCnc3DConfig(configToValidate);
      return validation.errors;
    };
    
    // Real-time validation - shows errors immediately as user types
    const currentValidationErrors = computed(() => {
      return validateConfiguration();
    });
    
    // Main function to validate and test 3D viewer generation
    const saveCncConfigAndOpen3D = async () => {
      // Double-check validation (button should be disabled if there are errors)
      const validationErrors = validateConfiguration();
      if (validationErrors.length > 0) {
        const formattedError = formatValidationError(validationErrors, 'Configuration');
        setTypedNotification(formattedError, NotificationType.ERROR);
        return;
      }
      
      try {
        logger.info('Testing 3D viewer generation with new configuration...');
        setTypedNotification(CncMessages.VIEWER_INITIALIZING, NotificationType.INFO);
        
        // First, try to open the 3D viewer with the current configuration
        // The 3D viewer will validate the config and fail if there are issues
        open3DViewer();
        
        // If we reach here, the 3D viewer opened successfully
        // Now we can save the configuration and close the modal
        // Note: We'll save after 3D viewer confirms successful initialization
      } catch (error) {
        logger.error('Error testing 3D viewer generation:', error);
        setTypedNotification(CncMessages.VIEWER_ERROR, NotificationType.ERROR);
      }
    };
    
    // Called when 3D viewer successfully initializes
    const on3DViewerSuccess = async () => {
      try {
        logger.info('3D viewer generated successfully, saving configuration to database...');
        
        // Save configuration including selected axes
        await saveCncConfig();
        
        // Remember the successfully saved configuration
        lastSavedConfig.value = { ...cncConfig.value };
        lastSavedSelectedAxes.value = { ...selectedAxes.value };
        
        // Close modal (this will reset form, but that's ok since we just saved)
        closeCncSetupModal();
        
        setTypedNotification(CncMessages.SETUP_SUCCESS, NotificationType.SUCCESS);
        logger.info('CNC 3D configuration saved successfully after viewer generation');
      } catch (error) {
        logger.error('Error saving 3D configuration after successful generation:', error);
        setTypedNotification(CncMessages.SETUP_FAILED, NotificationType.ERROR);
      }
    };
    
    // Called when 3D viewer fails to initialize
    const on3DViewerFailure = (failureInfo) => {
      logger.error('3D viewer generation failed:', failureInfo);
      
      // Close the 3D viewer since it failed
      show3DViewer.value = false;
      
      // Show specific error message based on failure type
      let errorMessage = CncMessages.VIEWER_ERROR;
      if (failureInfo?.type === 'config-validation') {
        errorMessage = failureInfo.error || CncMessages.CONFIG_INCOMPLETE;
        // Reopen setup modal since config is invalid
        showCncSetup.value = true;
      } else if (failureInfo?.error?.includes('WebGL')) {
        errorMessage = CncMessages.WEBGL_NOT_SUPPORTED;
      }
      
      setTypedNotification(errorMessage, NotificationType.ERROR);
      
      // Configuration is NOT saved since 3D viewer failed to generate
      logger.warn('CNC configuration was not saved due to 3D viewer generation failure');
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
      z: true
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
    
    const isSelectedCartesian = computed(() => {
      return selectedAxes.value.x && selectedAxes.value.y && selectedAxes.value.z;
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
        
        // Notify 3D viewer that movement is complete for target arrival indication
        // Use nextTick to ensure the position update has been processed
        await nextTick();
        // Call completion method to trigger green target indication
        if (show3DViewer.value && cncViewer3D.value) {
          cncViewer3D.value.completeRealCNCMovement();
        }
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
    
    // Handle simulation mode changes
    const handleSimulationModeChanged = (event) => {
      if (!event.isSimulationMode && event.realPosition) {
        // Simulation mode disabled - reset simulated position to real position
        logger.info('Simulation mode disabled, resetting simulated position to real position:', event.realPosition);
        simulatedPos.value = { ...event.realPosition };
      }
    };
    
    // Watch for real position changes to update simulated position
    watch(pos, (newPos) => {
      if (newPos) {
        simulatedPos.value = { ...newPos };
      }
    }, { deep: true });

    // Watch for changes in CNCs array to reload config
    watch(cncs, () => {
      loadCncConfig();
    }, { deep: true });
    
    // Watch for changes in selectedAxes and keep cncConfig in sync
    watch(selectedAxes, (newAxes) => {
      cncConfig.value.selectedAxes = { ...newAxes };
      
    }, { deep: true });

    // Check if config exists - uses centralized validation
    const hasConfig = computed(() => {
      const currentCnc = cncs.value?.find(cnc => cnc.uid === props.axisUid);
      
      if (!currentCnc) return false;
      
      // Convert backend format to frontend format for validation
      const configForValidation = {
        xAxisLength: currentCnc.xAxisLength || currentCnc.x_axis_length || 0,
        yAxisLength: currentCnc.yAxisLength || currentCnc.y_axis_length || 0,
        zAxisLength: currentCnc.zAxisLength || currentCnc.z_axis_length || 0,
        workingZoneX: currentCnc.workingZoneX || currentCnc.working_zone_x || 0,
        workingZoneY: currentCnc.workingZoneY || currentCnc.working_zone_y || 0,
        workingZoneZ: currentCnc.workingZoneZ || currentCnc.working_zone_z || 0,
        selectedAxes: currentCnc.selectedAxes || currentCnc.selected_axes || { x: true, y: true, z: true }
      };
      
      return !requires3DSetup(configForValidation);
    });

    // Handle Setup 3D button click
    const handleSetup3DClick = () => {
      showCncSetup.value = true;
    };

    // Handle 3D CNC button click
    const handle3DCNCClick = () => {
      const currentCnc = cncs.value?.find(cnc => cnc.uid === props.axisUid);
      
      if (!currentCnc) {
        setTypedNotification(CncMessages.NOT_FOUND, NotificationType.ERROR);
        return;
      }
      
      // Convert backend format for validation
      const configForValidation = {
        xAxisLength: currentCnc.xAxisLength || currentCnc.x_axis_length || 0,
        yAxisLength: currentCnc.yAxisLength || currentCnc.y_axis_length || 0,
        zAxisLength: currentCnc.zAxisLength || currentCnc.z_axis_length || 0,
        workingZoneX: currentCnc.workingZoneX || currentCnc.working_zone_x || 0,
        workingZoneY: currentCnc.workingZoneY || currentCnc.working_zone_y || 0,
        workingZoneZ: currentCnc.workingZoneZ || currentCnc.working_zone_z || 0,
        selectedAxes: currentCnc.selectedAxes || currentCnc.selected_axes || { x: true, y: true, z: true }
      };
      
      if (requires3DSetup(configForValidation)) {
        // Show error message and force setup
        const errorMessage = get3DSetupMessage(configForValidation);
        setTypedNotification(errorMessage || CncMessages.CONFIG_INCOMPLETE, NotificationType.WARNING);
        showCncSetup.value = true;
      } else {
        // Config is valid, open 3D viewer
        show3DViewer.value = true;
        setTypedNotification(CncMessages.VIEWER_READY, NotificationType.INFO, 2000);
      }
    };

    onMounted(() => {
      logger.lifecycle('mounted', 'PositionDisplay component mounted', { axisUid: props.axisUid });
      loadCncConfig();
    });

    return {
      pos,
      showCncSetup,
      show3DViewer,
      cncConfig,
      currentValidationErrors,
      lastSavedConfig,
      lastSavedSelectedAxes,
      closeCncSetupModal,
      saveCncConfigAndOpen3D,
      on3DViewerSuccess,
      on3DViewerFailure,
      handleMoveTo,
      handleSimulateMoveTo,
      handleSimulationModeChanged,
      isMoving,
      isCncConnected,
      simulatedPos,
      cncViewer3D,
      hasConfig,
      handleSetup3DClick,
      handle3DCNCClick,
      // Manual axis selection
      selectedAxes,
      selectedAxesCount,
      selectedAxesList,
      hasSelectedLinearAxes,
      isSelectedCartesian,
      // Utilities
      formatCoordinate
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
  min-height: 2rem;
}

.boxed {
  width: 70%;
  background-color: var(--color-bg-tertiary);
  border-radius: var(--border-radius-lg);
  padding: var(--space-2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  font-family: var(--font-family-mono);
  min-height: 2rem;
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

.button-group {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--space-2);
  margin-top: var(--space-2);
}

.button-group-bottom {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  margin-top: var(--space-3);
  padding-top: var(--space-4);
}

.cnc-setup-button,
.cnc-3d-button {
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

.cnc-setup-button:hover,
.cnc-3d-button:hover:not(:disabled) {
  background-color: var(--color-primary-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-base);
}

.cnc-3d-button:disabled {
  background-color: var(--color-background-secondary);
  color: var(--color-text-disabled);
  cursor: not-allowed;
  opacity: 0.6;
}

.gear-style-button {
  background-color: var(--color-bg-tertiary) !important;
  color: var(--color-text-secondary) !important;
  border: var(--border-width-1) solid var(--color-border-secondary) !important;
  border-radius: var(--border-radius-lg) !important;
  padding: 0.25rem 0.5rem !important;
  font-size: 1.2rem !important;
  cursor: pointer !important;
  transition: var(--transition-button) !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: var(--space-1) !important;
  font-weight: var(--font-weight-bold) !important;
  min-height: auto !important;
}

.gear-style-button:hover:not(:disabled) {
  background-color: var(--color-bg-secondary) !important;
  transform: translateY(-1px) !important;
  box-shadow: var(--shadow-button-hover) !important;
}

.gear-style-button:disabled {
  opacity: 0.6 !important;
  cursor: not-allowed !important;
  transform: none !important;
  background-color: var(--color-bg-tertiary) !important;
  color: var(--color-text-disabled) !important;
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
  align-items: flex-start; /* Changed from center to flex-start */
  padding-top: 5vh; /* Add top padding for better positioning */
  padding-bottom: 120px; /* Account for footer height */
  z-index: 1000;
  overflow-y: auto; /* Allow scrolling of the overlay itself */
}

.modal-content {
  background-color: var(--color-bg-primary);
  border-radius: var(--border-radius-card);
  box-shadow: var(--shadow-lg);
  width: 90%;
  max-width: 500px;
  max-height: calc(100vh - 200px); /* Account for footer and top padding */
  display: flex;
  flex-direction: column;
  border: var(--border-width-1) solid var(--color-border-primary);
  margin-bottom: 20px; /* Extra margin from footer */
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
  flex-shrink: 0; /* Prevent header from shrinking */
  position: sticky;
  top: 0;
  z-index: 10;
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
  flex: 1;
  overflow-y: auto;
  min-height: 0; /* Allow flex shrinking */
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
  flex-shrink: 0; /* Prevent footer from shrinking */
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

.save-button:hover:not(:disabled) {
  background-color: var(--color-primary-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-base);
}

.save-button:disabled,
.save-button.disabled {
  background-color: var(--color-background-secondary);
  color: var(--color-text-disabled);
  cursor: not-allowed;
  opacity: 0.6;
  transform: none;
  box-shadow: none;
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
  margin-bottom: var(--space-6); /* Increased spacing */
  padding-top: var(--space-2);
}

.axis-config h5 {
  margin: 0 0 var(--space-3) 0;
  color: var(--color-primary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
}

/* Validation Errors Styles */
.validation-errors {
  margin-bottom: var(--space-4);
  padding: var(--space-3);
  background-color: rgba(220, 53, 69, 0.1);
  border: var(--border-width-1) solid rgba(220, 53, 69, 0.3);
  border-radius: var(--border-radius-base);
  color: #dc3545;
}

.error-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-2);
  font-weight: var(--font-weight-bold);
  font-size: var(--font-size-sm);
}

.error-list {
  margin: 0;
  padding-left: var(--space-4);
  list-style-type: disc;
}

.error-item {
  margin-bottom: var(--space-1);
  font-size: var(--font-size-sm);
  line-height: 1.4;
}

.error-item:last-child {
  margin-bottom: 0;
}

/* Working Zone Configuration Styles */
.working-zone-config {
  margin-bottom: var(--space-6); /* Increased spacing */
  padding-top: var(--space-2);
}

.working-zone-config h5 {
  margin: 0 0 var(--space-3) 0;
  color: var(--color-primary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
}

/* Responsive adjustments for smaller screens */
@media (max-height: 600px) {
  .modal-overlay {
    padding-top: 2vh; /* Less top padding on short screens */
    padding-bottom: 100px; /* Slightly less footer space */
  }
  
  .modal-content {
    max-height: calc(100vh - 150px); /* Less aggressive height reduction */
  }
}

@media (max-width: 768px) {
  .modal-overlay {
    padding-top: 2vh;
    padding-left: var(--space-2);
    padding-right: var(--space-2);
  }
  
  .modal-content {
    width: 95%; /* More width on mobile */
    max-width: none;
  }
  
  .modal-body {
    padding: var(--space-3); /* Less padding on mobile */
  }
  
  .modal-header,
  .modal-footer {
    padding: var(--space-3); /* Consistent padding reduction */
  }
}
</style>

