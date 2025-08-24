<template>
  <div class="viewer-container">
    <div class="viewer-header">
      <h2>CNC Digital Twin</h2>
      <div class="viewer-controls">
        <button @click="resetCamera" class="control-button">
          <font-awesome-icon icon="home" />
          Reset View
        </button>
        <button @click="toggleWorkingZone" class="control-button">
          <font-awesome-icon icon="cog" />
          Working Zone
        </button>
        <button @click="toggleBoundingBox" class="control-button debug-button" :class="{ 'debug-active': showBoundingBox }">
          <font-awesome-icon icon="square" />
          Debug Box
        </button>
        <button v-if="cameraViews.length > 1" @click="switchCameraView" class="control-button">
          <font-awesome-icon icon="eye" />
          {{ currentCameraView }}
        </button>
        <button @click="toggleSimulationMode" class="control-button simulation-button" :class="{ 'simulation-active': isSimulationMode }" :disabled="isCncMoving">
          <font-awesome-icon icon="cog" />
          Simulation
        </button>
        <button 
          @click="executeSimulation" 
          class="control-button play-button" 
          :disabled="!canExecuteSimulation"
          :class="{ 'play-active': isSimulationMode && targetPosition }"
        >
          <font-awesome-icon icon="play" />
          Play
        </button>
        <button @click="closeViewer" class="close-button">
          <font-awesome-icon icon="home" />
          Close
        </button>
      </div>
    </div>
    
    <div class="viewer-content">
      <!-- WebGL Error Fallback -->
      <div v-if="webglError" class="webgl-error-container">
        <div class="error-content">
          <div class="error-icon">
            <font-awesome-icon icon="exclamation-triangle" />
          </div>
          <h3 class="error-title">3D Viewer Unavailable</h3>
          <p class="error-message">{{ errorMessage }}</p>
          
          <div class="error-actions">
            <button v-if="webglError === 'context-lost'" @click="retryInitialization" class="retry-button">
              <font-awesome-icon icon="redo" />
              Retry
            </button>
            <div class="troubleshooting">
              <h4>Troubleshooting:</h4>
              <ul>
                <li>Ensure your browser supports WebGL</li>
                <li>Enable hardware acceleration in browser settings</li>
                <li>Update your graphics drivers</li>
                <li>Try a different browser (Chrome, Firefox, Edge)</li>
                <li>Restart your browser</li>
              </ul>
            </div>
          </div>
          
          <!-- Basic position info as fallback -->
          <div class="fallback-info">
            <h4>Current Position (Text Mode)</h4>
            <div class="fallback-position">
              <div class="fallback-row">
                <span class="axis">X:</span>
                <span class="value">{{ formatCoordinate(displayPosition.x) }}mm</span>
              </div>
              <div class="fallback-row">
                <span class="axis">Y:</span>
                <span class="value">{{ formatCoordinate(displayPosition.y) }}mm</span>
              </div>
              <div class="fallback-row">
                <span class="axis">Z:</span>
                <span class="value">{{ formatCoordinate(displayPosition.z) }}mm</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Normal 3D Container -->
      <div v-else class="three-container" ref="threeContainer" :class="{ 'debug-border': showBoundingBox }">
        <!-- Debug overlay to show margins -->
        <div v-if="showBoundingBox" class="debug-overlay">
          <div class="margin-visualization">
            <div class="margin-info">0.5cm margins</div>
          </div>
        </div>
        
        <!-- Loading indicator -->
        <div v-if="!isInitialized" class="loading-container">
          <div class="loading-content">
            <div class="loading-spinner"></div>
            <p>Initializing 3D Viewer...</p>
          </div>
        </div>
        
        <!-- Mouse position tooltip -->
        <div v-if="mouseTooltip.visible" class="mouse-tooltip" :style="mouseTooltipStyle">
          <div class="tooltip-content">
            <span class="coord-x">X: {{ formatCoordinate(mouseTooltip.position.x) }}</span>
            <span class="coord-y">Y: {{ formatCoordinate(mouseTooltip.position.y) }}</span>
            <span class="coord-z">Z: {{ formatCoordinate(mouseTooltip.position.z) }}</span>
          </div>
        </div>
        
        <!-- Fixed axis legend in top-left corner -->
        <div v-if="isInitialized" class="axis-legend">
          <div class="legend-title">Axes</div>
          <div v-if="cncConfig?.selectedAxes?.x === true" class="legend-item">
            <div class="legend-color x-color"></div>
            <span class="legend-label">X-Axis</span>
          </div>
          <div v-if="cncConfig?.selectedAxes?.y === true" class="legend-item">
            <div class="legend-color y-color"></div>
            <span class="legend-label">Y-Axis</span>
          </div>
          <div v-if="cncConfig?.selectedAxes?.z === true" class="legend-item">
            <div class="legend-color z-color"></div>
            <span class="legend-label">Z-Axis</span>
          </div>
          <div class="legend-divider"></div>
          <div class="legend-item click-status">
            <div class="legend-color" :class="clickStatusClass"></div>
            <span class="legend-label">{{ clickStatusText }}</span>
          </div>
        </div>
      </div>
      
      <div class="info-panel">
        <div class="position-info">
          <h4>Current Position</h4>
          <div v-if="cncConfig.selectedAxes?.x === true" class="position-row">
            <span class="axis">X:</span>
            <span class="value">{{ formatCoordinate(displayPosition.x) }}mm</span>
          </div>
          <div v-if="cncConfig.selectedAxes?.y === true" class="position-row">
            <span class="axis">Y:</span>
            <span class="value">{{ formatCoordinate(displayPosition.y) }}mm</span>
          </div>
          <div v-if="cncConfig.selectedAxes?.z === true" class="position-row">
            <span class="axis">Z:</span>
            <span class="value">{{ formatCoordinate(displayPosition.z) }}mm</span>
          </div>
        </div>
        
        <div class="target-info">
          <h4>Target Position</h4>
          <div v-if="targetArrived && lastTargetPosition">
            <div v-if="cncConfig.selectedAxes?.x === true" class="position-row">
              <span class="axis">X:</span>
              <span class="value target arrived">{{ formatCoordinate(lastTargetPosition.x || 0) }}mm</span>
            </div>
            <div v-if="cncConfig.selectedAxes?.y === true" class="position-row">
              <span class="axis">Y:</span>
              <span class="value target arrived">{{ formatCoordinate(lastTargetPosition.y || 0) }}mm</span>
            </div>
            <div v-if="cncConfig.selectedAxes?.z === true" class="position-row">
              <span class="axis">Z:</span>
              <span class="value target arrived">{{ formatCoordinate(lastTargetPosition.z || 0) }}mm</span>
            </div>
          </div>
          <div v-else-if="targetPosition">
            <div v-if="cncConfig.selectedAxes?.x === true" class="position-row">
              <span class="axis">X:</span>
              <span class="value target">{{ formatCoordinate(targetPosition.x || 0) }}mm</span>
            </div>
            <div v-if="cncConfig.selectedAxes?.y === true" class="position-row">
              <span class="axis">Y:</span>
              <span class="value target">{{ formatCoordinate(targetPosition.y || 0) }}mm</span>
            </div>
            <div v-if="cncConfig.selectedAxes?.z === true" class="position-row">
              <span class="axis">Z:</span>
              <span class="value target">{{ formatCoordinate(targetPosition.z || 0) }}mm</span>
            </div>
          </div>
          <div v-else>
            <div v-if="cncConfig.selectedAxes?.x === true" class="position-row">
              <span class="axis">X:</span>
              <span class="value">--</span>
            </div>
            <div v-if="cncConfig.selectedAxes?.y === true" class="position-row">
              <span class="axis">Y:</span>
              <span class="value">--</span>
            </div>
            <div v-if="cncConfig.selectedAxes?.z === true" class="position-row">
              <span class="axis">Z:</span>
              <span class="value">--</span>
            </div>
          </div>
        </div>
        
        <div class="config-info">
          <h4>Configuration</h4>
          <div class="config-row">
            <span class="label">Selected Axes:</span>
            <span class="value">{{ selectedAxesDisplay }}</span>
          </div>
          <div v-if="selectedLinearAxes.length > 0" class="config-row">
            <span class="label">Axis Lengths:</span>
            <span class="value">{{ axisLengthsDisplay }}</span>
          </div>
          <div v-if="selectedLinearAxes.length > 0" class="config-row">
            <span class="label">Work Zone:</span>
            <span class="value">{{ workZoneDisplay }}</span>
          </div>
        </div>
        
        <div class="grid-settings">
          <h4>Grid Settings</h4>
          <div class="grid-spacing-control">
            <label for="grid-spacing">Grid Spacing:</label>
            <input 
              id="grid-spacing"
              type="number" 
              v-model.number="gridSpacing" 
              min="5" 
              max="100" 
              step="5"
              @change="regenerateGrids"
              class="grid-spacing-input"
            />
            <span class="unit">mm</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, watch, computed, nextTick } from 'vue';
import * as THREE from 'three';
import { logger } from '@/utils/logger';
import { useCncStore } from '@/composables/useStore';
import { formatPrecision, formatCoordinate, formatPosition, getWorkingZoneBounds, isWithinWorkingZone, setTargetForRealMovement } from '@/utils/validation';

export default {
  name: 'CncViewer3D',
  props: {
    cncConfig: {
      type: Object,
      required: true
    },
    axisUid: {
      type: String,
      required: true
    },
    currentPos: {
      type: Object,
      default: () => ({ x: 0, y: 0, z: 0 })
    },
    isCncConnected: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close', 'moveTo', 'simulateMoveTo', 'positionUpdate', 'targetUpdate', 'simulationModeChanged'],
  setup(props, { emit }) {
    // DOM reference - needs to be reactive for template ref
    const threeContainer = ref(null);
    
    // Access CNC state from store
    const { cncState } = useCncStore(props.axisUid);
    
    // Constants
    const DEFAULT_FEEDRATE = 1500; // mm/min
    
    // Three.js objects
    let scene = null;
    let camera = null;
    let renderer = null;
    let controls = null;
    let animationId = null;
    
    // CNC components
    let cncGroup = null;
    let toolHead = null;
    let ghostToolHead = null; // Ghost indicator for click target
    let trajectoryLine = null; // Line showing path from current to target
    let workingZoneMesh = null;
    let xAxisMesh = null;
    let yAxisMesh = null;
    let zAxisMesh = null;
    let xArrowMesh = null;
    let yArrowMesh = null;
    let zArrowMesh = null;
    let gridHelper = null;
    let fineGridHelper = null;
    let xAxisLabel = null;
    let yAxisLabel = null;
    let zAxisLabel = null;
    let sceneBoundingBox = null; // Invisible bounding box containing entire scene
    let cachedBoundingBox = null; // Cached bounding box to avoid redundant calculations
    let lastBoundingBoxViewType = null; // Track which view the cached box is for
    
    // State
    const isAnimating = ref(true);
    const showWorkingZone = ref(true); // Start visible by default
    // Internal grid state - doesn't need reactivity (not bound to template)
    let showGrid = true; // Grid visible in fixed views
    const isSimulationMode = ref(false); // Simulation mode for testing without real CNC
    const showBoundingBox = ref(false); // Debug: Show scene bounding box
    const gridSpacing = ref(10); // Grid spacing in mm (default 10mm)
    
    // Mouse tooltip state
    const mouseTooltip = ref({
      visible: false,
      position: { x: 0, y: 0, z: 0 },
      screenX: 0,
      screenY: 0
    });
    
    let boundingBoxMesh = null; // Debug mesh for bounding box visualization
    
    // Error handling state
    const webglError = ref(null);
    const hasWebglSupport = ref(true);
    const isInitialized = ref(false);
    const errorMessage = ref('');
    
    // Optimization: Dirty flags for performance
    const dirtyFlags = {
      trajectoryLine: false,
      rendering: true // Start with true to render initial frame
    };
    
    // Optimization: Cached values to avoid recalculation
    const cachedValues = {
      lastToolPosition: { x: 0, y: 0, z: 0 },
      lastDisplayPosition: { x: 0, y: 0, z: 0 },
      lastTargetPosition: null,
      movementDistance: 0,
      movementProgress: 0
    };
    
    // Frame rate limiting for idle periods
    let lastFrameTime = 0;
    const TARGET_FPS = 60;
    const FRAME_INTERVAL = 1000 / TARGET_FPS;
    const IDLE_FPS = 30; // Reduced FPS when nothing is moving
    const IDLE_FRAME_INTERVAL = 1000 / IDLE_FPS;
    
    // Resource tracking for proper disposal
    const disposableResources = {
      geometries: [],
      materials: [],
      textures: [],
      meshes: [],
      lights: []
    };
    
    // CNC movement simulation state
    const targetPosition = ref(null); // Target position for CNC movement
    const movementStartTime = ref(null); // Track when movement started
    const movementDuration = ref(2000); // Duration for movement in ms (based on feedrate)
    
    // Real-time position display (updated from tool head position)
    const displayPosition = ref({ x: 0, y: 0, z: 0 });
    
    // Target arrival status
    const targetArrived = ref(false);
    const lastTargetPosition = ref(null);
    
    // Play control for simulation
    const isExecutingSimulation = ref(false);
    
    // Camera views - now dynamic based on axis count
    const cameraViews = computed(() => {
      const axisCount = selectedLinearAxes.value.length;
      
      if (axisCount === 2) {
        return ['Top']; // Only top view for 2-axis systems
      }
      return ['3D', 'Top', 'Side']; // All views for 3-axis systems
    });
    const currentCameraIndex = ref(0);
    const currentCameraView = computed(() => cameraViews.value[currentCameraIndex.value]);
    
    // Click state tracking for 3-axis systems
    const topViewClicked = ref(false);
    const sideViewClicked = ref(false);
    const topViewPosition = ref(null);
    const sideViewPosition = ref(null);
    
    // Click-to-move status indicators
    const canClickToMove = computed(() => {
      const isFixedView = currentCameraView.value === 'Top' || currentCameraView.value === 'Side';
      return isFixedView && (props.isCncConnected || isSimulationMode.value);
    });
    
    const clickStatusClass = computed(() => {
      return canClickToMove.value ? 'status-enabled' : 'status-disabled';
    });
    
    const clickStatusText = computed(() => {
      if (currentCameraView.value === '3D') {
        return 'Presentation View';
      }
      
      const axisCount = selectedLinearAxes.value.length;
      
      if (isSimulationMode.value) {
        if (currentCameraView.value === 'Top' || currentCameraView.value === 'Side') {
          if (axisCount === 2) {
            return targetPosition.value ? 'Click Play to Execute' : 'Click to Set Target';
          } else if (axisCount === 3) {
            return targetPosition.value ? 'Click Play to Execute' : 'Click Both Views to Set Target';
          }
        }
        return 'Fixed View Only';
      }
      
      if (!props.isCncConnected) {
        return 'CNC Disconnected';
      }
      
      if (currentCameraView.value === 'Top' || currentCameraView.value === 'Side') {
        if (axisCount === 2) {
          return 'Click to Move';
        } else if (axisCount === 3) {
          if (!topViewClicked.value && !sideViewClicked.value) {
            return 'Click Both Top & Side Views';
          } else if (topViewClicked.value && !sideViewClicked.value) {
            return 'Now Click Side View';
          } else if (!topViewClicked.value && sideViewClicked.value) {
            return 'Now Click Top View';
          } else {
            return 'Ready to Move';
          }
        }
      }
      return 'Fixed View Only';
    });
    
    // Play button state
    const canExecuteSimulation = computed(() => {
      return isSimulationMode.value && targetPosition.value && !isExecutingSimulation.value;
    });
    
    // Check if CNC is currently moving (disable simulation button during real movements)
    const isCncMoving = computed(() => {
      const state = cncState.value;
      return state && state.toUpperCase() === 'JOG';
    });

    // Computed properties for display strings based on selected axes
    const selectedLinearAxes = computed(() => {
      const axes = [];
      if (props.cncConfig.selectedAxes?.x === true) axes.push('X');
      if (props.cncConfig.selectedAxes?.y === true) axes.push('Y');  
      if (props.cncConfig.selectedAxes?.z === true) axes.push('Z');
      
      return axes;
    });

    const selectedAxesDisplay = computed(() => {
      return selectedLinearAxes.value.length > 0 ? selectedLinearAxes.value.join(', ') : 'None';
    });
    
    const mouseTooltipStyle = computed(() => {
      return {
        left: `${mouseTooltip.value.screenX + 15}px`,
        top: `${mouseTooltip.value.screenY - 40}px`
      };
    });

    const axisLengthsDisplay = computed(() => {
      const lengths = [];
      if (props.cncConfig.selectedAxes?.x === true && props.cncConfig.xAxisLength) {
        lengths.push(`X:${props.cncConfig.xAxisLength}mm`);
      }
      if (props.cncConfig.selectedAxes?.y === true && props.cncConfig.yAxisLength) {
        lengths.push(`Y:${props.cncConfig.yAxisLength}mm`);
      }
      if (props.cncConfig.selectedAxes?.z === true && props.cncConfig.zAxisLength) {
        lengths.push(`Z:${props.cncConfig.zAxisLength}mm`);
      }
      return lengths.join(' × ');
    });


    const workZoneDisplay = computed(() => {
      const zones = [];
      if (props.cncConfig.selectedAxes?.x === true && props.cncConfig.workingZoneX) {
        zones.push(`X:${props.cncConfig.workingZoneX}mm`);
      }
      if (props.cncConfig.selectedAxes?.y === true && props.cncConfig.workingZoneY) {
        zones.push(`Y:${props.cncConfig.workingZoneY}mm`);
      }
      if (props.cncConfig.selectedAxes?.z === true && props.cncConfig.workingZoneZ) {
        zones.push(`Z:${props.cncConfig.workingZoneZ}mm`);
      }
      return zones.join(' × ');
    });
    
    // Click-to-move state
    let raycaster = null;
    let mouse = new THREE.Vector2();
    let clickTarget = null; // Visual indicator for click target
    
    // WebGL Support Detection
    const checkWebGLSupport = () => {
      try {
        const canvas = document.createElement('canvas');
        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
        
        if (!gl) {
          hasWebglSupport.value = false;
          webglError.value = 'webgl-not-supported';
          errorMessage.value = 'WebGL is not supported on this device. Please try a different browser or enable hardware acceleration.';
          logger.error('WebGL not supported');
          return false;
        }
        
        // Check for required WebGL extensions
        const requiredExtensions = ['OES_element_index_uint'];
        const missingExtensions = [];
        
        requiredExtensions.forEach(ext => {
          if (!gl.getExtension(ext)) {
            missingExtensions.push(ext);
          }
        });
        
        if (missingExtensions.length > 0) {
          logger.warn('Missing WebGL extensions:', missingExtensions);
        }
        
        // Check WebGL capabilities
        const maxTextureSize = gl.getParameter(gl.MAX_TEXTURE_SIZE);
        const maxRenderbufferSize = gl.getParameter(gl.MAX_RENDERBUFFER_SIZE);
        const maxVertexAttribs = gl.getParameter(gl.MAX_VERTEX_ATTRIBS);
        
        logger.info('WebGL capabilities:', {
          maxTextureSize,
          maxRenderbufferSize,
          maxVertexAttribs,
          vendor: gl.getParameter(gl.VENDOR),
          renderer: gl.getParameter(gl.RENDERER),
          version: gl.getParameter(gl.VERSION)
        });
        
        // Clean up test canvas
        canvas.width = 1;
        canvas.height = 1;
        gl.clear(gl.COLOR_BUFFER_BIT);
        
        return true;
      } catch (error) {
        hasWebglSupport.value = false;
        webglError.value = 'webgl-test-failed';
        errorMessage.value = 'WebGL test failed. This might be due to hardware limitations or driver issues.';
        logger.error('WebGL support test failed:', error);
        return false;
      }
    };
    
    // WebGL Context Lost/Restored Handlers
    const handleWebGLContextLost = (event) => {
      logger.warn('WebGL context lost');
      event.preventDefault();
      
      webglError.value = 'context-lost';
      errorMessage.value = 'WebGL context was lost. The 3D viewer will attempt to restore automatically.';
      
      // Stop animation to prevent errors
      stopAnimationLoop();
      
      // Clear dirty flags
      Object.keys(dirtyFlags).forEach(flag => {
        dirtyFlags[flag] = false;
      });
    };
    
    const handleWebGLContextRestored = (event) => {
      logger.info('WebGL context restored, reinitializing...');
      
      try {
        // Clear error state
        webglError.value = null;
        errorMessage.value = '';
        
        // Dispose existing resources
        disposeTrackedResources();
        
        // Reinitialize the 3D scene
        setTimeout(() => {
          try {
            initThreeJS();
            logger.info('3D scene successfully restored after context loss');
          } catch (error) {
            logger.error('Failed to restore 3D scene after context restoration:', error);
            webglError.value = 'restoration-failed';
            errorMessage.value = 'Failed to restore the 3D viewer after context loss. Please refresh the page.';
          }
        }, 100);
      } catch (error) {
        logger.error('Error during WebGL context restoration:', error);
        webglError.value = 'restoration-error';
        errorMessage.value = 'An error occurred while restoring the WebGL context. Please refresh the page.';
      }
    };
    
    // Resource Management Functions
    const trackResource = (resource, type) => {
      try {
        if (resource && disposableResources[type]) {
          disposableResources[type].push(resource);
        }
        return resource;
      } catch (error) {
        logger.error(`Error tracking resource of type ${type}:`, error);
        return resource;
      }
    };
    
    const createTrackedGeometry = (GeometryClass, ...args) => {
      try {
        const geometry = new GeometryClass(...args);
        
        if (!geometry) {
          throw new Error(`Failed to create geometry of type ${GeometryClass.name}`);
        }
        
        return trackResource(geometry, 'geometries');
      } catch (error) {
        logger.error(`Error creating geometry of type ${GeometryClass.name}:`, error);
        
        // Return a fallback box geometry to prevent crashes
        try {
          const fallbackGeometry = new THREE.BoxGeometry(1, 1, 1);
          return trackResource(fallbackGeometry, 'geometries');
        } catch (fallbackError) {
          logger.error('Failed to create fallback geometry:', fallbackError);
          throw error;
        }
      }
    };
    
    const createTrackedMaterial = (MaterialClass, options) => {
      try {
        const material = new MaterialClass(options);
        
        if (!material) {
          throw new Error(`Failed to create material of type ${MaterialClass.name}`);
        }
        
        return trackResource(material, 'materials');
      } catch (error) {
        logger.error(`Error creating material of type ${MaterialClass.name}:`, error);
        
        // Return a fallback basic material to prevent crashes
        try {
          const fallbackMaterial = new THREE.MeshBasicMaterial({ color: 0x888888 });
          return trackResource(fallbackMaterial, 'materials');
        } catch (fallbackError) {
          logger.error('Failed to create fallback material:', fallbackError);
          throw error;
        }
      }
    };
    
    const createTrackedTexture = (texture) => {
      return trackResource(texture, 'textures');
    };
    
    const createTrackedMesh = (geometry, material) => {
      try {
        if (!geometry) {
          throw new Error('Geometry is required to create mesh');
        }
        
        if (!material) {
          throw new Error('Material is required to create mesh');
        }
        
        const mesh = new THREE.Mesh(geometry, material);
        
        if (!mesh) {
          throw new Error('Failed to create Three.js Mesh');
        }
        
        return trackResource(mesh, 'meshes');
      } catch (error) {
        logger.error('Error creating mesh:', error);
        throw error;
      }
    };
    
    const createTrackedLight = (LightClass, ...args) => {
      try {
        const light = new LightClass(...args);
        
        if (!light) {
          throw new Error(`Failed to create light of type ${LightClass.name}`);
        }
        
        return trackResource(light, 'lights');
      } catch (error) {
        logger.error(`Error creating light of type ${LightClass.name}:`, error);
        
        // Return a fallback ambient light to prevent crashes
        try {
          const fallbackLight = new THREE.AmbientLight(0x404040, 0.5);
          return trackResource(fallbackLight, 'lights');
        } catch (fallbackError) {
          logger.error('Failed to create fallback light:', fallbackError);
          throw error;
        }
      }
    };
    
    // Optimization: Dirty flag management
    const markDirty = (flag) => {
      dirtyFlags[flag] = true;
      dirtyFlags.rendering = true; // Always mark rendering dirty when any other flag is dirty
    };
    
    const clearDirty = (flag) => {
      dirtyFlags[flag] = false;
    };
    
    const isDirty = (flag) => {
      return dirtyFlags[flag];
    };
    
    // Optimization: Position comparison with tolerance
    const hasPositionChanged = (pos1, pos2, tolerance = 0.001) => {
      return Math.abs(pos1.x - pos2.x) > tolerance ||
             Math.abs(pos1.y - pos2.y) > tolerance ||
             Math.abs(pos1.z - pos2.z) > tolerance;
    };
    
    // Optimization: Cached distance calculation
    const calculateDistance = (pos1, pos2) => {
      const dx = pos2.x - pos1.x;
      const dy = pos2.y - pos1.y;
      const dz = pos2.z - pos1.z;
      return Math.sqrt(dx * dx + dy * dy + dz * dz);
    };
    
    // Optimization: Update cached values and check for changes
    const updateCachedPosition = (newPos, cacheKey) => {
      const cached = cachedValues[cacheKey];
      const changed = hasPositionChanged(newPos, cached);
      if (changed) {
        cached.x = newPos.x;
        cached.y = newPos.y;
        cached.z = newPos.z;
      }
      return changed;
    };

    // Resource Disposal Functions
    const disposeMaterialMaps = (material) => {
      if (material.map) material.map.dispose();
      if (material.normalMap) material.normalMap.dispose();
      if (material.bumpMap) material.bumpMap.dispose();
      if (material.envMap) material.envMap.dispose();
    };
    
    const disposeMaterial = (material) => {
      if (Array.isArray(material)) {
        material.forEach(mat => {
          disposeMaterialMaps(mat);
          mat.dispose();
        });
      } else {
        disposeMaterialMaps(material);
        material.dispose();
      }
    };
    
    const disposeObject = (object) => {
      if (!object) return;
      
      // Remove from parent if it has one
      if (object.parent) {
        object.parent.remove(object);
      }
      
      // Dispose geometry
      if (object.geometry) {
        object.geometry.dispose();
      }
      
      // Dispose material(s)
      if (object.material) {
        disposeMaterial(object.material);
      }
      
      // Dispose children recursively
      if (object.children) {
        [...object.children].forEach(child => disposeObject(child));
      }
    };
    
    const disposeTrackedResources = () => {
      disposableResources.geometries.forEach(geometry => {
        if (geometry && typeof geometry.dispose === 'function') {
          geometry.dispose();
        }
      });
      
      disposableResources.materials.forEach(material => {
        if (material && typeof material.dispose === 'function') {
          material.dispose();
        }
      });
      
      disposableResources.textures.forEach(texture => {
        if (texture && typeof texture.dispose === 'function') {
          texture.dispose();
        }
      });
      
      disposableResources.meshes.forEach(mesh => disposeObject(mesh));
      
      disposableResources.lights.forEach(light => {
        if (light.parent) {
          light.parent.remove(light);
        }
        if (light.dispose) {
          light.dispose();
        }
      });
      
      // Clear arrays
      Object.keys(disposableResources).forEach(key => {
        disposableResources[key].length = 0;
      });
    };
    
    const disposeThreeJSObjects = () => {
      // Dispose scene
      if (scene) {
        disposeObject(scene);
        scene = null;
      }
      
      // Dispose renderer
      if (renderer) {
        renderer.dispose();
        if (renderer.domElement && renderer.domElement.parentNode) {
          renderer.domElement.parentNode.removeChild(renderer.domElement);
        }
        renderer = null;
      }
    };
    
    const clearObjectReferences = () => {
      camera = null;
      controls = null;
      cncGroup = null;
      toolHead = null;
      ghostToolHead = null;
      trajectoryLine = null;
      workingZoneMesh = null;
      xAxisMesh = null;
      yAxisMesh = null;
      zAxisMesh = null;
      gridHelper = null;
      fineGridHelper = null;
      xAxisLabel = null;
      yAxisLabel = null;
      zAxisLabel = null;
      boundingBoxMesh = null;
      raycaster = null;
      clickTarget = null;
      mouse = null;
    };
    
    const disposeAllResources = () => {
      disposeTrackedResources();
      disposeThreeJSObjects();
      clearObjectReferences();
    };
    
    // Safe error handling wrapper for all operations
    const safeExecute = (operation, errorContext) => {
      try {
        return operation();
      } catch (error) {
        logger.error(`Error in ${errorContext}:`, error);
        webglError.value = 'operation-failed';
        errorMessage.value = `Failed to ${errorContext}. Please try refreshing the page.`;
        throw error;
      }
    };
    
    // Scene initialization functions with error handling
    const initScene = () => {
      return safeExecute(() => {
        scene = new THREE.Scene();
        
        if (!scene) {
          throw new Error('Failed to create Three.js Scene');
        }
        
        // Create gradient background for better depth perception
        const canvas = document.createElement('canvas');
        if (!canvas) {
          throw new Error('Failed to create canvas element');
        }
        
        canvas.width = 128;
        canvas.height = 128;
        const context = canvas.getContext('2d');
        
        if (!context) {
          logger.warn('Failed to get 2D context for background, using solid color');
          scene.background = new THREE.Color(0x2a3448);
          return;
        }
        
        // Create vertical gradient from dark blue-gray to lighter gray
        const gradient = context.createLinearGradient(0, 0, 0, 128);
        gradient.addColorStop(0, '#2a3448'); // Dark blue-gray at top
        gradient.addColorStop(0.5, '#1e2433'); // Mid tone
        gradient.addColorStop(1, '#151925'); // Darker at bottom
        
        context.fillStyle = gradient;
        context.fillRect(0, 0, 128, 128);
        
        try {
          const backgroundTexture = createTrackedTexture(new THREE.CanvasTexture(canvas));
          scene.background = backgroundTexture;
        } catch (textureError) {
          logger.warn('Failed to create background texture, using solid color:', textureError);
          scene.background = new THREE.Color(0x2a3448);
        }
      }, 'initialize scene');
    };
    
    const initCamera = () => {
      return safeExecute(() => {
        if (!threeContainer.value) {
          throw new Error('Three.js container not available');
        }
        
        const width = threeContainer.value.clientWidth || 800;
        const height = threeContainer.value.clientHeight || 600;
        const aspect = width / height;
        
        if (aspect <= 0 || !isFinite(aspect)) {
          throw new Error('Invalid aspect ratio calculated');
        }
        
        camera = new THREE.PerspectiveCamera(60, aspect, 1, 50000);
        
        if (!camera) {
          throw new Error('Failed to create Three.js Camera');
        }
        
        // Note: setCameraPosition will be called after createCNCRig() in initThreeJS
      }, 'initialize camera');
    };
    
    const initRenderer = () => {
      return safeExecute(() => {
        if (!threeContainer.value) {
          throw new Error('Three.js container not available');
        }
        
        const width = threeContainer.value.clientWidth || 800;
        const height = threeContainer.value.clientHeight || 600;
        
        // Create renderer with error handling
        try {
          renderer = new THREE.WebGLRenderer({
            antialias: true,
            alpha: false,
            preserveDrawingBuffer: false,
            powerPreference: 'high-performance'
          });
        } catch (rendererError) {
          logger.warn('Failed to create WebGL renderer with preferred settings, trying basic settings:', rendererError);
          try {
            renderer = new THREE.WebGLRenderer();
          } catch (basicRendererError) {
            throw new Error('Failed to create WebGL renderer: ' + basicRendererError.message);
          }
        }
        
        if (!renderer) {
          throw new Error('WebGL renderer creation returned null');
        }
        
        // Validate renderer context
        const gl = renderer.getContext();
        if (!gl) {
          throw new Error('Failed to get WebGL context from renderer');
        }
        
        // Set up context lost/restored handlers
        renderer.domElement.addEventListener('webglcontextlost', handleWebGLContextLost, false);
        renderer.domElement.addEventListener('webglcontextrestored', handleWebGLContextRestored, false);
        
        // Configure renderer settings
        renderer.setSize(width, height);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2)); // Limit pixel ratio for performance
        
        // Enable shadow mapping if supported
        try {
          renderer.shadowMap.enabled = true;
          renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        } catch (shadowError) {
          logger.warn('Shadow mapping not supported:', shadowError);
        }
        
        // Append to container
        threeContainer.value.appendChild(renderer.domElement);
        
        logger.info('WebGL renderer initialized successfully');
      }, 'initialize renderer');
    };
    
    const initRaycaster = () => {
      return safeExecute(() => {
        raycaster = new THREE.Raycaster();
        
        if (!raycaster) {
          throw new Error('Failed to create Three.js Raycaster');
        }
        
        // Configure raycaster for better accuracy (reduced threshold)
        raycaster.params.Line.threshold = 0.01;
        raycaster.params.Points.threshold = 0.01;
      }, 'initialize raycaster');
    };
    
    // Main Three.js initialization function with comprehensive error handling
    const initThreeJS = () => {
      try {
        if (!threeContainer.value) {
          throw new Error('Three.js container element not found');
        }
        
        // Check WebGL support first
        if (!checkWebGLSupport()) {
          return; // Error already set by checkWebGLSupport
        }
        
        logger.info('Initializing Three.js CNC viewer...');
        
        // Initialize core Three.js components
        initScene();
        initCamera();
        initRenderer();
        initRaycaster();
        
        // Set up scene content
        setupLighting();
        createCNCRig();
        setupControls();
        
        // Apply initial 3D rotation since default view is 3D
        if (currentCameraView.value === '3D' && cncGroup) {
          const centerX = props.cncConfig.xAxisLength / 2;
          const centerY = props.cncConfig.yAxisLength / 2;
          const centerZ = props.cncConfig.zAxisLength / 2;
          
          const rotationMatrix = new THREE.Matrix4();
          const translationToOrigin = new THREE.Matrix4().makeTranslation(-centerX, -centerY, -centerZ);
          const translationBack = new THREE.Matrix4().makeTranslation(centerX, centerY, centerZ);
          const rotationZ = new THREE.Matrix4().makeRotationZ(Math.PI); // +180 degrees
          
          rotationMatrix.multiplyMatrices(translationBack, rotationZ);
          rotationMatrix.multiply(translationToOrigin);
          cncGroup.applyMatrix4(rotationMatrix);
        }
        
        // Set camera position after rotation is applied
        setCameraPosition(currentCameraView.value);
        
        // Start animation loop
        animate();
        
        isInitialized.value = true;
        logger.info('Three.js CNC viewer initialized successfully');
        
      } catch (error) {
        logger.error('Failed to initialize Three.js CNC viewer:', error);
        
        // Set error state
        webglError.value = 'initialization-failed';
        errorMessage.value = `Failed to initialize 3D viewer: ${error.message}`;
        
        // Clean up any partially created resources
        try {
          cleanupViewer();
        } catch (cleanupError) {
          logger.error('Error during cleanup after initialization failure:', cleanupError);
        }
      }
    };
    
    // Retry initialization function
    const retryInitialization = () => {
      logger.info('Retrying 3D viewer initialization...');
      
      // Reset error state
      webglError.value = null;
      errorMessage.value = '';
      isInitialized.value = false;
      
      // Clean up any existing resources
      try {
        cleanupViewer();
      } catch (cleanupError) {
        logger.warn('Error during cleanup before retry:', cleanupError);
      }
      
      // Wait a bit then retry
      setTimeout(() => {
        initThreeJS();
      }, 500);
    };
    
    const setupLighting = () => {
      return safeExecute(() => {
        if (!scene) {
          throw new Error('Scene not available for lighting setup');
        }
        
        // Increased ambient light for better visibility
        const ambientLight = createTrackedLight(THREE.AmbientLight, 0x606070, 0.9); // Slightly blue-tinted for contrast
        scene.add(ambientLight);
        
        // Main directional light
        const directionalLight = createTrackedLight(THREE.DirectionalLight, 0xffffff, 0.7);
        directionalLight.position.set(
          props.cncConfig.xAxisLength,
          props.cncConfig.yAxisLength,
          props.cncConfig.zAxisLength * 2
        );
        scene.add(directionalLight);
        
        // Fill light with warmer tone
        const fillLight = createTrackedLight(THREE.DirectionalLight, 0x8899ff, 0.5);
        fillLight.position.set(-props.cncConfig.xAxisLength, props.cncConfig.yAxisLength, props.cncConfig.zAxisLength);
        scene.add(fillLight);
        
        // Add a subtle point light at origin for axis emphasis
        const pointLight = createTrackedLight(THREE.PointLight, 0xffffff, 0.3, props.cncConfig.xAxisLength * 2);
        pointLight.position.set(0, 0, 0);
        scene.add(pointLight);
        
        logger.info('Lighting setup completed successfully');
      }, 'setup lighting');
    };
    
    const createCNCRig = () => {
      return safeExecute(() => {
        if (!scene) {
          throw new Error('Scene not available for CNC rig creation');
        }
        
        cncGroup = new THREE.Group();
        
        if (!cncGroup) {
          throw new Error('Failed to create CNC group');
        }
        
        // Validate CNC configuration
        if (!props.cncConfig) {
          throw new Error('Invalid CNC configuration');
        }
        
        // Create standard cartesian machine visualization
        try {
          createCartesianMachine();
        } catch (machineError) {
          logger.error('Error creating CNC machine:', machineError);
          // Create a basic fallback visualization
          createSimpleAxisVisualization();
        }
        
        // Scene bounding box is now calculated on-demand with caching
        
        // Create bounding box visualization (initially hidden) - only if debug mode is on
        if (showBoundingBox.value) {
          createBoundingBoxVisualization();
        }
        
        // Working zone visualization - always create but control visibility
        try {
          createWorkingZone();
        } catch (workingZoneError) {
          logger.warn('Failed to create working zone visualization:', workingZoneError);
        }
        
        scene.add(cncGroup);
        
        logger.info('CNC rig 3D model created successfully');
      }, 'create CNC rig');
    };
    
    const createCoreXYMachine = () => {
      createSimpleAxisVisualization();
    };
    
    const createDeltaMachine = () => {
      createSimpleAxisVisualization();
    };
    
    const createCartesianMachine = () => {
      createSimpleAxisVisualization();
    };
    
    // CNC Visualization Creation Functions
    const createAxisMaterials = () => {
      return {
        xAxis: createTrackedMaterial(THREE.MeshBasicMaterial, { color: 0xff3333 }),
        yAxis: createTrackedMaterial(THREE.MeshBasicMaterial, { color: 0x33ff33 }),
        zAxis: createTrackedMaterial(THREE.MeshBasicMaterial, { color: 0x0000ff }),
        tool: createTrackedMaterial(THREE.MeshBasicMaterial, { color: 0xffff00 }),
        origin: createTrackedMaterial(THREE.MeshBasicMaterial, { color: 0xffffff }),
        crosshair: createTrackedMaterial(THREE.MeshBasicMaterial, { color: 0x000000 })
      };
    };
    
    const createOriginPoint = (materials) => {
      const originGeometry = createTrackedGeometry(THREE.SphereGeometry, 5);
      const originSphere = createTrackedMesh(originGeometry, materials.origin);
      originSphere.position.set(0, 0, 0);
      cncGroup.add(originSphere);
    };

    const createTextSprite = (text, color = '#ffffff') => {
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d');
      canvas.width = 160;
      canvas.height = 160;
      
      // Clear background
      context.clearRect(0, 0, canvas.width, canvas.height);
      
      // Create symmetric rounded rectangle dark background
      const padding = 20;
      const radius = 15;
      const bgX = padding;
      const bgY = padding;
      const bgWidth = canvas.width - padding * 2;
      const bgHeight = canvas.height - padding * 2;
      
      // Draw rounded rectangle background
      context.beginPath();
      context.roundRect(bgX, bgY, bgWidth, bgHeight, radius);
      context.fillStyle = 'rgba(0, 0, 0, 0.85)';
      context.fill();
      context.strokeStyle = 'rgba(255, 255, 255, 0.3)';
      context.lineWidth = 2;
      context.stroke();
      
      // Add bold text
      context.font = 'bold 80px Arial';
      context.textAlign = 'center';
      context.textBaseline = 'middle';
      
      // Main text with intense color - centered in square canvas
      context.fillStyle = color;
      context.fillText(text, 80, 80);
      
      const texture = trackResource(new THREE.CanvasTexture(canvas), 'textures');
      const spriteMaterial = createTrackedMaterial(THREE.SpriteMaterial, { 
        map: texture,
        transparent: true,
        opacity: 1.0
      });
      const sprite = trackResource(new THREE.Sprite(spriteMaterial), 'meshes');
      sprite.scale.set(25, 25, 1);
      
      return sprite;
    };
    
    // Axis configuration for unified creation
    const AXIS_CONFIGS = {
      x: {
        lengthProp: 'xAxisLength',
        label: 'X',
        color: '#ff1744',
        materialKey: 'xAxis',
        axisPosition: (length) => [length / 2, 0, 0],
        axisRotation: [0, 0, Math.PI / 2],
        arrowPosition: (length) => [length, 0, 0],
        arrowRotation: [0, 0, -Math.PI / 2],
        labelPosition: (length) => [length, -50, 40],
        meshRef: () => ({ axis: 'xAxisMesh', arrow: 'xArrowMesh', label: 'xAxisLabel' })
      },
      y: {
        lengthProp: 'yAxisLength',
        label: 'Y',
        color: '#00e676',
        materialKey: 'yAxis',
        axisPosition: (length) => [0, length / 2, 0],
        axisRotation: [0, 0, 0],
        arrowPosition: (length) => [0, length, 0],
        arrowRotation: [0, 0, 0],
        labelPosition: (length) => [-50, length, 40],
        meshRef: () => ({ axis: 'yAxisMesh', arrow: 'yArrowMesh', label: 'yAxisLabel' })
      },
      z: {
        lengthProp: 'zAxisLength',
        label: 'Z',
        color: '#2196f3',
        materialKey: 'zAxis',
        axisPosition: (length) => [0, 0, length / 2],
        axisRotation: [Math.PI / 2, 0, 0],
        arrowPosition: (length) => [0, 0, length],
        arrowRotation: [Math.PI / 2, 0, 0],
        labelPosition: (length) => [-50, 40, length],
        meshRef: () => ({ axis: 'zAxisMesh', arrow: 'zArrowMesh', label: 'zAxisLabel' })
      }
    };
    
    const createAxis = (axisType, materials) => {
      const config = AXIS_CONFIGS[axisType];
      const length = props.cncConfig[config.lengthProp];
      
      if (length <= 0) return;
      
      // Create axis cylinder
      const axisGeometry = createTrackedGeometry(THREE.CylinderGeometry, 2, 2, length);
      const axisMesh = createTrackedMesh(axisGeometry, materials[config.materialKey]);
      axisMesh.position.set(...config.axisPosition(length));
      axisMesh.rotation.set(...config.axisRotation);
      cncGroup.add(axisMesh);
      
      // Create arrow
      const arrowGeometry = createTrackedGeometry(THREE.ConeGeometry, 5, 15, 8);
      const arrowMesh = createTrackedMesh(arrowGeometry, materials[config.materialKey]);
      arrowMesh.position.set(...config.arrowPosition(length));
      arrowMesh.rotation.set(...config.arrowRotation);
      cncGroup.add(arrowMesh);
      
      // Create label
      const label = createTextSprite(config.label, config.color);
      label.position.set(...config.labelPosition(length));
      cncGroup.add(label);
      
      // Store references for later use
      if (axisType === 'x') {
        xAxisMesh = axisMesh;
        xArrowMesh = arrowMesh;
        xAxisLabel = label;
      } else if (axisType === 'y') {
        yAxisMesh = axisMesh;
        yArrowMesh = arrowMesh;
        yAxisLabel = label;
      } else if (axisType === 'z') {
        zAxisMesh = axisMesh;
        zArrowMesh = arrowMesh;
        zAxisLabel = label;
      }
      
      return { axis: axisMesh, arrow: arrowMesh, label };
    };
    
    const initializeToolPosition = () => {
      displayPosition.value.x = props.currentPos.x;
      displayPosition.value.y = props.currentPos.y;
      displayPosition.value.z = props.currentPos.z;
      
      // Initialize cached values
      cachedValues.lastToolPosition.x = props.currentPos.x;
      cachedValues.lastToolPosition.y = props.currentPos.y;
      cachedValues.lastToolPosition.z = props.currentPos.z;
      cachedValues.lastDisplayPosition.x = props.currentPos.x;
      cachedValues.lastDisplayPosition.y = props.currentPos.y;
      cachedValues.lastDisplayPosition.z = props.currentPos.z;
    };
    
    // Crosshair configuration for unified creation
    const CROSSHAIR_CONFIG = {
      size: 20,
      radius: 0.5,
      directions: [
        { name: 'horizontal', rotation: [0, 0, Math.PI / 2] }, // X direction
        { name: 'vertical', rotation: [Math.PI / 2, 0, 0] },   // Y direction  
        { name: 'depth', rotation: [0, 0, 0] }                 // Z direction
      ]
    };
    
    const createCrosshairs = (parent, material) => {
      const crosshairs = [];
      
      CROSSHAIR_CONFIG.directions.forEach(direction => {
        const geometry = createTrackedGeometry(
          THREE.CylinderGeometry, 
          CROSSHAIR_CONFIG.radius, 
          CROSSHAIR_CONFIG.radius, 
          CROSSHAIR_CONFIG.size
        );
        const crosshair = createTrackedMesh(geometry, material);
        crosshair.rotation.set(...direction.rotation);
        parent.add(crosshair);
        crosshairs.push(crosshair);
      });
      
      return crosshairs;
    };
    
    const createToolCrosshairs = (materials) => {
      return createCrosshairs(toolHead, materials.crosshair);
    };
    
    const createToolHead = (materials) => {
      const toolGeometry = createTrackedGeometry(THREE.SphereGeometry, 12);
      toolHead = createTrackedMesh(toolGeometry, materials.tool);
      // Convert to visual coordinates for proper display
      const visualPosition = getVisualPosition(props.currentPos);
      toolHead.position.set(visualPosition.x, visualPosition.y, visualPosition.z);
      
      initializeToolPosition();
      cncGroup.add(toolHead);
      createToolCrosshairs(materials);
    };
    
    // Grid configurations for unified creation
    const GRID_CONFIGS = {
      xy: {
        dimensions: ['workingZoneX', 'workingZoneY'],
        position: [0, 0, -1],
        visibilityCondition: () => showGrid && currentCameraView.value === 'Top',
        meshRef: 'gridHelper',
        lineConfigs: [
          { // Vertical lines (parallel to Y axis)
            axis: 0, // X axis divisions
            startCoords: (pos, dims) => [pos, 0, 0],
            endCoords: (pos, dims) => [pos, dims[1], 0]
          },
          { // Horizontal lines (parallel to X axis)  
            axis: 1, // Y axis divisions
            startCoords: (pos, dims) => [0, pos, 0],
            endCoords: (pos, dims) => [dims[0], pos, 0]
          }
        ]
      },
      xz: {
        dimensions: ['workingZoneX', 'workingZoneZ'],
        position: [0, -1, 0],
        visibilityCondition: () => showGrid && currentCameraView.value === 'Side',
        meshRef: 'fineGridHelper',
        lineConfigs: [
          { // Vertical lines (parallel to Z axis)
            axis: 0, // X axis divisions
            startCoords: (pos, dims) => [pos, 0, 0],
            endCoords: (pos, dims) => [pos, 0, dims[1]]
          },
          { // Horizontal lines (parallel to X axis)
            axis: 1, // Z axis divisions  
            startCoords: (pos, dims) => [0, 0, pos],
            endCoords: (pos, dims) => [dims[0], 0, pos]
          }
        ]
      }
    };
    
    const createGrid = (gridType) => {
      const config = GRID_CONFIGS[gridType];
      const dimensions = config.dimensions.map(prop => props.cncConfig[prop]);
      const divisions = dimensions.map(dim => Math.max(Math.floor(dim / gridSpacing.value), 4));
      
      const geometry = trackResource(new THREE.BufferGeometry(), 'geometries');
      const vertices = [];
      
      // Generate lines based on configuration
      config.lineConfigs.forEach((lineConfig, index) => {
        const divisionCount = divisions[lineConfig.axis];
        const dimensionValue = dimensions[lineConfig.axis];
        
        for (let i = 0; i <= divisionCount; i++) {
          const pos = (i / divisionCount) * dimensionValue;
          vertices.push(...lineConfig.startCoords(pos, dimensions));
          vertices.push(...lineConfig.endCoords(pos, dimensions));
        }
      });
      
      geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
      const material = createTrackedMaterial(THREE.LineBasicMaterial, {
        color: 0x2a2a3a,
        opacity: 0.6,
        transparent: true
      });
      
      const mesh = trackResource(new THREE.LineSegments(geometry, material), 'meshes');
      mesh.position.set(...config.position);
      mesh.visible = config.visibilityCondition();
      cncGroup.add(mesh);
      
      // Store reference for later use
      if (config.meshRef === 'gridHelper') {
        gridHelper = mesh;
      } else if (config.meshRef === 'fineGridHelper') {
        fineGridHelper = mesh;
      }
      
      return mesh;
    };
    
    const createSimpleAxisVisualization = () => {
      const materials = createAxisMaterials();
      
      createOriginPoint(materials);
      
      // Only create axes that are selected
      if (props.cncConfig.selectedAxes?.x === true) {
        createAxis('x', materials);
      }
      if (props.cncConfig.selectedAxes?.y === true) {
        createAxis('y', materials);
      }
      if (props.cncConfig.selectedAxes?.z === true) {
        createAxis('z', materials);
      }
      
      createToolHead(materials);
      
      // Only create grids for selected axes
      if (props.cncConfig.selectedAxes?.x === true && props.cncConfig.selectedAxes?.y === true) {
        createGrid('xy');
      }
      if (props.cncConfig.selectedAxes?.x === true && props.cncConfig.selectedAxes?.z === true) {
        createGrid('xz');
      }
      
      createClickTarget();
    };
    
    // Working zone material configuration
    const WORKING_ZONE_MATERIAL = {
      color: 0xffa500,  // Orange color - distinct from axes
      opacity: 0.8,     // Much more visible
      transparent: true,
      linewidth: 2      // Thicker lines
    };
    
    const createWorkingZoneGeometry = (dimensions) => {
      const { x, y, z } = dimensions;
      const geometry = createTrackedGeometry(THREE.BoxGeometry, x, y, z);
      return trackResource(new THREE.EdgesGeometry(geometry), 'geometries');
    };
    
    const createWorkingZone = (swapXY = false) => {
      // Remove existing working zone if present
      if (workingZoneMesh) {
        cncGroup.remove(workingZoneMesh);
      }
      
      // Calculate dimensions using centralized utility
      const bounds = getWorkingZoneBounds(props.cncConfig, false);
      let dimensions = {
        x: bounds.x || 1, // Minimal dimension for unselected axis
        y: bounds.y || 1,
        z: bounds.z || 1
      };
      
      // For visual display only, swap X/Y dimensions in Top view
      if (swapXY) {
        dimensions = {
          x: bounds.y || 1,  // Visual X shows physical Y bounds
          y: bounds.x || 1,  // Visual Y shows physical X bounds  
          z: bounds.z || 1
        };
      }
      
      
      // Create geometry and material
      const edgesGeometry = createWorkingZoneGeometry(dimensions);
      const material = createTrackedMaterial(THREE.LineBasicMaterial, WORKING_ZONE_MATERIAL);
      
      // Create mesh
      workingZoneMesh = trackResource(new THREE.LineSegments(edgesGeometry, material), 'meshes');
      
      // Position working zone at origin to align with grid (not centered)
      workingZoneMesh.position.set(
        dimensions.x / 2,
        dimensions.y / 2,
        dimensions.z / 2
      );
      
      workingZoneMesh.visible = showWorkingZone.value;
      cncGroup.add(workingZoneMesh);
      
      return workingZoneMesh;
    };
    
    
    const getSceneBounds = () => {
      // Always use the cached dynamic bounds
      const currentBounds = getBoundingBoxForView(currentCameraView.value);
      
      // Store dimensions for compatibility with existing code
      const size = new THREE.Vector3();
      currentBounds.getSize(size);
      currentBounds.dimensions = {
        x: size.x,
        y: size.y, 
        z: size.z,
        diagonal: Math.sqrt(size.x * size.x + size.y * size.y + size.z * size.z)
      };
      
      return currentBounds;
    };
    
    const createClickTarget = () => {
      // Create a ghost tool head identical to the original but transparent
      const ghostGeometry = createTrackedGeometry(THREE.SphereGeometry, 12); // Same size as actual tool
      const ghostMaterial = createTrackedMaterial(THREE.MeshBasicMaterial, { 
        color: 0xffff00, // Same yellow color as original
        transparent: true,
        opacity: 0.3, // Semi-transparent ghost effect
      });
      ghostToolHead = createTrackedMesh(ghostGeometry, ghostMaterial);
      ghostToolHead.visible = false; // Initially hidden
      
      // Add ghost crosshairs using unified creation function
      const ghostCrosshairMaterial = createTrackedMaterial(THREE.MeshBasicMaterial, { 
        color: 0x000000, // Same black color as original
        transparent: true,
        opacity: 0.3 // Semi-transparent
      });
      
      createCrosshairs(ghostToolHead, ghostCrosshairMaterial);
      
      cncGroup.add(ghostToolHead);
      
      // Remove the cyan ring - we don't need extra indicators
      clickTarget = null;
    };

    // Mouse event throttling
    let mouseAnimationFrame = null;
    let pendingMouseUpdate = null;

    // Mouse event handling functions
    const createMouseState = () => {
      return {
        isLeftMouseDown: false,
        mouseX: 0,
        mouseY: 0,
        isDragging: false,
        lastDeltaX: 0,
        lastDeltaY: 0
        // Right mouse state and deltaHistory removed - rotation disabled
      };
    };
    
    const handleMouseDown = (mouseState) => (event) => {
      event.preventDefault();
      mouseState.mouseX = event.clientX;
      mouseState.mouseY = event.clientY;
      mouseState.isDragging = false;
      
      if (event.button === 0) {
        mouseState.isLeftMouseDown = true;
      }
      // Right mouse rotation removed
    };
    
    const handleMouseUp = (mouseState) => (event) => {
      if (event.button === 0) {
        mouseState.isLeftMouseDown = false;
        
        // Handle click-to-move only in fixed camera views and if not dragging
        if (!mouseState.isDragging && (currentCameraView.value === 'Top' || currentCameraView.value === 'Side')) {
          handleClickToMove(event);
        }
      }
      // Right mouse tracking removed
    };
    
    // Cache frequently used vectors to reduce garbage collection
    const vectorCache = {
      rightVector: new THREE.Vector3(),
      upVector: new THREE.Vector3(),
      direction: new THREE.Vector3(),
      panX: new THREE.Vector3(),
      panY: new THREE.Vector3(),
      tempVector: new THREE.Vector3()
    };

    const calculatePanning = (deltaX, deltaY) => {
      const panSpeed = 2;
      
      // Reuse cached vectors to reduce object creation
      camera.getWorldDirection(vectorCache.direction);
      vectorCache.rightVector.crossVectors(camera.up, vectorCache.direction);
      vectorCache.rightVector.normalize();
      
      // Use camera's up vector directly
      vectorCache.upVector.copy(camera.up);
      
      // Calculate pan movement using cached vectors
      vectorCache.panX.copy(vectorCache.rightVector).multiplyScalar(deltaX * panSpeed);
      vectorCache.panY.copy(vectorCache.upVector).multiplyScalar(deltaY * panSpeed);
      
      return { 
        panX: vectorCache.panX.clone(), 
        panY: vectorCache.panY.clone() 
      };
    };
    
    // Cache panning limits calculations
    let cachedPanLimit = null;
    let cachedCenter = null;
    let lastConfigHash = null;

    const getCachedPanningParams = () => {
      const configHash = `${props.cncConfig.xAxisLength}-${props.cncConfig.yAxisLength}-${props.cncConfig.zAxisLength}`;
      
      if (configHash !== lastConfigHash) {
        const maxDimension = Math.max(
          props.cncConfig.xAxisLength,
          props.cncConfig.yAxisLength,
          props.cncConfig.zAxisLength
        );
        cachedPanLimit = maxDimension * 2;
        cachedCenter = new THREE.Vector3(
          props.cncConfig.xAxisLength / 2,
          props.cncConfig.yAxisLength / 2,
          props.cncConfig.zAxisLength / 2
        );
        lastConfigHash = configHash;
      }
      
      return { panLimit: cachedPanLimit, center: cachedCenter };
    };

    const applyPanningLimits = (newPosition) => {
      // Use cached camera properties to avoid redundant calculations
      const cameraProps = getCameraPropertiesForView();
      const bounds = cameraProps.bounds;
      const center = cameraProps.center.vector;
      
      // Allow panning within 2x the bounding box diagonal from center
      // This gives freedom while ensuring the scene remains accessible
      const panLimit = bounds.dimensions.diagonal;
      
      const constrainedPosition = newPosition.clone();
      
      // Constrain each axis independently
      const offsetFromCenter = constrainedPosition.clone().sub(center);
      if (Math.abs(offsetFromCenter.x) > panLimit) {
        constrainedPosition.x = center.x + Math.sign(offsetFromCenter.x) * panLimit;
      }
      if (Math.abs(offsetFromCenter.y) > panLimit) {
        constrainedPosition.y = center.y + Math.sign(offsetFromCenter.y) * panLimit;
      }
      if (Math.abs(offsetFromCenter.z) > panLimit) {
        constrainedPosition.z = center.z + Math.sign(offsetFromCenter.z) * panLimit;
      }
      
      return constrainedPosition;
    };
    
    const handleCameraPanning = (deltaX, deltaY) => {
      // Cancel any active camera transition that might interfere with panning
      if (activeTransitionId) {
        cancelAnimationFrame(activeTransitionId);
        activeTransitionId = null;
      }
      
      // Labels no longer hidden during panning since rotation is disabled
      
      const { panX, panY } = calculatePanning(deltaX, deltaY);
      const newPosition = camera.position.clone().add(panX).add(panY);
      const constrainedPosition = applyPanningLimits(newPosition);
      
      camera.position.copy(constrainedPosition);
      markDirty('rendering');
    };
    
    // Rotation cache removed - no longer needed since mouse rotation is disabled

    let cachedRotationLimits = null;
    let lastRotationConfigHash = null;

    const getCachedRotationLimits = () => {
      const configHash = `${props.cncConfig.xAxisLength}-${props.cncConfig.yAxisLength}-${props.cncConfig.zAxisLength}`;
      
      if (configHash !== lastRotationConfigHash) {
        const maxDimension = Math.max(
          props.cncConfig.xAxisLength,
          props.cncConfig.yAxisLength,
          props.cncConfig.zAxisLength
        );
        cachedRotationLimits = {
          minRadius: maxDimension * 0.5,
          maxRadius: maxDimension * 5
        };
        lastRotationConfigHash = configHash;
      }
      
      return cachedRotationLimits;
    };

    const handleCameraRotation = (deltaX, deltaY) => {
      // Mouse rotation disabled - only use view switching buttons
      return;
    };
    
    // Throttled mouse update processing
    const processMouseUpdate = (mouseState, deltaX, deltaY) => {
      // Only handle panning now - rotation is disabled
      if (mouseState.isLeftMouseDown) {
        handleCameraPanning(deltaX, deltaY);
      }
      // Right mouse rotation removed
    };

    
    
    const updateMouseTooltip = (normalizedMouse, screenX, screenY) => {
      // Only show tooltip in fixed views where clicking is enabled
      const isFixedView = currentCameraView.value === 'Top' || currentCameraView.value === 'Side';
      if (!isFixedView || !raycaster || !camera || !scene) {
        mouseTooltip.value.visible = false;
        return;
      }
      
      raycaster.setFromCamera(normalizedMouse, camera);
      
      // Use raycasting with plane intersection
      let physicalPosition = null;
      
      if (currentCameraView.value === 'Top') {
        // Top view: intersect with XY plane at Z=0
        const plane = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0);
        const intersectionPoint = new THREE.Vector3();
        if (raycaster.ray.intersectPlane(plane, intersectionPoint)) {
          // In Top view, visual X maps to physical Y and visual Y maps to physical X
          physicalPosition = {
            x: intersectionPoint.y,  // Visual Y becomes physical X
            y: intersectionPoint.x,  // Visual X becomes physical Y
            z: targetPosition.value?.z || props.currentPos.z // Keep Z from previous target or current
          };
        }
      } else if (currentCameraView.value === 'Side') {
        // Side view: intersect with XZ plane at Y=0
        const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
        const intersectionPoint = new THREE.Vector3();
        if (raycaster.ray.intersectPlane(plane, intersectionPoint)) {
          physicalPosition = {
            x: targetPosition.value?.x || props.currentPos.x, // Keep X from previous target or current
            y: targetPosition.value?.y || props.currentPos.y, // Keep Y from previous target or current
            z: intersectionPoint.z   // Only set Z from click
          };
        }
      }
      
      if (physicalPosition) {
        // Snap to 1mm precision - same as clicking would do
        const snappedPosition = {
          x: snapToGrid(physicalPosition.x, 1.0), // 1mm precision
          y: snapToGrid(physicalPosition.y, 1.0), // 1mm precision
          z: snapToGrid(physicalPosition.z, 1.0)  // 1mm precision
        };
        
        // Check if position is within working zone
        if (isWithinWorkingZoneLocal(snappedPosition)) {
          mouseTooltip.value = {
            visible: true,
            position: snappedPosition,
            screenX: screenX,
            screenY: screenY
          };
        } else {
          mouseTooltip.value.visible = false;
        }
      } else {
        mouseTooltip.value.visible = false;
      }
    };
    
    const handleMouseMove = (mouseState) => (event) => {
      // Always update mouse position for tooltip
      const rect = renderer.domElement.getBoundingClientRect();
      const mouse = new THREE.Vector2(
        ((event.clientX - rect.left) / rect.width) * 2 - 1,
        -((event.clientY - rect.top) / rect.height) * 2 + 1
      );
      
      // Update tooltip position
      updateMouseTooltip(mouse, event.clientX - rect.left, event.clientY - rect.top);
      
      if (!mouseState.isLeftMouseDown) return;  // Only handle left mouse for panning
      
      const deltaX = event.clientX - mouseState.mouseX;
      const deltaY = event.clientY - mouseState.mouseY;
      
      // Mark as dragging if mouse moved more than a small threshold
      if (Math.abs(deltaX) > 5 || Math.abs(deltaY) > 5) {
        mouseState.isDragging = true;
      }
      
      // Store pending update data
      pendingMouseUpdate = {
        mouseState,
        deltaX,
        deltaY
      };
      
      mouseState.mouseX = event.clientX;
      mouseState.mouseY = event.clientY;
      
      // Throttle mouse updates using requestAnimationFrame
      if (!mouseAnimationFrame) {
        mouseAnimationFrame = requestAnimationFrame(() => {
          if (pendingMouseUpdate) {
            const { mouseState: ms, deltaX: dx, deltaY: dy } = pendingMouseUpdate;
            processMouseUpdate(ms, dx, dy);
            pendingMouseUpdate = null;
          }
          mouseAnimationFrame = null;
        });
      }
    };
    
    const handleContextMenu = (event) => {
      event.preventDefault();
    };
    
    // Cache wheel/zoom calculations
    const zoomCache = {
      direction: new THREE.Vector3(),
      targetPosition: new THREE.Vector3()
    };

    let cachedZoomLimits = null;
    let lastZoomConfigHash = null;

    const getCachedZoomLimits = () => {
      const configHash = `${props.cncConfig.xAxisLength}-${props.cncConfig.yAxisLength}-${props.cncConfig.zAxisLength}-${props.cncConfig.workingZoneX}-${props.cncConfig.workingZoneY}-${props.cncConfig.workingZoneZ}-${currentCameraView.value}`;
      
      if (configHash !== lastZoomConfigHash) {
        // Calculate optimal distance for 0.5cm margin (this is our baseline)
        const optimalDistance = getCameraPropertiesForView().distance;
        
        // Minimum distance: allow getting closer but not too close to avoid clipping
        // Allow zooming to 50% of optimal distance
        const minDistance = optimalDistance * 0.5;
        
        // Maximum distance: allow zooming out to 3x optimal distance
        // This gives freedom while maintaining reasonable limits
        const maxDistance = optimalDistance * 3;
        
        cachedZoomLimits = {
          minDistance: minDistance,
          maxDistance: maxDistance
        };
        lastZoomConfigHash = configHash;
        
        logger.debug('Updated zoom limits:', {
          configHash,
          minDistance,
          maxDistance
        });
      }
      
      return cachedZoomLimits;
    };

    const handleWheel = (event) => {
      event.preventDefault();
      const scale = event.deltaY > 0 ? 1.1 : 0.9;
      const center = getCameraCenter().vector;
      
      // Use cached zoom limits
      const { minDistance, maxDistance } = getCachedZoomLimits();
      
      // Zoom towards/away from center with limits using cached vectors
      zoomCache.direction.copy(camera.position).sub(center).normalize();
      const currentDistance = camera.position.distanceTo(center);
      const newDistance = Math.min(maxDistance, Math.max(minDistance, currentDistance * scale));
      
      // Apply direct zoom without smooth lerp to avoid interfering with panning
      zoomCache.targetPosition.copy(center).add(zoomCache.direction.multiplyScalar(newDistance));
      camera.position.copy(zoomCache.targetPosition);
      markDirty('rendering');
    };
    
    const setupControls = () => {
      const mouseState = createMouseState();
      
      const onMouseDown = handleMouseDown(mouseState);
      const onMouseUp = handleMouseUp(mouseState);
      const onMouseMove = handleMouseMove(mouseState);
      
      renderer.domElement.addEventListener('mousedown', onMouseDown);
      renderer.domElement.addEventListener('mouseup', onMouseUp);
      renderer.domElement.addEventListener('mousemove', onMouseMove);
      renderer.domElement.addEventListener('contextmenu', handleContextMenu);
      renderer.domElement.addEventListener('wheel', handleWheel);
    };
    
    // Helper functions for improved click-to-move accuracy
    const roundPosition = (value, precision = 0.01) => {
      // Round to 2 decimal places (0.01mm precision)
      return Math.round(value / precision) * precision;
    };
    
    const snapToGrid = (value, gridSize = null) => {
      const actualGridSize = gridSize || gridSpacing.value;
      return Math.round(value / actualGridSize) * actualGridSize;
    };
    
    const processClickPosition = (position) => {
      // Apply 1mm snapping for precise positioning (independent of visual grid)
      const snappedPosition = {
        x: snapToGrid(position.x, 1.0), // 1mm precision
        y: snapToGrid(position.y, 1.0), // 1mm precision
        z: snapToGrid(position.z, 1.0)  // 1mm precision
      };
      
      // Apply 2 decimal place rounding (0.01mm precision)
      return {
        x: roundPosition(snappedPosition.x, 0.01),
        y: roundPosition(snappedPosition.y, 0.01),
        z: roundPosition(snappedPosition.z, 0.01)
      };
    };
    
    const handleClickToMove = (event) => {
      try {
        // Check if WebGL is available and renderer is ready
        if (webglError.value || !renderer || !renderer.domElement) {
          logger.warn('Click-to-move blocked: WebGL error or renderer not available');
          return;
        }
        
        // Check for WebGL context
        const gl = renderer.getContext();
        if (!gl || gl.isContextLost()) {
          logger.warn('Click-to-move blocked: WebGL context lost');
          return;
        }
        
        // Ensure we don't interfere with mouse state
        event.stopPropagation();
        
        // Get mouse position relative to the renderer canvas with improved precision
        const rect = renderer.domElement.getBoundingClientRect();
        if (rect.width <= 0 || rect.height <= 0) {
          logger.warn('Click-to-move blocked: invalid canvas dimensions');
          return;
        }
        
        // Use double precision for mouse coordinates calculation
        const clientX = event.clientX;
        const clientY = event.clientY;
        const rectLeft = rect.left;
        const rectTop = rect.top;
        const rectWidth = rect.width;
        const rectHeight = rect.height;
        
        mouse.x = ((clientX - rectLeft) / rectWidth) * 2.0 - 1.0;
        mouse.y = -((clientY - rectTop) / rectHeight) * 2.0 + 1.0;
        
      
      // Update raycaster
      raycaster.setFromCamera(mouse, camera);
      
      // Create intersection plane based on current view using fixed reference planes
      let clickedPosition = null;
      
      if (currentCameraView.value === 'Top') {
        // Top view: intersect with XY plane at Z=0 for better accuracy
        const plane = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0); // Fixed Z=0 plane
        const intersectionPoint = new THREE.Vector3();
        if (raycaster.ray.intersectPlane(plane, intersectionPoint)) {
          // In Top view, visual X maps to physical Y and visual Y maps to physical X
          // So we need to swap the coordinates to match the physical CNC axes
          clickedPosition = {
            x: intersectionPoint.y,  // Visual Y becomes physical X
            y: intersectionPoint.x,  // Visual X becomes physical Y
            z: targetPosition.value?.z || props.currentPos.z // Keep Z from previous target or current
          };
          
        }
      } else if (currentCameraView.value === 'Side') {
        // Side view: intersect with XZ plane at Y=0 for better accuracy
        const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0); // Fixed Y=0 plane
        const intersectionPoint = new THREE.Vector3();
        if (raycaster.ray.intersectPlane(plane, intersectionPoint)) {
          clickedPosition = {
            x: targetPosition.value?.x || props.currentPos.x, // Keep X from previous target or current
            y: targetPosition.value?.y || props.currentPos.y, // Keep Y from previous target or current
            z: intersectionPoint.z   // Only set Z from click
          };
          
        }
      }
      
      if (clickedPosition) {
        // Process position for improved accuracy (grid snapping and precision rounding)
        clickedPosition = processClickPosition(clickedPosition);
        
        // Also show what the ghost will be positioned at
        const ghostPosition = formatPosition(clickedPosition);
      }
      
      if (clickedPosition && isWithinWorkingZoneLocal(clickedPosition)) {
        // Check if CNC is connected OR simulation mode is enabled
        if (!props.isCncConnected && !isSimulationMode.value) {
          logger.warn('Click-to-move blocked: CNC not connected and simulation disabled');
          return;
        }
        
        const axisCount = selectedLinearAxes.value.length;
        
        if (axisCount === 2) {
          // 2-axis system: immediate execution (existing behavior)
          showClickTarget(clickedPosition);
          
          if (isSimulationMode.value) {
            logger.info(`Simulation: Target set at position (${formatCoordinate(clickedPosition.x)}, ${formatCoordinate(clickedPosition.y)}, ${formatCoordinate(clickedPosition.z)})`);
            setSimulationTarget(clickedPosition);
          } else {
            // Set target position for real CNC movements too (for green indication)
            setTargetForRealMovement(
              clickedPosition,
              { onMoveTo: (pos) => emit('moveTo', pos), onTargetUpdate: (pos) => emit('targetUpdate', pos) },
              targetPosition,
              targetArrived,
              logger
            );
          }
        } else if (axisCount === 3) {
          // 3-axis system: require clicks in both Top and Side views
          if (currentCameraView.value === 'Top') {
            // Don't reset Side view position - preserve Z if already set
            topViewClicked.value = true;
            topViewPosition.value = { x: clickedPosition.x, y: clickedPosition.y };
            logger.info(`Top view clicked: X=${formatCoordinate(clickedPosition.x)}, Y=${formatCoordinate(clickedPosition.y)}`);
          } else if (currentCameraView.value === 'Side') {
            // Don't reset Top view position - preserve X,Y if already set
            sideViewClicked.value = true;
            sideViewPosition.value = { z: clickedPosition.z };
            logger.info(`Side view clicked: Z=${formatCoordinate(clickedPosition.z)}`);
          }
          
          // Check if both views have been clicked
          if (topViewClicked.value && sideViewClicked.value) {
            // Combine coordinates from both views
            const combinedPosition = {
              x: topViewPosition.value.x,
              y: topViewPosition.value.y,
              z: sideViewPosition.value.z
            };
            
            logger.info(`3-axis click complete: Combined position (${formatCoordinate(combinedPosition.x)}, ${formatCoordinate(combinedPosition.y)}, ${formatCoordinate(combinedPosition.z)})`);
            
            // Reset only the completion flags, keep both positions for subsequent clicks
            topViewClicked.value = false;
            sideViewClicked.value = false;
            // Don't reset either position - keep them for subsequent clicks in any view
            
            // Show target and execute movement
            showClickTarget(combinedPosition);
            
            if (isSimulationMode.value) {
              setSimulationTarget(combinedPosition);
            } else {
              // Set target position for real CNC movements too (for green indication)
              setTargetForRealMovement(
                combinedPosition,
                { onMoveTo: (pos) => emit('moveTo', pos), onTargetUpdate: (pos) => emit('targetUpdate', pos) },
                targetPosition,
                targetArrived,
                logger
              );
            }
          } else {
            // Show partial target for visual feedback
            showPartialClickTarget(clickedPosition, currentCameraView.value);
          }
        }
      } else if (clickedPosition && !isWithinWorkingZoneLocal(clickedPosition)) {
        logger.warn('Click-to-move blocked: Target outside working zone', clickedPosition);
      }
      } catch (error) {
        logger.error('Error in handleClickToMove:', error);
        
        // Check if it's a WebGL-related error
        if (error.message.includes('WebGL') || error.message.includes('context')) {
          webglError.value = 'click-handling-error';
          errorMessage.value = 'WebGL error occurred during click handling. Please try refreshing the page.';
        }
      }
    };
    
    const isWithinWorkingZoneLocal = (position) => {
      return isWithinWorkingZone(position, props.cncConfig, false, 0.01);
    };
    
    // Helper function to convert physical coordinates to visual coordinates for display
    const getVisualPosition = (physicalPosition) => {
      if (currentCameraView.value === 'Top') {
        // In Top view, visual coordinates need to be swapped for correct display
        return {
          x: physicalPosition.y,  // Physical Y becomes visual X
          y: physicalPosition.x,  // Physical X becomes visual Y  
          z: physicalPosition.z   // Z remains the same
        };
      }
      // In other views, use physical coordinates directly
      return { ...physicalPosition };
    };
    
    const showClickTarget = (position) => {
      // Show ghost tool head at target position with same precision and constraints as CNC movement
      if (ghostToolHead) {
        // Apply the same precision as CNC movement (2 decimal places)
        let precisePosition = formatPosition(position);
        
        // Apply working zone constraints with safety margin using centralized utility
        const bounds = getWorkingZoneBounds(props.cncConfig, false);
        const safetyMargin = 10; // The CNC firmware appears to apply a ~10mm safety margin
        
        if (props.cncConfig.selectedAxes?.x === true) {
          precisePosition.x = Math.max(0, Math.min(precisePosition.x, bounds.x - safetyMargin));
        }
        if (props.cncConfig.selectedAxes?.y === true) {
          precisePosition.y = Math.max(0, Math.min(precisePosition.y, bounds.y - safetyMargin));
        }
        if (props.cncConfig.selectedAxes?.z === true) {
          precisePosition.z = Math.max(0, Math.min(precisePosition.z, bounds.z - safetyMargin));
        }
        
        // Convert to visual coordinates for proper display
        const visualPosition = getVisualPosition(precisePosition);
        ghostToolHead.position.set(visualPosition.x, visualPosition.y, visualPosition.z);
        ghostToolHead.visible = true;
        // Ghost stays visible until tool reaches exact position
        // No timeout - ghost only disappears when tool arrives
        
      }
      
      // Set target position and start movement simulation
      if (toolHead) {
        const startPos = {
          x: toolHead.position.x,
          y: toolHead.position.y,
          z: toolHead.position.z
        };
        
        // Calculate distance for feedrate simulation
        const distance = Math.sqrt(
          Math.pow(position.x - startPos.x, 2) +
          Math.pow(position.y - startPos.y, 2) +
          Math.pow(position.z - startPos.z, 2)
        );
        
        // Calculate movement duration based on feedrate (mm/min)
        const feedrate = DEFAULT_FEEDRATE; // mm/min
        const feedratePerMs = feedrate / 60000; // Convert to mm/ms
        movementDuration.value = distance / feedratePerMs; // Duration in ms
        
        targetPosition.value = position;
        movementStartTime.value = Date.now();
        
        // Clear arrived status when new target is set
        targetArrived.value = false;
        
        // Emit target position update
        emit('targetUpdate', position);
      }
      
      // Create or update trajectory line
      markDirty('trajectoryLine');
      updateTrajectoryLine(position);
    };
    
    const showPartialClickTarget = (position, viewType) => {
      // Show partial target with different visual style
      if (ghostToolHead) {
        // For partial clicks, position ghost at current position but make it semi-transparent
        const currentPos = toolHead ? toolHead.position : props.currentPos;
        
        let partialPosition;
        if (viewType === 'Top') {
          // Show X,Y from click, Z from previous Side view click if available, otherwise current position
          const zPos = sideViewPosition.value ? sideViewPosition.value.z : currentPos.z;
          partialPosition = { x: position.x, y: position.y, z: zPos };
        } else if (viewType === 'Side') {
          // Show Z from click, X,Y from previous Top view click if available, otherwise current position
          // Use the most recent topViewPosition if it exists, otherwise use current position
          let xPos = currentPos.x;
          let yPos = currentPos.y;
          
          if (topViewPosition.value) {
            xPos = topViewPosition.value.x;
            yPos = topViewPosition.value.y;
          }
          
          partialPosition = { x: xPos, y: yPos, z: position.z };
        }
        
        // Convert to visual coordinates for proper display
        const visualPosition = getVisualPosition(partialPosition);
        ghostToolHead.position.set(visualPosition.x, visualPosition.y, visualPosition.z);
        
        ghostToolHead.visible = true;
        // Make ghost more transparent for partial clicks
        if (ghostToolHead.material) {
          ghostToolHead.material.opacity = 0.3;
        }
        
        // Force re-render to make ghost visible immediately
        markDirty('rendering');
        
        // Update trajectory line to show path to partial target
        markDirty('trajectoryLine');
        updateTrajectoryLine(partialPosition);
        
        // Update target position and emit for display
        targetPosition.value = partialPosition;
        targetArrived.value = false;
        emit('targetUpdate', partialPosition);
      }
      
      logger.info(`Partial target set in ${viewType} view: (${formatCoordinate(position.x)}, ${formatCoordinate(position.y)}, ${formatCoordinate(position.z)})`);
    };
    
    const clearPartialClicks = () => {
      // Reset all click states AND positions
      topViewClicked.value = false;
      sideViewClicked.value = false;
      topViewPosition.value = null;
      sideViewPosition.value = null;
      
      // Reset ghost tool head opacity
      if (ghostToolHead && ghostToolHead.material) {
        ghostToolHead.material.opacity = 0.5; // Default opacity
        ghostToolHead.visible = false;
      }
      
      logger.info('Partial clicks cleared');
    };
    
    const resetClickFlags = () => {
      // Reset only the click flags, preserve positions
      topViewClicked.value = false;
      sideViewClicked.value = false;
      logger.info('Click flags reset, positions preserved');
    };
    
    // Optimization: Smart trajectory line updates with dirty flags
    const updateTrajectoryLine = (targetPosition) => {
      try {
        // Check WebGL availability
        if (webglError.value || !renderer) {
          return;
        }
        
        // Only update if trajectory is dirty or target position changed
        if (!isDirty('trajectoryLine') && 
            cachedValues.lastTargetPosition && 
            !hasPositionChanged(targetPosition, cachedValues.lastTargetPosition)) {
          return; // Skip update if nothing changed
        }
      
      // Remove existing trajectory line if it exists
      if (trajectoryLine) {
        cncGroup.remove(trajectoryLine);
        // Properly dispose geometry and material
        if (trajectoryLine.geometry) {
          trajectoryLine.geometry.dispose();
        }
        if (trajectoryLine.material) {
          trajectoryLine.material.dispose();
        }
        trajectoryLine = null;
      }
      
      // Create new trajectory line from current tool position to target
      if (toolHead && targetPosition) {
        const currentPos = toolHead.position;
        // Convert target position to visual coordinates to match toolHead positioning
        const visualTargetPos = getVisualPosition(targetPosition);
        
        // Create line geometry showing simultaneous multi-axis movement
        // Direct straight line path from current to target position
        const points = [];
        
        // Start position
        points.push(new THREE.Vector3(currentPos.x, currentPos.y, currentPos.z));
        
        // Direct to target position (simultaneous movement) using visual coordinates
        points.push(new THREE.Vector3(visualTargetPos.x, visualTargetPos.y, visualTargetPos.z));
        
        // Use tracked resources for trajectory line (temporary objects)
        const geometry = trackResource(new THREE.BufferGeometry().setFromPoints(points), 'geometries');
        
        // Create dashed line material for trajectory
        const material = createTrackedMaterial(THREE.LineDashedMaterial, {
          color: 0xffff00, // Yellow to match tool color
          opacity: 0.5,
          transparent: true,
          dashSize: 3,
          gapSize: 2,
          linewidth: 2
        });
        
        trajectoryLine = trackResource(new THREE.Line(geometry, material), 'meshes');
        trajectoryLine.computeLineDistances(); // Required for dashed lines
        cncGroup.add(trajectoryLine);
        
        // Cache the target position
        cachedValues.lastTargetPosition = { ...targetPosition };
      }
      
        clearDirty('trajectoryLine');
      } catch (error) {
        logger.error('Error updating trajectory line:', error);
        
        // Clear trajectory line on error to prevent visual artifacts
        if (trajectoryLine) {
          try {
            cncGroup.remove(trajectoryLine);
            trajectoryLine = null;
          } catch (cleanupError) {
            logger.error('Error cleaning up trajectory line:', cleanupError);
          }
        }
      }
    };
    
    // Optimization: Efficient trajectory line position updates
    const updateTrajectoryLinePositions = () => {
      if (!trajectoryLine || !toolHead) return;
      
      const positions = trajectoryLine.geometry.attributes.position.array;
      const currentPos = toolHead.position;
      
      // Only update if tool position changed significantly
      if (hasPositionChanged(currentPos, { x: positions[0], y: positions[1], z: positions[2] }, 0.1)) {
        positions[0] = currentPos.x;
        positions[1] = currentPos.y;
        positions[2] = currentPos.z;
        trajectoryLine.geometry.attributes.position.needsUpdate = true;
        trajectoryLine.computeLineDistances();
        markDirty('rendering');
      }
    };
    
    const hideClickTarget = () => {
      if (ghostToolHead) {
        ghostToolHead.visible = false;
      }
      
      // Remove trajectory line with proper disposal
      if (trajectoryLine) {
        cncGroup.remove(trajectoryLine);
        // Properly dispose geometry and material
        if (trajectoryLine.geometry) {
          trajectoryLine.geometry.dispose();
        }
        if (trajectoryLine.material) {
          trajectoryLine.material.dispose();
        }
        trajectoryLine = null;
      }
    };
    
    const setSimulationTarget = (position) => {
      // Set target but don't start movement - wait for play button
      targetPosition.value = position;
      targetArrived.value = false;
      
      // Show ghost tool and trajectory line
      if (ghostToolHead) {
        // Convert to visual coordinates for proper display
        const visualPosition = getVisualPosition(position);
        ghostToolHead.position.set(visualPosition.x, visualPosition.y, visualPosition.z);
        ghostToolHead.visible = true;
      }
      markDirty('trajectoryLine');
      updateTrajectoryLine(position);
      
      emit('targetUpdate', position);
    };
    
    const executeSimulation = () => {
      if (!canExecuteSimulation.value) return;
      
      isExecutingSimulation.value = true;
      const target = targetPosition.value;
      
      // Calculate movement duration based on distance and feedrate
      if (toolHead && target) {
        const startPos = {
          x: toolHead.position.x,
          y: toolHead.position.y,
          z: toolHead.position.z
        };
        
        // Optimization: Use cached distance calculation
        const distance = calculateDistance(startPos, target);
        cachedValues.movementDistance = distance;
        
        const feedrate = DEFAULT_FEEDRATE; // mm/min
        const feedratePerMs = feedrate / 60000;
        movementDuration.value = distance / feedratePerMs;
        
        movementStartTime.value = Date.now();
        cachedValues.movementProgress = 0;
        
        // Simulation movement will be handled in the animation loop
        
        logger.info(`Simulation: Executing movement to (${formatCoordinate(target.x)}, ${formatCoordinate(target.y)}, ${formatCoordinate(target.z)})`);
      }
    };
    

    // Animation and Movement Functions
    const shouldSkipFrame = (currentTime) => {
      const isMoving = isSimulationMode.value && targetPosition.value && movementStartTime.value && isExecutingSimulation.value;
      const frameInterval = isMoving ? FRAME_INTERVAL : IDLE_FRAME_INTERVAL;
      
      if (currentTime - lastFrameTime < frameInterval) {
        return true; // Skip this frame to maintain target FPS
      }
      lastFrameTime = currentTime;
      return false;
    };
    
    const updateToolHeadMovement = () => {
      if (!toolHead) return false;
      
      if (isSimulationMode.value && targetPosition.value && movementStartTime.value && isExecutingSimulation.value) {
        return updateSimulationMovement();
      } else if (!isSimulationMode.value) {
        return updateRealCNCMovement();
      } else {
        return updateSimulationIdle();
      }
    };
    
    const animate = (currentTime = 0) => {
      try {
        // Early exit if not animating or if resources are being disposed
        if (!isAnimating.value || !scene || !camera || !renderer) {
          return;
        }
        
        // Check for WebGL context loss
        const gl = renderer.getContext();
        if (!gl || gl.isContextLost()) {
          logger.warn('Animation stopped: WebGL context lost');
          return;
        }
        
        animationId = requestAnimationFrame(animate);
        
        if (shouldSkipFrame(currentTime)) {
          return;
        }
        
        const hasChanges = updateToolHeadMovement();
        
        // Only render if something actually changed or rendering is explicitly dirty
        if (hasChanges || isDirty('rendering')) {
          try {
            renderer.render(scene, camera);
            clearDirty('rendering');
          } catch (renderError) {
            logger.error('Render error in animation loop:', renderError);
            
            // Check if it's a context lost error
            if (renderError.message.includes('context') || renderError.message.includes('lost')) {
              logger.warn('WebGL context appears to be lost during rendering');
              return; // Stop animation, let context restored handler take over
            }
            
            // For other render errors, continue but log them
            throw renderError;
          }
        }
      } catch (error) {
        logger.error('Error in animation loop:', error);
        
        // Don't stop animation for minor errors, but stop for critical ones
        if (error.message.includes('context') || error.message.includes('WebGL')) {
          logger.error('Critical WebGL error, stopping animation');
          stopAnimationLoop();
        }
      }
    };
    
    const calculateMovementProgress = () => {
      const elapsed = Date.now() - movementStartTime.value;
      return Math.min(elapsed / movementDuration.value, 1);
    };
    
    const getOrSetStartPosition = () => {
      if (!toolHead.userData.startX) {
        toolHead.userData.startX = toolHead.position.x;
        toolHead.userData.startY = toolHead.position.y;
        toolHead.userData.startZ = toolHead.position.z;
      }
      
      return {
        x: toolHead.userData.startX,
        y: toolHead.userData.startY,
        z: toolHead.userData.startZ
      };
    };
    
    const interpolatePosition = (startPos, targetPos, progress) => {
      return {
        x: startPos.x + (targetPos.x - startPos.x) * progress,
        y: startPos.y + (targetPos.y - startPos.y) * progress,
        z: startPos.z + (targetPos.z - startPos.z) * progress
      };
    };
    
    const updateSimulationMovement = () => {
      const progress = calculateMovementProgress();
      
      // Only recalculate if progress changed significantly
      if (Math.abs(progress - cachedValues.movementProgress) < 0.001) {
        return false;
      }
      cachedValues.movementProgress = progress;
      
      const startPos = getOrSetStartPosition();
      const newPosition = interpolatePosition(startPos, targetPosition.value, progress);
      
      // Only update if position changed significantly
      if (updateCachedPosition(newPosition, 'lastToolPosition')) {
        // Convert to visual coordinates for proper display
        const visualPosition = getVisualPosition(newPosition);
        toolHead.position.set(visualPosition.x, visualPosition.y, visualPosition.z);
        
        // Update display position only if it changed
        if (updateCachedPosition(newPosition, 'lastDisplayPosition')) {
          displayPosition.value.x = newPosition.x;
          displayPosition.value.y = newPosition.y;
          displayPosition.value.z = newPosition.z;
        }
        
        updateTrajectoryLinePositions();
        
        // Check if movement is complete
        if (progress >= 1) {
          completeSimulationMovement();
        }
        
        return true;
      }
      
      return false;
    };
    
    const updateRealCNCMovement = () => {
      const targetPos = {
        x: props.currentPos.x,
        y: props.currentPos.y,
        z: props.currentPos.z
      };
      
      // Convert to visual coordinates for interpolation calculations (to match toolHead.position)
      const visualTargetPos = getVisualPosition(targetPos);
      
      // Only update if target position changed
      if (!hasPositionChanged(targetPos, cachedValues.lastToolPosition)) {
        return false;
      }
      
      // Check if CNC is idle - if so, snap directly to position for accuracy
      const isIdle = cncState.value && cncState.value.toLowerCase() === 'idle';
      
      let newVisualPosition;
      if (isIdle) {
        // When idle, snap directly to exact position to eliminate precision drift
        newVisualPosition = { ...visualTargetPos };
      } else {
        // When moving, use smooth interpolation but with higher precision near target
        const distance = calculateDistance(toolHead.position, visualTargetPos);
        const lerpSpeed = distance < 0.1 ? 0.8 : 0.15; // Faster convergence when close
        newVisualPosition = {
          x: toolHead.position.x + (visualTargetPos.x - toolHead.position.x) * lerpSpeed,
          y: toolHead.position.y + (visualTargetPos.y - toolHead.position.y) * lerpSpeed,
          z: toolHead.position.z + (visualTargetPos.z - toolHead.position.z) * lerpSpeed
        };
        
        // Snap to exact position when very close (within 0.01mm)
        if (distance < 0.01) {
          newVisualPosition = { ...visualTargetPos };
        }
      }
      
      // Force update when snapping to exact position (idle state or very close)
      const forceUpdate = isIdle || calculateDistance(toolHead.position, visualTargetPos) < 0.01;
      
      // Check if visual position changed significantly for smooth animation
      if (updateCachedPosition(newVisualPosition, 'lastToolPosition') || forceUpdate) {
        // Use the calculated visual position directly
        toolHead.position.set(newVisualPosition.x, newVisualPosition.y, newVisualPosition.z);
        
        // Always update display position when forcing exact position (use physical coords for display)
        if (updateCachedPosition(targetPos, 'lastDisplayPosition') || forceUpdate) {
          displayPosition.value.x = targetPos.x;
          displayPosition.value.y = targetPos.y;
          displayPosition.value.z = targetPos.z;
        }
        
        // Complex target arrival detection removed - now handled by completeRealCNCMovement() call
        
        return true;
      }
      
      return false;
    };
    
    const checkGhostToolHeadReached = () => {
      if (ghostToolHead && ghostToolHead.visible) {
        const distance = calculateDistance(toolHead.position, ghostToolHead.position);
        if (distance < 0.5) {
          hideClickTarget();
          emit('targetUpdate', null);
        }
      }
    };
    
    const updateSimulationIdle = () => {
      const currentPos = {
        x: displayPosition.value.x,
        y: displayPosition.value.y,
        z: displayPosition.value.z
      };
      
      // Keep tool head at current display position without unnecessary updates
      if (hasPositionChanged(currentPos, { x: toolHead.position.x, y: toolHead.position.y, z: toolHead.position.z })) {
        // Convert to visual coordinates for proper display
        const visualPosition = getVisualPosition(currentPos);
        toolHead.position.set(visualPosition.x, visualPosition.y, visualPosition.z);
        updateTrajectoryLinePositions();
        checkGhostToolHeadReached();
        return true;
      }
      
      return false;
    };
    
    const completeSimulationMovement = () => {
      lastTargetPosition.value = { ...targetPosition.value };
      targetPosition.value = null;
      targetArrived.value = true;
      isExecutingSimulation.value = false;
      movementStartTime.value = null;
      toolHead.userData.startX = null;
      toolHead.userData.startY = null;
      toolHead.userData.startZ = null;
      cachedValues.movementProgress = 0;
      hideClickTarget();
      emit('targetUpdate', null);
    };

    const completeRealCNCMovement = () => {
      // Handle target position state similar to simulation completion
      if (targetPosition.value) {
        lastTargetPosition.value = { ...targetPosition.value };
        targetPosition.value = null;
        emit('targetUpdate', null);
      }
      // Set target arrived to trigger green indication
      targetArrived.value = true;
      hideClickTarget();
      logger.info('Real CNC movement completed, target arrived indication set');
    };
    
    // Camera management functions
    const getCameraPropertiesForView = (viewType = null) => {
      // Get bounds once and reuse for both center and distance calculations
      const bounds = getBoundingBoxForView(viewType || currentCameraView.value);
      
      // Add dimensions for compatibility if needed
      if (viewType && !bounds.dimensions) {
        const size = new THREE.Vector3();
        bounds.getSize(size);
        bounds.dimensions = {
          x: size.x,
          y: size.y, 
          z: size.z,
          diagonal: Math.sqrt(size.x * size.x + size.y * size.y + size.z * size.z)
        };
      }
      
      // Calculate center
      const center = new THREE.Vector3();
      bounds.getCenter(center);
      
      // Calculate distance to keep bounding box 0.5cm from viewport edges
      
      // Get viewport dimensions - use renderer dimensions for consistency
      const viewportWidth = renderer?.domElement?.width || threeContainer.value?.clientWidth || 800;
      const viewportHeight = renderer?.domElement?.height || threeContainer.value?.clientHeight || 600;
      
      // Convert 0.5cm to pixels (assuming ~96 DPI)
      const cmToPixels = 96 / 2.54; // 96 DPI conversion
      const marginPixels = 0.5 * cmToPixels; // 0.5cm margin
      
      // Calculate available viewport space after margins
      const availableWidth = viewportWidth - (2 * marginPixels);
      const availableHeight = viewportHeight - (2 * marginPixels);
      
      // Get bounding box dimensions in the view plane
      let boundingWidth, boundingHeight;
      
      if (viewType === 'Top') {
        // Top view: X and Y dimensions are visible
        boundingWidth = bounds.dimensions.x;
        boundingHeight = bounds.dimensions.y;
      } else if (viewType === 'Side') {
        // Side view: X and Z dimensions are visible
        boundingWidth = bounds.dimensions.x;
        boundingHeight = bounds.dimensions.z;
      } else {
        // 3D view: Use diagonal projections
        // In isometric view, we see X, Y, and Z projected
        boundingWidth = Math.sqrt(bounds.dimensions.x * bounds.dimensions.x + bounds.dimensions.y * bounds.dimensions.y);
        boundingHeight = bounds.dimensions.z;
      }
      
      // Calculate distance needed to fit bounding box in available viewport
      const currentCamera = camera || { fov: 60, aspect: viewportWidth / viewportHeight };
      const fov = THREE.MathUtils.degToRad(currentCamera.fov);
      const aspect = currentCamera.aspect;
      
      // Calculate distance based on field of view to fit the bounding box
      // We want the bounding box to fill the AVAILABLE viewport space (after margins)
      
      // First calculate distance needed for full viewport
      const distanceForWidth = (boundingWidth / 2) / (Math.tan(fov / 2) * aspect);
      const distanceForHeight = (boundingHeight / 2) / Math.tan(fov / 2);
      const baseDistance = Math.max(distanceForWidth, distanceForHeight);
      
      // Calculate how much smaller the available space is compared to full viewport
      const widthRatio = availableWidth / viewportWidth;  // e.g. 0.9 for 0.5cm margins
      const heightRatio = availableHeight / viewportHeight; // e.g. 0.9 for 0.5cm margins
      const ratio = Math.min(widthRatio, heightRatio); // Use the more restrictive ratio
      
      // To fit in smaller available space, we need to move camera farther away
      // The smaller the ratio, the farther we need to be
      // Add a generous safety buffer (20%) to ensure comfortable fit within margins
      // This accounts for floating-point precision and projection variations
      const safetyFactor = 0.80; // Make bounding box 20% smaller than available space
      const finalDistance = baseDistance / (ratio * safetyFactor);
      
      // Always store calculation details for debugging (not just when showBoundingBox is true)
      window.debugBoundingBoxCalc = {
        viewport: { width: viewportWidth, height: viewportHeight },
        marginPixels,
        availableWidth,
        availableHeight,
        boundingWidth,
        boundingHeight,
        baseDistance,
        ratios: { width: widthRatio.toFixed(3), height: heightRatio.toFixed(3), applied: ratio.toFixed(3) },
        safetyFactor,
        finalDistance,
        viewType: viewType || currentCameraView.value
      };
      
      return {
        center: {
          x: center.x,
          y: center.y,
          z: center.z,
          vector: center
        },
        distance: finalDistance,
        bounds: bounds
      };
    };
    
    // Simplified helper functions that use the cached system
    const getCameraCenter = (viewType = null) => {
      return getCameraPropertiesForView(viewType).center;
    };
    
    const getCameraDistance = (viewType = null) => {
      return getCameraPropertiesForView(viewType).distance;
    };
    
    const easeInOutCubic = (t) => {
      return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
    };
    
    let activeTransitionId = null;

    const smoothCameraTransition = (targetPosition, targetLookAt, duration = 500) => {
      // Cancel any existing transition
      if (activeTransitionId) {
        cancelAnimationFrame(activeTransitionId);
        activeTransitionId = null;
      }
      
      const startPosition = camera.position.clone();
      const startQuaternion = camera.quaternion.clone();
      
      // Create temporary camera to get target quaternion
      const tempCamera = camera.clone();
      tempCamera.position.copy(targetPosition);
      tempCamera.lookAt(targetLookAt);
      const targetQuaternion = tempCamera.quaternion.clone();
      
      const startTime = Date.now();
      
      const transitionAnimate = () => {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easedProgress = easeInOutCubic(progress);
        
        // Interpolate position and rotation
        camera.position.lerpVectors(startPosition, targetPosition, easedProgress);
        camera.quaternion.slerpQuaternions(startQuaternion, targetQuaternion, easedProgress);
        markDirty('rendering');
        
        if (progress < 1) {
          activeTransitionId = requestAnimationFrame(transitionAnimate);
        } else {
          camera.lookAt(targetLookAt);
          markDirty('rendering');
          activeTransitionId = null;
        }
      };
      
      activeTransitionId = requestAnimationFrame(transitionAnimate);
    };
    
    const swapXYAxes = (isTopView) => {
      if (!xAxisMesh || !yAxisMesh || !xArrowMesh || !yArrowMesh) return;
      
      if (isTopView) {
        // Swap X and Y axis positions and rotations
        // X axis goes to Y position
        xAxisMesh.position.set(0, props.cncConfig.xAxisLength / 2, 0);
        xAxisMesh.rotation.set(0, 0, 0); // Remove Z rotation for Y-like orientation
        
        xArrowMesh.position.set(0, props.cncConfig.xAxisLength, 0);
        xArrowMesh.rotation.set(0, 0, 0); // Remove Z rotation for Y-like orientation
        
        // Y axis goes to X position  
        yAxisMesh.position.set(props.cncConfig.yAxisLength / 2, 0, 0);
        yAxisMesh.rotation.z = Math.PI / 2; // Add Z rotation for X-like orientation
        
        yArrowMesh.position.set(props.cncConfig.yAxisLength, 0, 0);
        yArrowMesh.rotation.z = -Math.PI / 2; // Add Z rotation for X-like orientation
        yArrowMesh.rotation.x = 0; // Remove any X rotation
        yArrowMesh.rotation.y = 0; // Remove any Y rotation
        
      } else {
        // Restore normal positions
        // X axis back to X position
        xAxisMesh.position.set(props.cncConfig.xAxisLength / 2, 0, 0);
        xAxisMesh.rotation.z = Math.PI / 2;
        
        xArrowMesh.position.set(props.cncConfig.xAxisLength, 0, 0);
        xArrowMesh.rotation.z = -Math.PI / 2;
        xArrowMesh.rotation.x = 0;
        xArrowMesh.rotation.y = 0;
        
        // Y axis back to Y position
        yAxisMesh.position.set(0, props.cncConfig.yAxisLength / 2, 0);
        yAxisMesh.rotation.set(0, 0, 0);
        
        yArrowMesh.position.set(0, props.cncConfig.yAxisLength, 0);
        yArrowMesh.rotation.set(0, 0, 0);
      }
    };

    const swapWorkingZone = (isTopView) => {
      createWorkingZone(isTopView);
    };

    const updateSwappedGrid = (isTopView) => {
      if (!gridHelper) return;
      
      if (isTopView) {
        // Recreate grid with swapped dimensions for top view
        // Since axes are swapped, grid should reflect swapped working zone
        cncGroup.remove(gridHelper);
        
        const workingX = props.cncConfig.workingZoneY; // Use Y config for X grid lines  
        const workingY = props.cncConfig.workingZoneX; // Use X config for Y grid lines
        const gridDivisionsX = Math.max(Math.floor(workingX / gridSpacing.value), 4);
        const gridDivisionsY = Math.max(Math.floor(workingY / gridSpacing.value), 4);
        
        const xyGridGeometry = trackResource(new THREE.BufferGeometry(), 'geometries');
        const xyGridVertices = [];
        
        // Vertical lines (now parallel to swapped Y axis)
        for (let i = 0; i <= gridDivisionsX; i++) {
          const x = (i / gridDivisionsX) * workingX;
          xyGridVertices.push(x, 0, 0);
          xyGridVertices.push(x, workingY, 0);
        }
        
        // Horizontal lines (now parallel to swapped X axis)
        for (let i = 0; i <= gridDivisionsY; i++) {
          const y = (i / gridDivisionsY) * workingY;
          xyGridVertices.push(0, y, 0);
          xyGridVertices.push(workingX, y, 0);
        }
        
        xyGridGeometry.setAttribute('position', new THREE.Float32BufferAttribute(xyGridVertices, 3));
        
        const xyGridMaterial = trackResource(new THREE.LineBasicMaterial({
          color: 0x444444,
          opacity: 0.6,
          transparent: true
        }), 'materials');
        
        gridHelper = trackResource(new THREE.LineSegments(xyGridGeometry, xyGridMaterial), 'meshes');
        gridHelper.position.set(0, 0, -1);
        cncGroup.add(gridHelper);
      } else {
        // Restore original grid when not in top view
        if (gridHelper) {
          cncGroup.remove(gridHelper);
          
          // Recreate original XY grid
          const workingX = props.cncConfig.workingZoneX;
          const workingY = props.cncConfig.workingZoneY;
          const gridDivisionsX = Math.max(Math.floor(workingX / gridSpacing.value), 4);
          const gridDivisionsY = Math.max(Math.floor(workingY / gridSpacing.value), 4);
          
          const xyGridGeometry = trackResource(new THREE.BufferGeometry(), 'geometries');
          const xyGridVertices = [];
          
          // Vertical lines (parallel to Y axis)
          for (let i = 0; i <= gridDivisionsX; i++) {
            const x = (i / gridDivisionsX) * workingX;
            xyGridVertices.push(x, 0, 0);
            xyGridVertices.push(x, workingY, 0);
          }
          
          // Horizontal lines (parallel to X axis)
          for (let i = 0; i <= gridDivisionsY; i++) {
            const y = (i / gridDivisionsY) * workingY;
            xyGridVertices.push(0, y, 0);
            xyGridVertices.push(workingX, y, 0);
          }
          
          xyGridGeometry.setAttribute('position', new THREE.Float32BufferAttribute(xyGridVertices, 3));
          
          const xyGridMaterial = trackResource(new THREE.LineBasicMaterial({
            color: 0x444444,
            opacity: 0.6,
            transparent: true
          }), 'materials');
          
          gridHelper = trackResource(new THREE.LineSegments(xyGridGeometry, xyGridMaterial), 'meshes');
          gridHelper.position.set(0, 0, -1);
          cncGroup.add(gridHelper);
        }
      }
    };

    const updateLabelPositions = (viewType) => {
      // Swap physical axes geometry based on view
      swapXYAxes(viewType === 'Top');
      // Update grid to match swapped axes
      updateSwappedGrid(viewType === 'Top');
      // Update working zone to match swapped axes
      swapWorkingZone(viewType === 'Top');
      
      
      switch (viewType) {
        case '3D':
          // In 3D view, show all three axis labels in normal positions
          if (xAxisLabel && yAxisLabel) {
            // Restore normal labels if they were swapped
            cncGroup.remove(xAxisLabel);
            cncGroup.remove(yAxisLabel);
            
            // Create normal labels
            xAxisLabel = createTextSprite('X', '#ff1744');
            yAxisLabel = createTextSprite('Y', '#00e676');
            
            xAxisLabel.position.set(props.cncConfig.xAxisLength, -50, 40);
            yAxisLabel.position.set(-50, props.cncConfig.yAxisLength, 40);
            
            cncGroup.add(xAxisLabel);
            cncGroup.add(yAxisLabel);
            
            xAxisLabel.visible = true;
            yAxisLabel.visible = true;
          }
          if (zAxisLabel) {
            zAxisLabel.position.set(-50, 40, props.cncConfig.zAxisLength);
            zAxisLabel.visible = true;
          }
          break;
        case 'Top':
          // In top view - swap X and Y axes and labels to match physically swapped axes
          if (xAxisLabel && yAxisLabel) {
            // Since axes are physically swapped, labels should follow the physical positions
            cncGroup.remove(xAxisLabel);
            cncGroup.remove(yAxisLabel);
            
            // Create labels that match the swapped physical axes
            // X axis (red) should still show "X" label at its swapped position
            // Y axis (green) should still show "Y" label at its swapped position  
            const tempXLabel = createTextSprite('X', '#ff1744'); // X sprite shows "X" at swapped position
            const tempYLabel = createTextSprite('Y', '#00e676'); // Y sprite shows "Y" at swapped position
            
            // Position labels exactly where the swapped arrowheads are
            // X arrowhead is at (0, xAxisLength, 0), so X label near there
            tempXLabel.position.set(-20, props.cncConfig.xAxisLength + 20, -10); 
            // Y arrowhead is at (yAxisLength, 0, 0), so Y label near there  
            tempYLabel.position.set(props.cncConfig.yAxisLength + 20, -20, -10);
            
            cncGroup.add(tempXLabel);
            cncGroup.add(tempYLabel);
            
            // Update references
            xAxisLabel = tempXLabel;
            yAxisLabel = tempYLabel;
            
            xAxisLabel.visible = true;
            yAxisLabel.visible = true;
          }
          if (zAxisLabel) {
            // Z label near origin to indicate depth axis
            zAxisLabel.position.set(-20, -20, props.cncConfig.zAxisLength);
            zAxisLabel.visible = true;
          }
          break;
        case 'Side':
          // In side view, show only X and Z labels (front axes), hide Y label (behind)
          if (xAxisLabel && yAxisLabel) {
            // Restore normal labels if they were swapped
            cncGroup.remove(xAxisLabel);
            cncGroup.remove(yAxisLabel);
            
            // Create normal labels
            xAxisLabel = createTextSprite('X', '#ff1744');
            yAxisLabel = createTextSprite('Y', '#00e676');
            
            xAxisLabel.position.set(props.cncConfig.xAxisLength, 50, -50);
            yAxisLabel.position.set(-50, props.cncConfig.yAxisLength, 40); // Normal Y position
            
            cncGroup.add(xAxisLabel);
            cncGroup.add(yAxisLabel);
            
            xAxisLabel.visible = true;
            yAxisLabel.visible = false; // Hide Y label (behind in side view)
          }
          if (zAxisLabel) {
            zAxisLabel.position.set(-50, 50, props.cncConfig.zAxisLength);
            zAxisLabel.visible = true;
          }
          break;
      }
    };

    const setGridVisibility = (viewType) => {
      showGrid = true;
      
      switch (viewType) {
        case '3D':
          // In 3D view, no grids - presentation only
          if (gridHelper) gridHelper.visible = false;  // No XY grid
          if (fineGridHelper) fineGridHelper.visible = false; // No XZ grid
          break;
        case 'Top':
          if (gridHelper) gridHelper.visible = true;  // XY grid
          if (fineGridHelper) fineGridHelper.visible = false; // XZ grid
          break;
        case 'Side':
          if (gridHelper) gridHelper.visible = false; // XY grid
          if (fineGridHelper) fineGridHelper.visible = true; // XZ grid
          break;
        default:
          if (gridHelper) gridHelper.visible = true;  // XY grid
          if (fineGridHelper) fineGridHelper.visible = false; // XZ grid
          // Hide all axis labels when rotating/free camera
          if (xAxisLabel) xAxisLabel.visible = false;
          if (yAxisLabel) yAxisLabel.visible = false;
          if (zAxisLabel) zAxisLabel.visible = false;
      }
      
      // Update label positions and visibility based on view
      updateLabelPositions(viewType);
    };
    
    const setCameraPosition = (viewType) => {
      // FIRST: Update grid visibility and swap axes
      setGridVisibility(viewType);
      
      // THEN: Get camera properties AFTER axes are in correct positions
      const cameraProps = getCameraPropertiesForView(viewType);
      const center = cameraProps.center;
      const distance = cameraProps.distance;
      const bounds = cameraProps.bounds;
      
      let targetPosition;
      
      switch (viewType) {
        case '3D':
          // Isometric 3D view - use cached bounding box
          const isoDistance = distance; // Use the calculated optimal distance
          const boxCenter3D = center.vector;
          const boxCenterX = boxCenter3D.x;
          const boxCenterY = boxCenter3D.y;
          const boxCenterZ = boxCenter3D.z;
          
          // Position camera diagonally but ensure Z-axis appears vertical
          targetPosition = new THREE.Vector3(
            boxCenterX - isoDistance * 0.7,  // Diagonal position
            boxCenterY - isoDistance * 0.7,  // Diagonal position
            boxCenterZ                        // Same Z height as center (horizontal view)
          );
          // Look at the center of the working zone
          const lookAtPoint = new THREE.Vector3(
            boxCenterX,
            boxCenterY,
            boxCenterZ
          );
          
          // Use custom transition that sets the camera up vector to ensure Z appears vertical
          const startPosition = camera.position.clone();
          const startQuaternion = camera.quaternion.clone();
          
          // Set camera up vector to align with world Z-axis
          camera.up.set(0, 0, 1);
          camera.position.copy(targetPosition);
          camera.lookAt(lookAtPoint);
          
          const targetQuaternion = camera.quaternion.clone();
          camera.position.copy(startPosition);
          camera.quaternion.copy(startQuaternion);
          
          
          smoothCameraTransition(targetPosition, lookAtPoint, 600);
          break;
        case 'Top':
          // Top view - use cached bounding box (with swapped dimensions)
          const boxCenterTop = center.vector;
          const topDistance = distance; // Use the calculated optimal distance
          
          // Position camera below the bounding box center looking up so Z axis points to background
          // Position just below the minimum Z of the bounding box
          // This ensures we see the XY plane (at Z=0) from below
          const cameraZ = bounds.min.z - topDistance;
          targetPosition = new THREE.Vector3(boxCenterTop.x, boxCenterTop.y, cameraZ);
          
          // Custom transition that respects camera.up from the start
          const startPositionTop = camera.position.clone();
          const startQuaternionTop = camera.quaternion.clone();
          
          // Create target quaternion with the up vector we want
          const tempCamera = new THREE.PerspectiveCamera();
          tempCamera.up.set(0, 0, 1); // Set up vector BEFORE positioning (Z-up so Z points to background)
          tempCamera.position.copy(targetPosition);
          tempCamera.lookAt(boxCenterTop);
          const targetQuaternionTop = tempCamera.quaternion.clone();
          
          const startTime = Date.now();
          
          const topTransition = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / 600, 1);
            const easedProgress = progress < 0.5 ? 4 * progress * progress * progress : 1 - Math.pow(-2 * progress + 2, 3) / 2;
            
            camera.position.lerpVectors(startPositionTop, targetPosition, easedProgress);
            camera.quaternion.slerpQuaternions(startQuaternionTop, targetQuaternionTop, easedProgress);
            markDirty('rendering');
            
            if (progress < 1) {
              requestAnimationFrame(topTransition);
            } else {
              markDirty('rendering');
            }
          };
          
          requestAnimationFrame(topTransition);
          break;
        case 'Side':
          // Side view - use cached bounding box for accurate framing
          const sideDistance = distance; // Use the calculated optimal distance
          targetPosition = new THREE.Vector3(center.x, -sideDistance, center.z);
          
          // Set camera up vector to align with world Z-axis for proper side view orientation
          camera.up.set(0, 0, 1);
          
          smoothCameraTransition(targetPosition, center.vector, 600);
          break;
        default:
          targetPosition = new THREE.Vector3(center.x, center.y, distance);
          smoothCameraTransition(targetPosition, new THREE.Vector3(center.x, center.y, 0), 600);
      }
      
      markDirty('rendering');
    };
    
    const resetCamera = () => {
      setCameraPosition(currentCameraView.value);
    };
    
    const switchCameraView = () => {
      const previousView = currentCameraView.value;
      currentCameraIndex.value = (currentCameraIndex.value + 1) % cameraViews.value.length;
      const newView = currentCameraView.value;
      
      
      // Clear cache to force recalculation for new view
      clearBoundingBoxCache();
      
      // Handle 3D view rotation transitions
      if (cncGroup) {
        if (previousView === '3D' && newView !== '3D') {
          // Leaving 3D view: Apply -180° to undo the rotation
          const centerX = props.cncConfig.xAxisLength / 2;
          const centerY = props.cncConfig.yAxisLength / 2;
          const centerZ = props.cncConfig.zAxisLength / 2;
          
          const rotationMatrix = new THREE.Matrix4();
          const translationToOrigin = new THREE.Matrix4().makeTranslation(-centerX, -centerY, -centerZ);
          const translationBack = new THREE.Matrix4().makeTranslation(centerX, centerY, centerZ);
          const rotationZ = new THREE.Matrix4().makeRotationZ(-Math.PI); // -180 degrees
          
          rotationMatrix.multiplyMatrices(translationBack, rotationZ);
          rotationMatrix.multiply(translationToOrigin);
          cncGroup.applyMatrix4(rotationMatrix);
        } else if (previousView !== '3D' && newView === '3D') {
          // Entering 3D view: Apply +180° rotation
          const centerX = props.cncConfig.xAxisLength / 2;
          const centerY = props.cncConfig.yAxisLength / 2;
          const centerZ = props.cncConfig.zAxisLength / 2;
          
          const rotationMatrix = new THREE.Matrix4();
          const translationToOrigin = new THREE.Matrix4().makeTranslation(-centerX, -centerY, -centerZ);
          const translationBack = new THREE.Matrix4().makeTranslation(centerX, centerY, centerZ);
          const rotationZ = new THREE.Matrix4().makeRotationZ(Math.PI); // +180 degrees
          
          rotationMatrix.multiplyMatrices(translationBack, rotationZ);
          rotationMatrix.multiply(translationToOrigin);
          cncGroup.applyMatrix4(rotationMatrix);
        }
      }
      
      setCameraPosition(newView);
      
      // Update bounding box visualization immediately (axes are now in correct positions)
      if (showBoundingBox.value) {
        createBoundingBoxVisualization();
        logger.info(`Bounding box updated after axis swapping for view change: ${previousView} → ${newView}`);
      }
      
      // Always run verification when view changes (even if debug box is off) to catch issues
      const bounds = getBoundingBoxForView(newView);
      if (bounds) {
        verifyBoundingBoxContainsAxes(bounds, newView);
      }
    };
    
    // UI Interaction Functions
    const syncToRealCNCPosition = () => {
      if (!toolHead) return;
      
      logger.info('Syncing to real CNC position:', props.currentPos);
      
      // Force update tool head position to real position
      const visualPosition = getVisualPosition(props.currentPos);
      toolHead.position.set(visualPosition.x, visualPosition.y, visualPosition.z);
      
      // Force update display position to real position
      displayPosition.value.x = props.currentPos.x;
      displayPosition.value.y = props.currentPos.y;
      displayPosition.value.z = props.currentPos.z;
      
      // Update cached values to match real position (this prevents animation loop from overriding)
      cachedValues.lastToolPosition.x = props.currentPos.x;
      cachedValues.lastToolPosition.y = props.currentPos.y;
      cachedValues.lastToolPosition.z = props.currentPos.z;
      cachedValues.lastDisplayPosition.x = props.currentPos.x;
      cachedValues.lastDisplayPosition.y = props.currentPos.y;
      cachedValues.lastDisplayPosition.z = props.currentPos.z;
      
      // Force immediate render to show the position change
      markDirty('rendering');
      logger.info('Real CNC position restored after simulation exit');
    };
    
    const clearSimulationState = () => {
      targetPosition.value = null;
      targetArrived.value = false;
      lastTargetPosition.value = null;
      movementStartTime.value = null;
      cachedValues.movementProgress = 0;
      cachedValues.lastTargetPosition = null;
      hideClickTarget();
    };
    
    const toggleSimulationMode = () => {
      isSimulationMode.value = !isSimulationMode.value;
      logger.info(`Simulation mode ${isSimulationMode.value ? 'enabled' : 'disabled'}`);
      
      // Clear partial clicks when switching modes
      clearPartialClicks();
      
      // When exiting simulation mode, sync back to real CNC position
      if (!isSimulationMode.value) {
        syncToRealCNCPosition();
        clearSimulationState();
        // Notify parent to reset simulated position to real position
        emit('simulationModeChanged', { isSimulationMode: false, realPosition: props.currentPos });
      } else {
        emit('simulationModeChanged', { isSimulationMode: true });
      }
    };
    
    const toggleWorkingZone = () => {
      showWorkingZone.value = !showWorkingZone.value;
      if (workingZoneMesh) {
        workingZoneMesh.visible = showWorkingZone.value;
        markDirty('rendering');
      }
    };
    
    const regenerateGrids = () => {
      if (!cncGroup) return;
      
      // Remove existing grids
      if (gridHelper) {
        cncGroup.remove(gridHelper);
        gridHelper = null;
      }
      if (fineGridHelper) {
        cncGroup.remove(fineGridHelper);
        fineGridHelper = null;
      }
      
      // Recreate grids with new spacing
      if (props.cncConfig.selectedAxes?.x === true && props.cncConfig.selectedAxes?.y === true) {
        createGrid('xy');
      }
      if (props.cncConfig.selectedAxes?.x === true && props.cncConfig.selectedAxes?.z === true) {
        createGrid('xz');
      }
      
      // Update grid visibility based on current view
      setGridVisibility(currentCameraView.value);
      markDirty('rendering');
    };

    const getBoundingBoxForView = (viewType = null) => {
      // Use current view type if not provided
      const currentView = viewType || currentCameraView.value;
      
      // Return cached box if it's for the same view
      if (cachedBoundingBox && lastBoundingBoxViewType === currentView) {
        return cachedBoundingBox;
      }
      
      // Get the actual axis lengths from configuration (only for selected axes)
      let axisX = props.cncConfig.selectedAxes?.x === true ? props.cncConfig.xAxisLength : 0;
      let axisY = props.cncConfig.selectedAxes?.y === true ? props.cncConfig.yAxisLength : 0;
      const axisZ = props.cncConfig.selectedAxes?.z === true ? props.cncConfig.zAxisLength : 0;
      
      // Get working zone dimensions using centralized utility
      const bounds = getWorkingZoneBounds(props.cncConfig, false);
      let { x: workingX, y: workingY, z: workingZ } = bounds;
      
      // In Top view, X and Y axes are swapped, so swap their dimensions too
      if (currentView === 'Top') {
        // Swap X and Y dimensions to match the swapped axes
        [axisX, axisY] = [axisY, axisX];
      }
      
      // Calculate the maximum extent in each direction (with minimums for unselected axes)
      const maxX = Math.max(axisX, workingX, 10); // Minimum 10mm for visualization
      const maxY = Math.max(axisY, workingY, 10); // Minimum 10mm for visualization
      const maxZ = Math.max(axisZ, workingZ, 10); // Minimum 10mm for visualization
      
      // Small uniform margin around the axes
      const uniformMargin = 20;
      
      
      // Create bounding box that closely matches the axes with small uniform margin
      const currentBounds = new THREE.Box3(
        new THREE.Vector3(
          -uniformMargin,     // Small negative space for origin
          -uniformMargin,     // Small negative space for origin
          -uniformMargin      // Small negative space for origin
        ),
        new THREE.Vector3(
          maxX + uniformMargin,  // Axis length plus small margin
          maxY + uniformMargin,  // Axis length plus small margin
          maxZ + uniformMargin   // Axis length plus small margin
        )
      );
      
      
      // Cache the result
      cachedBoundingBox = currentBounds;
      lastBoundingBoxViewType = currentView;
      
      return currentBounds;
    };
    
    // Function to verify if bounding box correctly contains all axes
    const verifyBoundingBoxContainsAxes = (bounds, viewType) => {
      if (!xAxisMesh || !yAxisMesh || !zAxisMesh || !xArrowMesh || !yArrowMesh || !zArrowMesh) {
        return { valid: false, reason: 'Axes not initialized' };
      }
      
      // Get actual axis endpoint positions (where arrows are)
      const xAxisEnd = { x: xArrowMesh.position.x, y: xArrowMesh.position.y, z: xArrowMesh.position.z };
      const yAxisEnd = { x: yArrowMesh.position.x, y: yArrowMesh.position.y, z: yArrowMesh.position.z };
      const zAxisEnd = { x: zArrowMesh.position.x, y: zArrowMesh.position.y, z: zArrowMesh.position.z };
      
      // Check if all axis endpoints are within the bounding box
      const xInside = xAxisEnd.x >= bounds.min.x && xAxisEnd.x <= bounds.max.x &&
                     xAxisEnd.y >= bounds.min.y && xAxisEnd.y <= bounds.max.y &&
                     xAxisEnd.z >= bounds.min.z && xAxisEnd.z <= bounds.max.z;
      
      const yInside = yAxisEnd.x >= bounds.min.x && yAxisEnd.x <= bounds.max.x &&
                     yAxisEnd.y >= bounds.min.y && yAxisEnd.y <= bounds.max.y &&
                     yAxisEnd.z >= bounds.min.z && yAxisEnd.z <= bounds.max.z;
      
      const zInside = zAxisEnd.x >= bounds.min.x && zAxisEnd.x <= bounds.max.x &&
                     zAxisEnd.y >= bounds.min.y && zAxisEnd.y <= bounds.max.y &&
                     zAxisEnd.z >= bounds.min.z && zAxisEnd.z <= bounds.max.z;
      
      const allInside = xInside && yInside && zInside;
      
      logger.info(`${viewType} View Bounding Box Verification:`, {
        boundingBox: { 
          min: { x: bounds.min.x, y: bounds.min.y, z: bounds.min.z },
          max: { x: bounds.max.x, y: bounds.max.y, z: bounds.max.z },
          size: { x: bounds.max.x - bounds.min.x, y: bounds.max.y - bounds.min.y, z: bounds.max.z - bounds.min.z }
        },
        axisEndpoints: { xAxisEnd, yAxisEnd, zAxisEnd },
        containment: { xInside, yInside, zInside },
        result: allInside ? '✅ CORRECT' : '❌ WRONG'
      });
      
      return { valid: allInside, xInside, yInside, zInside };
    };
    
    // Function to clear cache when configuration changes
    const clearBoundingBoxCache = () => {
      cachedBoundingBox = null;
      lastBoundingBoxViewType = null;
    };

    const createBoundingBoxVisualization = () => {
      // Remove existing visualization if it exists
      if (boundingBoxMesh) {
        scene.remove(boundingBoxMesh);
        boundingBoxMesh = null;
      }
      
      // Get current cached bounding box for current view
      const currentBounds = getBoundingBoxForView(currentCameraView.value);
      
      // Get bounding box dimensions
      const size = new THREE.Vector3();
      currentBounds.getSize(size);
      const center = new THREE.Vector3();
      currentBounds.getCenter(center);
      
      // Create box geometry with bounding box dimensions
      const boxGeometry = createTrackedGeometry(THREE.BoxGeometry, size.x, size.y, size.z);
      const edgesGeometry = trackResource(new THREE.EdgesGeometry(boxGeometry), 'geometries');
      
      // Create material with distinctive debug color
      const boxMaterial = createTrackedMaterial(THREE.LineBasicMaterial, {
        color: 0xff00ff,  // Magenta for visibility
        opacity: 0.6,
        transparent: true,
        linewidth: 1
      });
      
      boundingBoxMesh = trackResource(new THREE.LineSegments(edgesGeometry, boxMaterial), 'meshes');
      boundingBoxMesh.position.copy(center);
      boundingBoxMesh.visible = showBoundingBox.value;
      
      scene.add(boundingBoxMesh); // Add to scene, not cncGroup, so it doesn't rotate
      
      // Debug: Verify if bounding box fits within margins
      if (showBoundingBox.value && camera && renderer) {
        // Project bounding box corners to screen space
        const corners = [
          new THREE.Vector3(currentBounds.min.x, currentBounds.min.y, currentBounds.min.z),
          new THREE.Vector3(currentBounds.max.x, currentBounds.min.y, currentBounds.min.z),
          new THREE.Vector3(currentBounds.min.x, currentBounds.max.y, currentBounds.min.z),
          new THREE.Vector3(currentBounds.max.x, currentBounds.max.y, currentBounds.min.z),
          new THREE.Vector3(currentBounds.min.x, currentBounds.min.y, currentBounds.max.z),
          new THREE.Vector3(currentBounds.max.x, currentBounds.min.y, currentBounds.max.z),
          new THREE.Vector3(currentBounds.min.x, currentBounds.max.y, currentBounds.max.z),
          new THREE.Vector3(currentBounds.max.x, currentBounds.max.y, currentBounds.max.z)
        ];

        let minScreenX = Infinity, maxScreenX = -Infinity;
        let minScreenY = Infinity, maxScreenY = -Infinity;

        corners.forEach(corner => {
          const screenPos = corner.clone().project(camera);
          const x = (screenPos.x * 0.5 + 0.5) * renderer.domElement.width;
          const y = (1 - (screenPos.y * 0.5 + 0.5)) * renderer.domElement.height;
          
          minScreenX = Math.min(minScreenX, x);
          maxScreenX = Math.max(maxScreenX, x);
          minScreenY = Math.min(minScreenY, y);
          maxScreenY = Math.max(maxScreenY, y);
        });

        const marginPixels = window.debugBoundingBoxCalc?.marginPixels || 19;
        const exceedsLeft = minScreenX < marginPixels;
        const exceedsRight = maxScreenX > (renderer.domElement.width - marginPixels);
        const exceedsTop = minScreenY < marginPixels;
        const exceedsBottom = maxScreenY > (renderer.domElement.height - marginPixels);
        
        const exceeds = exceedsLeft || exceedsRight || exceedsTop || exceedsBottom;
      }
      
      // Verify if the bounding box correctly contains all axes
      verifyBoundingBoxContainsAxes(currentBounds, currentCameraView.value);
    };

    const toggleBoundingBox = () => {
      showBoundingBox.value = !showBoundingBox.value;
      
      if (showBoundingBox.value) {
        // Always recreate visualization to ensure it's up to date
        createBoundingBoxVisualization();
      } else {
        // Hide visualization
        if (boundingBoxMesh) {
          boundingBoxMesh.visible = false;
        }
      }
      
      markDirty('rendering');
    };
    
    const closeViewer = () => {
      emit('close');
    };
    
    // Window Resize Handler with error handling
    const onWindowResize = () => {
      try {
        if (!threeContainer.value || !camera || !renderer) {
          logger.warn('Resize skipped: required components not available');
          return;
        }
        
        const width = threeContainer.value.clientWidth || 800;
        const height = threeContainer.value.clientHeight || 600;
        
        if (width <= 0 || height <= 0) {
          logger.warn('Resize skipped: invalid dimensions', { width, height });
          return;
        }
        
        const newAspect = width / height;
        if (!isFinite(newAspect) || newAspect <= 0) {
          logger.warn('Resize skipped: invalid aspect ratio', { newAspect });
          return;
        }
        
        camera.aspect = newAspect;
        camera.updateProjectionMatrix();
        
        // Handle potential WebGL context issues during resize
        const gl = renderer.getContext();
        if (!gl || gl.isContextLost()) {
          logger.warn('WebGL context lost during resize');
          return;
        }
        
        renderer.setSize(width, height);
        markDirty('rendering');
        
      } catch (error) {
        logger.error('Error during window resize:', error);
        
        // Don't throw error to prevent page crash, just log it
        webglError.value = 'resize-error';
        errorMessage.value = 'Error occurred during window resize. 3D viewer may not display correctly.';
      }
    };
    
    // Canvas and Context Validation
    const validateCanvas = () => {
      if (!threeContainer.value) {
        throw new Error('Three.js container element not found');
      }
      
      const containerRect = threeContainer.value.getBoundingClientRect();
      if (containerRect.width <= 0 || containerRect.height <= 0) {
        throw new Error('Three.js container has invalid dimensions');
      }
      
      logger.info('Canvas validation passed', {
        width: containerRect.width,
        height: containerRect.height
      });
      
      return true;
    };
    
    // Lifecycle Management Functions
    const initializeViewer = () => {
      try {
        validateCanvas();
        initThreeJS();
        
        // Immediately update bounding box after full initialization
        nextTick(() => {
          if (showBoundingBox.value && boundingBoxMesh) {
            createBoundingBoxVisualization();
            logger.info('Bounding box calculated immediately after initialization');
          }
        });
        
        window.addEventListener('resize', onWindowResize);
      } catch (error) {
        logger.error('Failed to initialize viewer:', error);
        webglError.value = 'initialization-failed';
        errorMessage.value = `Failed to initialize 3D viewer: ${error.message}`;
      }
    };
    
    const stopAnimationLoop = () => {
      try {
        isAnimating.value = false;
        if (animationId) {
          cancelAnimationFrame(animationId);
          animationId = null;
        }
        logger.info('Animation loop stopped');
      } catch (error) {
        logger.error('Error stopping animation loop:', error);
      }
    };
    
    const removeEventListeners = () => {
      try {
        if (renderer?.domElement) {
          const events = ['mousedown', 'mouseup', 'mousemove', 'contextmenu', 'wheel', 'webglcontextlost', 'webglcontextrestored'];
          events.forEach(eventType => {
            try {
              // Note: We can't remove specific listeners without references, but this is mainly for cleanup
              // The WebGL context events are handled during renderer disposal
            } catch (eventError) {
              logger.warn(`Error removing ${eventType} listener:`, eventError);
            }
          });
        }
        window.removeEventListener('resize', onWindowResize);
      } catch (error) {
        logger.error('Error removing event listeners:', error);
      }
    };
    
    const cleanupViewer = () => {
      try {
        logger.info('Starting CNC 3D Viewer cleanup...');
        
        stopAnimationLoop();
        removeEventListeners();
        
        // Cleanup mouse performance optimizations
        if (mouseAnimationFrame) {
          cancelAnimationFrame(mouseAnimationFrame);
          mouseAnimationFrame = null;
        }
        pendingMouseUpdate = null;
        
        
        disposeAllResources();
        
        // Reset state
        isInitialized.value = false;
        webglError.value = null;
        errorMessage.value = '';
        
        logger.info('CNC 3D Viewer disposed completely - all resources cleaned up');
      } catch (error) {
        logger.error('Error during viewer cleanup:', error);
        
        // Ensure we still reset critical state even if cleanup fails
        isAnimating.value = false;
        isInitialized.value = false;
      }
    };
    
    const handlePositionWatch = (newPos) => {
      // Position updates are handled automatically in the animation loop
      // No additional dirty flag marking needed as the animation loop
      // continuously checks for position changes using cached values
    };
    
    // Lifecycle
    onMounted(initializeViewer);
    onUnmounted(cleanupViewer);
    
    // Watch for position changes
    watch(() => props.currentPos, handlePositionWatch, { deep: true });
    
    
    // Watch for CNC connection changes and clear partial clicks when disconnected
    watch(() => props.isCncConnected, (newConnected, oldConnected) => {
      if (oldConnected && !newConnected) {
        // CNC disconnected, clear any partial clicks
        clearPartialClicks();
        logger.info('CNC disconnected: cleared partial clicks');
      }
    });
    
    // Watch for camera views changes and adjust current index
    watch(cameraViews, (newViews) => {
      // Ensure current index is within bounds
      if (currentCameraIndex.value >= newViews.length) {
        currentCameraIndex.value = 0; // Reset to first view
        logger.info(`Camera view reset to ${newViews[0]} due to view count change`);
      }
    });

    
    return {
      threeContainer,
      isAnimating,
      showWorkingZone,
      showBoundingBox,
      gridSpacing,
      mouseTooltip,
      mouseTooltipStyle,
      currentCameraView,
      resetCamera,
      toggleWorkingZone,
      toggleBoundingBox,
      regenerateGrids,
      switchCameraView,
      toggleSimulationMode,
      closeViewer,
      canClickToMove,
      clickStatusClass,
      clickStatusText,
      isSimulationMode,
      displayPosition,
      targetPosition,
      targetArrived,
      lastTargetPosition,
      currentPos: props.currentPos,
      canExecuteSimulation,
      isCncMoving,
      executeSimulation,
      completeRealCNCMovement,
      webglError,
      errorMessage,
      hasWebglSupport,
      isInitialized,
      retryInitialization,
      // Axis display computed properties
      selectedLinearAxes,
      selectedAxesDisplay,
      axisLengthsDisplay,
      workZoneDisplay,
      
      // Click state tracking for 3-axis systems
      topViewClicked,
      sideViewClicked,
      topViewPosition,
      sideViewPosition,
      cameraViews,
      // Utilities
      formatCoordinate
    };
  }
};
</script>

<style scoped>
.viewer-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: var(--color-bg-primary);
  z-index: 2000;
  display: flex;
  flex-direction: column;
}

.viewer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4);
  padding-right: var(--space-8); /* Just a little extra padding on the right */
  background-color: var(--color-bg-secondary);
  border-bottom: var(--border-width-1) solid var(--color-border-secondary);
}

.viewer-header h2 {
  margin: 0;
  color: var(--color-text-primary);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
}

.viewer-controls {
  display: flex;
  gap: var(--space-3);
  align-items: center;
}

.control-button,
.close-button {
  padding: var(--space-2) var(--space-3);
  border: var(--border-width-1) solid var(--color-border-secondary);
  border-radius: var(--border-radius-base);
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-primary);
  cursor: pointer;
  font-size: var(--font-size-sm);
  display: flex;
  align-items: center;
  gap: var(--space-1);
  min-height: var(--touch-target-min);
  transition: var(--transition-hover);
}

.control-button:hover {
  background-color: var(--color-bg-quaternary);
  border-color: var(--color-primary);
}

.close-button {
  background-color: var(--color-danger);
  color: var(--color-text-on-primary);
  border-color: var(--color-danger);
}

.close-button:hover {
  background-color: var(--color-danger-dark);
}

.viewer-content {
  flex: 1;
  display: flex;
  position: relative;
}

.three-container {
  flex: 1;
  background-color: var(--color-bg-tertiary);
  position: relative;
}

.three-container.debug-border {
  box-shadow: inset 0 0 0 3px rgba(255, 0, 0, 0.5);
}

.mouse-tooltip {
  position: absolute;
  background-color: rgba(0, 0, 0, 0.85);
  border: 1px solid rgba(0, 255, 0, 0.5);
  border-radius: 4px;
  padding: 6px 10px;
  pointer-events: none;
  z-index: 1000;
  font-family: monospace;
  font-size: 12px;
  white-space: nowrap;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.mouse-tooltip .tooltip-content {
  display: flex;
  gap: 12px;
  color: #fff;
}

.mouse-tooltip .coord-x {
  color: #ff6b6b;
}

.mouse-tooltip .coord-y {
  color: #51cf66;
}

.mouse-tooltip .coord-z {
  color: #339af0;
}

.debug-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 10;
}

.margin-visualization {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border: 2px dashed rgba(0, 255, 0, 0.5);
  /* 0.5cm margins - approximately 19px at 96 DPI (0.5 * 96 / 2.54) */
  margin: 19px;
}

.margin-visualization::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  border: 1px solid rgba(0, 255, 0, 0.2);
}

.margin-info {
  position: absolute;
  top: -25px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.8);
  color: #00ff00;
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 12px;
  font-family: monospace;
  white-space: nowrap;
}

.info-panel {
  width: 380px !important;
  background-color: var(--color-bg-secondary);
  border-left: var(--border-width-1) solid var(--color-border-secondary);
  padding: var(--space-5);
  padding-right: var(--space-6); /* Extra space from scrollbar */
  overflow-y: auto;
}

.grid-settings {
  margin-bottom: var(--space-6);
  max-width: 320px;
  margin-left: auto;
  margin-right: auto;
  padding-bottom: var(--space-4);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.grid-settings h4 {
  margin: 0 0 var(--space-3) 0;
  color: var(--color-primary);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-bold);
}

.grid-spacing-control {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.grid-spacing-control label {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  white-space: nowrap;
  font-weight: var(--font-weight-medium);
}

.grid-spacing-input {
  width: 70px;
  padding: var(--space-2);
  background-color: var(--color-bg-tertiary);
  border: 1px solid var(--color-border-secondary);
  border-radius: var(--border-radius-base);
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
  text-align: center;
}

.grid-spacing-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(var(--color-primary-rgb), 0.2);
}

.grid-spacing-control .unit {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.position-info,
.target-info,
.config-info {
  margin-bottom: var(--space-6);
  max-width: 320px; /* More width for content */
  margin-left: auto;
  margin-right: auto; /* Center the content blocks */
}

.position-info h4,
.target-info h4,
.config-info h4 {
  margin: 0 0 var(--space-3) 0;
  color: var(--color-primary);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-bold);
}

.target-info h4 {
  color: var(--color-warning);
}

.position-row,
.config-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3);
  padding: var(--space-3);
  background-color: var(--color-bg-tertiary);
  border-radius: var(--border-radius-base);
  min-height: 36px;
}

.axis,
.label {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.value {
  font-family: var(--font-family-mono);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
  white-space: nowrap;
}

.value.target {
  color: var(--color-warning);
  background-color: rgba(255, 193, 7, 0.1);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--border-radius-base);
  border: 1px solid var(--color-warning);
}

.value.target.arrived {
  color: var(--color-success);
  background-color: rgba(40, 167, 69, 0.1);
  border: 1px solid var(--color-success);
}


/* Axis Legend Box */
.axis-legend {
  position: absolute;
  top: 16px;
  left: 16px;
  background-color: rgba(26, 26, 26, 0.9);
  border: 1px solid var(--color-border-secondary);
  border-radius: var(--border-radius-base);
  padding: var(--space-3);
  backdrop-filter: blur(4px);
  z-index: 100;
  min-width: 100px;
}

.legend-title {
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
  margin-bottom: var(--space-2);
  text-align: center;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-1);
}

.legend-item:last-child {
  margin-bottom: 0;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 2px;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.x-color {
  background-color: #ff3333;
}

.y-color {
  background-color: #33ff33;
}

.z-color {
  background-color: #0000ff;
}

.legend-label {
  color: var(--color-text-primary);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
}

.legend-divider {
  width: 100%;
  height: 1px;
  background-color: rgba(255, 255, 255, 0.2);
  margin: var(--space-2) 0;
}

.click-status .legend-label {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-bold);
}

.status-enabled {
  background-color: #00ff00 !important;
  box-shadow: 0 0 4px #00ff00;
}

.status-disabled {
  background-color: #ff4444 !important;
}

/* Simulation Button Styles */
.simulation-button {
  transition: all 0.3s ease;
}

.simulation-button.simulation-active {
  background-color: var(--color-warning) !important;
  color: var(--color-text-on-primary) !important;
  border-color: var(--color-warning-dark) !important;
  box-shadow: 0 0 8px rgba(255, 193, 7, 0.4);
}

.simulation-button.simulation-active:hover {
  background-color: var(--color-warning-dark) !important;
  transform: translateY(-1px);
  box-shadow: 0 0 12px rgba(255, 193, 7, 0.6);
}

.simulation-button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  background-color: var(--color-bg-tertiary) !important;
}

/* Debug Button Styles */
.debug-button {
  transition: all 0.3s ease;
}

.debug-button.debug-active {
  background-color: #ff00ff !important; /* Magenta to match bounding box */
  color: white !important;
  border-color: #cc00cc !important;
  box-shadow: 0 0 8px rgba(255, 0, 255, 0.4);
}

.debug-button.debug-active:hover {
  background-color: #cc00cc !important;
  transform: translateY(-1px);
  box-shadow: 0 0 12px rgba(255, 0, 255, 0.6);
}

/* Play Button Styles */
.play-button {
  transition: all 0.3s ease;
}

.play-button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  background-color: var(--color-bg-tertiary) !important;
  color: var(--color-text-disabled) !important;
  border-color: var(--color-border-secondary) !important;
}

.play-button.play-active {
  background-color: var(--color-success) !important;
  color: var(--color-text-on-primary) !important;
  border-color: var(--color-success-dark) !important;
  box-shadow: 0 0 8px rgba(40, 167, 69, 0.4);
}

.play-button.play-active:hover:not(:disabled) {
  background-color: var(--color-success-dark) !important;
  transform: translateY(-1px);
}

/* WebGL Error Handling Styles */
.webgl-error-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-bg-tertiary);
  padding: var(--space-8);
}

.error-content {
  max-width: 600px;
  text-align: center;
  background-color: var(--color-bg-secondary);
  border: 2px solid var(--color-danger);
  border-radius: var(--border-radius-lg);
  padding: var(--space-6);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.error-icon {
  font-size: 3rem;
  color: var(--color-danger);
  margin-bottom: var(--space-4);
}

.error-title {
  color: var(--color-text-primary);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  margin: 0 0 var(--space-3) 0;
}

.error-message {
  color: var(--color-text-secondary);
  font-size: var(--font-size-base);
  line-height: 1.5;
  margin: 0 0 var(--space-4) 0;
}

.error-actions {
  margin-bottom: var(--space-4);
}

.retry-button {
  padding: var(--space-3) var(--space-4);
  background-color: var(--color-primary);
  color: var(--color-text-on-primary);
  border: none;
  border-radius: var(--border-radius-base);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  transition: var(--transition-hover);
  margin-bottom: var(--space-4);
}

.retry-button:hover {
  background-color: var(--color-primary-dark);
  transform: translateY(-1px);
}

.troubleshooting {
  text-align: left;
  background-color: var(--color-bg-tertiary);
  border-radius: var(--border-radius-base);
  padding: var(--space-4);
  margin-top: var(--space-4);
}

.troubleshooting h4 {
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-bold);
  margin: 0 0 var(--space-2) 0;
}

.troubleshooting ul {
  margin: 0;
  padding-left: var(--space-4);
  color: var(--color-text-secondary);
}

.troubleshooting li {
  margin-bottom: var(--space-1);
  line-height: 1.4;
}

.fallback-info {
  background-color: var(--color-bg-tertiary);
  border-radius: var(--border-radius-base);
  padding: var(--space-4);
  margin-top: var(--space-4);
}

.fallback-info h4 {
  color: var(--color-primary);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-bold);
  margin: 0 0 var(--space-3) 0;
  text-align: center;
}

.fallback-position {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.fallback-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--color-bg-secondary);
  padding: var(--space-2);
  border-radius: var(--border-radius-base);
}

.fallback-row .axis {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
}

.fallback-row .value {
  font-family: var(--font-family-mono);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

/* Loading Indicator */
.loading-container {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(26, 26, 26, 0.8);
  z-index: 1000;
}

.loading-content {
  text-align: center;
  color: var(--color-text-primary);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--color-border-secondary);
  border-top: 4px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto var(--space-3) auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-content p {
  margin: 0;
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
}

</style>