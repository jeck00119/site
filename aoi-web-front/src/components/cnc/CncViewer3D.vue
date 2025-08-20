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
        <button @click="switchCameraView" class="control-button">
          <font-awesome-icon icon="eye" />
          {{ currentCameraView }}
        </button>
        <button @click="toggleSimulationMode" class="control-button simulation-button" :class="{ 'simulation-active': isSimulationMode }">
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
                <span class="value">{{ displayPosition.x.toFixed(3) }}mm</span>
              </div>
              <div class="fallback-row">
                <span class="axis">Y:</span>
                <span class="value">{{ displayPosition.y.toFixed(3) }}mm</span>
              </div>
              <div class="fallback-row">
                <span class="axis">Z:</span>
                <span class="value">{{ displayPosition.z.toFixed(3) }}mm</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Normal 3D Container -->
      <div v-else class="three-container" ref="threeContainer">
        <!-- Loading indicator -->
        <div v-if="!isInitialized" class="loading-container">
          <div class="loading-content">
            <div class="loading-spinner"></div>
            <p>Initializing 3D Viewer...</p>
          </div>
        </div>
        
        <!-- Fixed axis legend in top-left corner -->
        <div v-if="isInitialized" class="axis-legend">
          <div class="legend-title">Axes</div>
          <div class="legend-item">
            <div class="legend-color x-color"></div>
            <span class="legend-label">X-Axis</span>
          </div>
          <div class="legend-item">
            <div class="legend-color y-color"></div>
            <span class="legend-label">Y-Axis</span>
          </div>
          <div class="legend-item">
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
          <div v-if="cncConfig.selectedAxes?.x !== false" class="position-row">
            <span class="axis">X:</span>
            <span class="value">{{ displayPosition.x.toFixed(3) }}mm</span>
          </div>
          <div v-if="cncConfig.selectedAxes?.y !== false" class="position-row">
            <span class="axis">Y:</span>
            <span class="value">{{ displayPosition.y.toFixed(3) }}mm</span>
          </div>
          <div v-if="cncConfig.selectedAxes?.z !== false" class="position-row">
            <span class="axis">Z:</span>
            <span class="value">{{ displayPosition.z.toFixed(3) }}mm</span>
          </div>
        </div>
        
        <div class="target-info" v-if="targetPosition || (targetArrived && lastTargetPosition)">
          <h4>Target Position</h4>
          <div v-if="targetArrived && lastTargetPosition">
            <div v-if="cncConfig.selectedAxes?.x !== false" class="position-row">
              <span class="axis">X:</span>
              <span class="value target arrived">{{ lastTargetPosition.x?.toFixed(3) || '0.000' }}mm</span>
            </div>
            <div v-if="cncConfig.selectedAxes?.y !== false" class="position-row">
              <span class="axis">Y:</span>
              <span class="value target arrived">{{ lastTargetPosition.y?.toFixed(3) || '0.000' }}mm</span>
            </div>
            <div v-if="cncConfig.selectedAxes?.z !== false" class="position-row">
              <span class="axis">Z:</span>
              <span class="value target arrived">{{ lastTargetPosition.z?.toFixed(3) || '0.000' }}mm</span>
            </div>
          </div>
          <div v-else-if="targetPosition">
            <div v-if="cncConfig.selectedAxes?.x !== false" class="position-row">
              <span class="axis">X:</span>
              <span class="value target">{{ targetPosition.x?.toFixed(3) || '0.000' }}mm</span>
            </div>
            <div v-if="cncConfig.selectedAxes?.y !== false" class="position-row">
              <span class="axis">Y:</span>
              <span class="value target">{{ targetPosition.y?.toFixed(3) || '0.000' }}mm</span>
            </div>
            <div v-if="cncConfig.selectedAxes?.z !== false" class="position-row">
              <span class="axis">Z:</span>
              <span class="value target">{{ targetPosition.z?.toFixed(3) || '0.000' }}mm</span>
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
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue';
import * as THREE from 'three';
import { logger } from '@/utils/logger';

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
  emits: ['close', 'moveTo', 'simulateMoveTo', 'positionUpdate', 'targetUpdate'],
  setup(props, { emit }) {
    // DOM reference - needs to be reactive for template ref
    const threeContainer = ref(null);
    
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
    let gridHelper = null;
    let fineGridHelper = null;
    let xAxisLabel = null;
    let yAxisLabel = null;
    let zAxisLabel = null;
    
    // State
    const isAnimating = ref(true);
    const showWorkingZone = ref(true); // Start visible by default
    // Internal grid state - doesn't need reactivity (not bound to template)
    let showGrid = true; // Grid visible in fixed views
    const isSimulationMode = ref(false); // Simulation mode for testing without real CNC
    
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
    
    // Camera views
    const cameraViews = ['3D', 'Top', 'Side'];
    const currentCameraIndex = ref(0);
    const currentCameraView = computed(() => cameraViews[currentCameraIndex.value]);
    
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
      if (isSimulationMode.value) {
        if (currentCameraView.value === 'Top' || currentCameraView.value === 'Side') {
          return targetPosition.value ? 'Click Play to Execute' : 'Click to Set Target';
        }
        return 'Fixed View Only';
      }
      if (!props.isCncConnected) {
        return 'CNC Disconnected';
      }
      if (currentCameraView.value === 'Top' || currentCameraView.value === 'Side') {
        return 'Click to Move';
      }
      return 'Fixed View Only';
    });
    
    // Play button state
    const canExecuteSimulation = computed(() => {
      return isSimulationMode.value && targetPosition.value && !isExecutingSimulation.value;
    });

    // Computed properties for display strings based on selected axes
    const selectedLinearAxes = computed(() => {
      const axes = [];
      if (props.cncConfig.selectedAxes?.x !== false) axes.push('X');
      if (props.cncConfig.selectedAxes?.y !== false) axes.push('Y');  
      if (props.cncConfig.selectedAxes?.z !== false) axes.push('Z');
      return axes;
    });

    const selectedAxesDisplay = computed(() => {
      return selectedLinearAxes.value.length > 0 ? selectedLinearAxes.value.join(', ') : 'None';
    });

    const axisLengthsDisplay = computed(() => {
      const lengths = [];
      if (props.cncConfig.selectedAxes?.x !== false && props.cncConfig.xAxisLength) {
        lengths.push(`X:${props.cncConfig.xAxisLength}mm`);
      }
      if (props.cncConfig.selectedAxes?.y !== false && props.cncConfig.yAxisLength) {
        lengths.push(`Y:${props.cncConfig.yAxisLength}mm`);
      }
      if (props.cncConfig.selectedAxes?.z !== false && props.cncConfig.zAxisLength) {
        lengths.push(`Z:${props.cncConfig.zAxisLength}mm`);
      }
      return lengths.join(' × ');
    });


    const workZoneDisplay = computed(() => {
      const zones = [];
      if (props.cncConfig.selectedAxes?.x !== false && props.cncConfig.workingZoneX) {
        zones.push(`X:${props.cncConfig.workingZoneX}mm`);
      }
      if (props.cncConfig.selectedAxes?.y !== false && props.cncConfig.workingZoneY) {
        zones.push(`Y:${props.cncConfig.workingZoneY}mm`);
      }
      if (props.cncConfig.selectedAxes?.z !== false && props.cncConfig.workingZoneZ) {
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
        
        setCameraPosition(currentCameraView.value);
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
        
        // Configure raycaster for better performance
        raycaster.params.Line.threshold = 0.1;
        raycaster.params.Points.threshold = 0.1;
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
        if (!props.cncConfig || !props.cncConfig.cncType) {
          throw new Error('Invalid CNC configuration');
        }
        
        try {
          switch (props.cncConfig.cncType) {
            case 'corexy':
              createCoreXYMachine();
              break;
            case 'delta':
              createDeltaMachine();
              break;
            case 'cartesian':
            default:
              createCartesianMachine();
              break;
          }
        } catch (machineError) {
          logger.error(`Error creating ${props.cncConfig.cncType} machine:`, machineError);
          // Create a basic fallback visualization
          createSimpleAxisVisualization();
        }
        
        // Working zone visualization - always create but control visibility
        try {
          createWorkingZone();
        } catch (workingZoneError) {
          logger.warn('Failed to create working zone visualization:', workingZoneError);
        }
        
        scene.add(cncGroup);
        
        logger.info(`${props.cncConfig.cncType.toUpperCase()} CNC rig 3D model created successfully`);
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
    
    const createXAxis = (materials) => {
      if (props.cncConfig.xAxisLength <= 0) return;
      
      const xAxisGeometry = createTrackedGeometry(THREE.CylinderGeometry, 2, 2, props.cncConfig.xAxisLength);
      const xAxis = createTrackedMesh(xAxisGeometry, materials.xAxis);
      xAxis.position.set(props.cncConfig.xAxisLength / 2, 0, 0);
      xAxis.rotation.z = Math.PI / 2;
      cncGroup.add(xAxis);
      
      // X-Axis arrow
      const xArrowGeometry = createTrackedGeometry(THREE.ConeGeometry, 5, 15, 8);
      const xArrow = createTrackedMesh(xArrowGeometry, materials.xAxis);
      xArrow.position.set(props.cncConfig.xAxisLength, 0, 0);
      xArrow.rotation.z = -Math.PI / 2;
      cncGroup.add(xArrow);

      // X-Axis label - initial position (will be updated by updateLabelPositions)
      xAxisLabel = createTextSprite('X', '#ff1744');
      xAxisLabel.position.set(props.cncConfig.xAxisLength, -50, 40);
      cncGroup.add(xAxisLabel);
    };
    
    const createYAxis = (materials) => {
      if (props.cncConfig.yAxisLength <= 0) return;
      
      const yAxisGeometry = createTrackedGeometry(THREE.CylinderGeometry, 2, 2, props.cncConfig.yAxisLength);
      const yAxis = createTrackedMesh(yAxisGeometry, materials.yAxis);
      yAxis.position.set(0, props.cncConfig.yAxisLength / 2, 0);
      cncGroup.add(yAxis);
      
      // Y-Axis arrow
      const yArrowGeometry = createTrackedGeometry(THREE.ConeGeometry, 5, 15, 8);
      const yArrow = createTrackedMesh(yArrowGeometry, materials.yAxis);
      yArrow.position.set(0, props.cncConfig.yAxisLength, 0);
      cncGroup.add(yArrow);

      // Y-Axis label - initial position (will be updated by updateLabelPositions)
      yAxisLabel = createTextSprite('Y', '#00e676');
      yAxisLabel.position.set(-50, props.cncConfig.yAxisLength, 40);
      cncGroup.add(yAxisLabel);
    };
    
    const createZAxis = (materials) => {
      if (props.cncConfig.zAxisLength <= 0) return;
      
      const zAxisGeometry = createTrackedGeometry(THREE.CylinderGeometry, 2, 2, props.cncConfig.zAxisLength);
      const zAxis = createTrackedMesh(zAxisGeometry, materials.zAxis);
      zAxis.position.set(0, 0, props.cncConfig.zAxisLength / 2);
      zAxis.rotation.x = Math.PI / 2;
      cncGroup.add(zAxis);
      
      // Z-Axis arrow
      const zArrowGeometry = createTrackedGeometry(THREE.ConeGeometry, 5, 15, 8);
      const zArrow = createTrackedMesh(zArrowGeometry, materials.zAxis);
      zArrow.position.set(0, 0, props.cncConfig.zAxisLength);
      zArrow.rotation.x = Math.PI / 2;
      cncGroup.add(zArrow);

      // Z-Axis label - initial position (will be updated by updateLabelPositions)
      zAxisLabel = createTextSprite('Z', '#2196f3');
      zAxisLabel.position.set(-50, 40, props.cncConfig.zAxisLength);
      cncGroup.add(zAxisLabel);
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
    
    const createToolCrosshairs = (materials) => {
      const crosshairSize = 20;
      const crosshairRadius = 0.5;
      
      // Horizontal crosshair (X direction)
      const hCrosshairGeometry = createTrackedGeometry(THREE.CylinderGeometry, crosshairRadius, crosshairRadius, crosshairSize);
      const hCrosshair = createTrackedMesh(hCrosshairGeometry, materials.crosshair);
      hCrosshair.rotation.z = Math.PI / 2;
      toolHead.add(hCrosshair);
      
      // Vertical crosshair (Y direction)
      const vCrosshairGeometry = createTrackedGeometry(THREE.CylinderGeometry, crosshairRadius, crosshairRadius, crosshairSize);
      const vCrosshair = createTrackedMesh(vCrosshairGeometry, materials.crosshair);
      vCrosshair.rotation.x = Math.PI / 2;
      toolHead.add(vCrosshair);
      
      // Z crosshair (Z direction)
      const zCrosshairGeometry = createTrackedGeometry(THREE.CylinderGeometry, crosshairRadius, crosshairRadius, crosshairSize);
      const zCrosshair = createTrackedMesh(zCrosshairGeometry, materials.crosshair);
      toolHead.add(zCrosshair);
    };
    
    const createToolHead = (materials) => {
      const toolGeometry = createTrackedGeometry(THREE.SphereGeometry, 12);
      toolHead = createTrackedMesh(toolGeometry, materials.tool);
      toolHead.position.set(props.currentPos.x, props.currentPos.y, props.currentPos.z);
      
      initializeToolPosition();
      cncGroup.add(toolHead);
      createToolCrosshairs(materials);
    };
    
    const createXYGrid = () => {
      const workingX = props.cncConfig.workingZoneX;
      const workingY = props.cncConfig.workingZoneY;
      const gridDivisionsX = Math.max(Math.floor(workingX / 25), 4);
      const gridDivisionsY = Math.max(Math.floor(workingY / 25), 4);
      
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
      const xyGridMaterial = createTrackedMaterial(THREE.LineBasicMaterial, {
        color: 0x2a2a3a,
        opacity: 0.6,
        transparent: true
      });
      
      gridHelper = trackResource(new THREE.LineSegments(xyGridGeometry, xyGridMaterial), 'meshes');
      gridHelper.position.set(0, 0, -1);
      gridHelper.visible = showGrid && currentCameraView.value === 'Top';
      cncGroup.add(gridHelper);
    };
    
    const createXZGrid = () => {
      const workingX = props.cncConfig.workingZoneX;
      const workingZ = props.cncConfig.workingZoneZ;
      const gridDivisionsX = Math.max(Math.floor(workingX / 25), 4);
      const gridDivisionsZ = Math.max(Math.floor(workingZ / 25), 4);
      
      const xzGridGeometry = trackResource(new THREE.BufferGeometry(), 'geometries');
      const xzGridVertices = [];
      
      // Vertical lines (parallel to Z axis)
      for (let i = 0; i <= gridDivisionsX; i++) {
        const x = (i / gridDivisionsX) * workingX;
        xzGridVertices.push(x, 0, 0);
        xzGridVertices.push(x, 0, workingZ);
      }
      
      // Horizontal lines (parallel to X axis)
      for (let i = 0; i <= gridDivisionsZ; i++) {
        const z = (i / gridDivisionsZ) * workingZ;
        xzGridVertices.push(0, 0, z);
        xzGridVertices.push(workingX, 0, z);
      }
      
      xzGridGeometry.setAttribute('position', new THREE.Float32BufferAttribute(xzGridVertices, 3));
      const xzGridMaterial = createTrackedMaterial(THREE.LineBasicMaterial, {
        color: 0x2a2a3a,
        opacity: 0.6,
        transparent: true
      });
      
      fineGridHelper = trackResource(new THREE.LineSegments(xzGridGeometry, xzGridMaterial), 'meshes');
      fineGridHelper.position.set(0, -1, 0);
      fineGridHelper.visible = showGrid && currentCameraView.value === 'Side';
      cncGroup.add(fineGridHelper);
    };

    
    // Debug rotation axes - separate from cncGroup so they don't rotate
    let debugAxesGroup = null;
    let debugVerticalAxis = null;
    let debugHorizontalAxis = null;
    
    const createDebugRotationAxes = () => {
      // Create a separate group for debug axes that won't rotate with the CNC
      debugAxesGroup = new THREE.Group();
      scene.add(debugAxesGroup);
      
      // Get the center of the working zone box
      const centerX = props.cncConfig.xAxisLength / 2;
      const centerY = props.cncConfig.yAxisLength / 2;
      const centerZ = props.cncConfig.zAxisLength / 2;
      
      // Create vertical axis (Z-axis through center) - always stays vertical
      const verticalGeometry = createTrackedGeometry(THREE.CylinderGeometry, 1, 1, props.cncConfig.zAxisLength * 2);
      const verticalMaterial = createTrackedMaterial(THREE.MeshBasicMaterial, {
        color: 0xff00ff,  // Magenta for visibility
        opacity: 0.5,
        transparent: true
      });
      debugVerticalAxis = createTrackedMesh(verticalGeometry, verticalMaterial);
      debugVerticalAxis.position.set(centerX, centerY, centerZ);
      debugVerticalAxis.rotation.x = Math.PI / 2;  // Rotate to align with Z-axis
      debugAxesGroup.add(debugVerticalAxis);  // Add to separate group, not cncGroup
      
      // Create horizontal axis (X-axis through center for initial view) - always stays horizontal
      const horizontalGeometry = createTrackedGeometry(THREE.CylinderGeometry, 1, 1, Math.max(props.cncConfig.xAxisLength, props.cncConfig.yAxisLength) * 2);
      const horizontalMaterial = createTrackedMaterial(THREE.MeshBasicMaterial, {
        color: 0x00ffff,  // Cyan for visibility
        opacity: 0.5,
        transparent: true
      });
      debugHorizontalAxis = createTrackedMesh(horizontalGeometry, horizontalMaterial);
      debugHorizontalAxis.position.set(centerX, centerY, centerZ);
      debugHorizontalAxis.rotation.z = Math.PI / 2;
      debugAxesGroup.add(debugHorizontalAxis);  // Add to separate group, not cncGroup
    };
    
    const createSimpleAxisVisualization = () => {
      const materials = createAxisMaterials();
      
      createOriginPoint(materials);
      createXAxis(materials);
      createYAxis(materials);
      createZAxis(materials);
      createToolHead(materials);
      createXYGrid();
      createXZGrid();
      createClickTarget();
      createDebugRotationAxes(); // Add debug axes
    };
    
    const createWorkingZone = () => {
      const workingZoneGeometry = createTrackedGeometry(THREE.BoxGeometry,
        props.cncConfig.workingZoneX,
        props.cncConfig.workingZoneY,
        props.cncConfig.workingZoneZ
      );
      // Use EdgesGeometry to show only edges without diagonals
      const edgesGeometry = trackResource(new THREE.EdgesGeometry(workingZoneGeometry), 'geometries');
      const workingZoneMaterial = createTrackedMaterial(THREE.LineBasicMaterial, {
        color: 0xffa500,  // Orange color - distinct from axes
        opacity: 0.8,     // Much more visible
        transparent: true,
        linewidth: 2      // Thicker lines
      });
      workingZoneMesh = trackResource(new THREE.LineSegments(edgesGeometry, workingZoneMaterial), 'meshes');
      // Position working zone starting from origin (0,0,0)
      workingZoneMesh.position.set(
        props.cncConfig.workingZoneX / 2,
        props.cncConfig.workingZoneY / 2,
        props.cncConfig.workingZoneZ / 2
      );
      workingZoneMesh.visible = showWorkingZone.value; // Set initial visibility from state (now true by default)
      cncGroup.add(workingZoneMesh);
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
      
      // Add ghost crosshairs identical to original but transparent
      const ghostCrosshairMaterial = createTrackedMaterial(THREE.MeshBasicMaterial, { 
        color: 0x000000, // Same black color as original
        transparent: true,
        opacity: 0.3 // Semi-transparent
      });
      
      // Horizontal crosshair (X direction) - identical to original
      const hGhostCrosshair = createTrackedMesh(
        createTrackedGeometry(THREE.CylinderGeometry, 0.5, 0.5, 20),
        ghostCrosshairMaterial
      );
      hGhostCrosshair.rotation.z = Math.PI / 2;
      ghostToolHead.add(hGhostCrosshair);
      
      // Vertical crosshair (Y direction) - identical to original
      const vGhostCrosshair = createTrackedMesh(
        createTrackedGeometry(THREE.CylinderGeometry, 0.5, 0.5, 20),
        ghostCrosshairMaterial
      );
      vGhostCrosshair.rotation.x = Math.PI / 2;
      ghostToolHead.add(vGhostCrosshair);
      
      // Z crosshair (Z direction) - identical to original
      const zGhostCrosshair = createTrackedMesh(
        createTrackedGeometry(THREE.CylinderGeometry, 0.5, 0.5, 20),
        ghostCrosshairMaterial
      );
      ghostToolHead.add(zGhostCrosshair);
      
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
      // No panning limits - allow free movement
      return newPosition;
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

    const handleMouseMove = (mouseState) => (event) => {
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
      const configHash = `${props.cncConfig.xAxisLength}-${props.cncConfig.yAxisLength}-${props.cncConfig.zAxisLength}`;
      
      if (configHash !== lastZoomConfigHash) {
        const maxDimension = Math.max(
          props.cncConfig.xAxisLength,
          props.cncConfig.yAxisLength,
          props.cncConfig.zAxisLength
        );
        cachedZoomLimits = {
          minDistance: maxDimension * 0.5,
          maxDistance: maxDimension * 1.5
        };
        lastZoomConfigHash = configHash;
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
        
        // Get mouse position relative to the renderer canvas
        const rect = renderer.domElement.getBoundingClientRect();
        if (rect.width <= 0 || rect.height <= 0) {
          logger.warn('Click-to-move blocked: invalid canvas dimensions');
          return;
        }
        
        mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
      
      // Update raycaster
      raycaster.setFromCamera(mouse, camera);
      
      // Create intersection plane based on current view
      let clickedPosition = null;
      
      if (currentCameraView.value === 'Top') {
        // Top view: intersect with XY plane, preserve Z from previous target or use current Z
        const plane = new THREE.Plane(new THREE.Vector3(0, 0, 1), -props.currentPos.z);
        const intersectionPoint = new THREE.Vector3();
        if (raycaster.ray.intersectPlane(plane, intersectionPoint)) {
          clickedPosition = {
            x: intersectionPoint.x,
            y: intersectionPoint.y,
            z: targetPosition.value?.z || props.currentPos.z // Keep Z from previous target or current
          };
        }
      } else if (currentCameraView.value === 'Side') {
        // Side view: only set Z-axis from click, keep X,Y from previous target or current position
        const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), -props.currentPos.y);
        const intersectionPoint = new THREE.Vector3();
        if (raycaster.ray.intersectPlane(plane, intersectionPoint)) {
          clickedPosition = {
            x: targetPosition.value?.x || props.currentPos.x, // Keep X from previous target or current
            y: targetPosition.value?.y || props.currentPos.y, // Keep Y from previous target or current
            z: intersectionPoint.z   // Only set Z from click
          };
        }
      }
      
      console.log('Target position calculated:', clickedPosition);
      console.log('Working zone check:', clickedPosition ? isWithinWorkingZone(clickedPosition) : 'No target position');
      
      if (clickedPosition && isWithinWorkingZone(clickedPosition)) {
        console.log('Target position is valid, checking connection/simulation...');
        
        // Check if CNC is connected OR simulation mode is enabled
        if (!props.isCncConnected && !isSimulationMode.value) {
          logger.warn('Click-to-move blocked: CNC not connected and simulation disabled');
          return;
        }
        
        console.log('Showing click target...');
        // Show click target indicator
        showClickTarget(clickedPosition);
        
        if (isSimulationMode.value) {
          // Simulation mode: just set target, don't execute until play button is pressed
          logger.info(`Simulation: Target set at position (${clickedPosition.x.toFixed(2)}, ${clickedPosition.y.toFixed(2)}, ${clickedPosition.z.toFixed(2)})`);
          setSimulationTarget(clickedPosition);
        } else {
          // Real mode: emit move command to parent component
          emit('moveTo', clickedPosition);
          logger.info(`Click-to-move: Target position (${clickedPosition.x.toFixed(2)}, ${clickedPosition.y.toFixed(2)}, ${clickedPosition.z.toFixed(2)})`);
          
          // Also emit target update for real mode
          emit('targetUpdate', clickedPosition);
        }
      } else if (clickedPosition && !isWithinWorkingZone(clickedPosition)) {
        console.log('Target outside working zone:', clickedPosition);
        console.log('Working zone bounds:', {
          x: props.cncConfig.workingZoneX,
          y: props.cncConfig.workingZoneY,
          z: props.cncConfig.workingZoneZ
        });
        logger.warn('Click-to-move blocked: Target outside working zone', clickedPosition);
      } else {
        console.log('No valid target position calculated');
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
    
    const isWithinWorkingZone = (position) => {
      return position.x >= 0 && position.x <= props.cncConfig.workingZoneX &&
             position.y >= 0 && position.y <= props.cncConfig.workingZoneY &&
             position.z >= 0 && position.z <= props.cncConfig.workingZoneZ;
    };
    
    const showClickTarget = (position) => {
      // Show ghost tool head at target position
      if (ghostToolHead) {
        ghostToolHead.position.set(position.x, position.y, position.z);
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
        
        // Create line geometry showing simultaneous multi-axis movement
        // Direct straight line path from current to target position
        const points = [];
        
        // Start position
        points.push(new THREE.Vector3(currentPos.x, currentPos.y, currentPos.z));
        
        // Direct to target position (simultaneous movement)
        points.push(new THREE.Vector3(targetPosition.x, targetPosition.y, targetPosition.z));
        
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
        ghostToolHead.position.set(position.x, position.y, position.z);
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
        
        logger.info(`Simulation: Executing movement to (${target.x.toFixed(2)}, ${target.y.toFixed(2)}, ${target.z.toFixed(2)})`);
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
        toolHead.position.set(newPosition.x, newPosition.y, newPosition.z);
        
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
      
      // Only update if target position changed
      if (!hasPositionChanged(targetPos, cachedValues.lastToolPosition)) {
        return false;
      }
      
      // Smooth lerp to actual position
      const lerpSpeed = 0.15;
      const newPosition = {
        x: toolHead.position.x + (targetPos.x - toolHead.position.x) * lerpSpeed,
        y: toolHead.position.y + (targetPos.y - toolHead.position.y) * lerpSpeed,
        z: toolHead.position.z + (targetPos.z - toolHead.position.z) * lerpSpeed
      };
      
      if (updateCachedPosition(newPosition, 'lastToolPosition')) {
        toolHead.position.set(newPosition.x, newPosition.y, newPosition.z);
        
        // Update display position only if it changed significantly
        if (updateCachedPosition(newPosition, 'lastDisplayPosition')) {
          displayPosition.value.x = newPosition.x;
          displayPosition.value.y = newPosition.y;
          displayPosition.value.z = newPosition.z;
        }
        
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
        toolHead.position.set(currentPos.x, currentPos.y, currentPos.z);
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
    
    // Camera management functions
    const getCameraCenter = () => {
      const maxX = props.cncConfig.xAxisLength;
      const maxY = props.cncConfig.yAxisLength;
      const maxZ = props.cncConfig.zAxisLength;
      
      return {
        x: maxX / 2,
        y: maxY / 2,
        z: maxZ / 2,
        vector: new THREE.Vector3(maxX / 2, maxY / 2, maxZ / 2)
      };
    };
    
    const getCameraDistance = () => {
      const maxX = props.cncConfig.xAxisLength;
      const maxY = props.cncConfig.yAxisLength;
      const maxZ = props.cncConfig.zAxisLength;
      return Math.max(maxX, maxY, maxZ) * 0.7;
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
    
    const updateLabelPositions = (viewType) => {
      switch (viewType) {
        case '3D':
          // In 3D view, show all three axis labels
          if (xAxisLabel) {
            xAxisLabel.position.set(props.cncConfig.xAxisLength, -50, 40);
            xAxisLabel.visible = true;
          }
          if (yAxisLabel) {
            yAxisLabel.position.set(-50, props.cncConfig.yAxisLength, 40);
            yAxisLabel.visible = true;
          }
          if (zAxisLabel) {
            zAxisLabel.position.set(-50, 40, props.cncConfig.zAxisLength);
            zAxisLabel.visible = true;
          }
          break;
        case 'Top':
          // In top view, show only X and Y labels (front axes), hide Z label (behind)
          if (xAxisLabel) {
            xAxisLabel.position.set(props.cncConfig.xAxisLength, -50, 40);
            xAxisLabel.visible = true;
          }
          if (yAxisLabel) {
            yAxisLabel.position.set(-50, props.cncConfig.yAxisLength, 40);
            yAxisLabel.visible = true;
          }
          if (zAxisLabel) zAxisLabel.visible = false; // Hide Z label (behind in top view)
          break;
        case 'Side':
          // In side view, show only X and Z labels (front axes), hide Y label (behind)
          if (xAxisLabel) {
            xAxisLabel.position.set(props.cncConfig.xAxisLength, 50, -50);
            xAxisLabel.visible = true;
          }
          if (yAxisLabel) yAxisLabel.visible = false; // Hide Y label (behind in side view)
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
      const center = getCameraCenter();
      const distance = getCameraDistance();
      
      setGridVisibility(viewType);
      
      let targetPosition;
      
      switch (viewType) {
        case '3D':
          // Isometric 3D view - camera positioned so Z-axis appears perfectly vertical on screen
          const isoDistance = Math.max(props.cncConfig.xAxisLength, props.cncConfig.yAxisLength, props.cncConfig.zAxisLength) * 1.45;
          const boxCenterX = props.cncConfig.xAxisLength * 0.5;
          const boxCenterY = props.cncConfig.yAxisLength * 0.5;
          const boxCenterZ = props.cncConfig.zAxisLength * 0.5;
          
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
          // Adjust zoom for Top view to show labels better
          const topDistance = Math.max(props.cncConfig.xAxisLength, props.cncConfig.yAxisLength, props.cncConfig.zAxisLength) * 0.75;
          targetPosition = new THREE.Vector3(center.x, center.y, -topDistance);
          smoothCameraTransition(targetPosition, new THREE.Vector3(center.x, center.y, 0), 600);
          break;
        case 'Side':
          // Adjust distance for Side view - slightly zoomed out
          const sideDistance = Math.max(props.cncConfig.xAxisLength, props.cncConfig.zAxisLength) * 1.1;
          targetPosition = new THREE.Vector3(center.x, -sideDistance, center.z);
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
      currentCameraIndex.value = (currentCameraIndex.value + 1) % cameraViews.length;
      const newView = currentCameraView.value;
      
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
    };
    
    // UI Interaction Functions
    const syncToRealCNCPosition = () => {
      if (!toolHead) return;
      
      toolHead.position.set(props.currentPos.x, props.currentPos.y, props.currentPos.z);
      displayPosition.value.x = props.currentPos.x;
      displayPosition.value.y = props.currentPos.y;
      displayPosition.value.z = props.currentPos.z;
      
      // Update cached values when syncing position
      cachedValues.lastToolPosition.x = props.currentPos.x;
      cachedValues.lastToolPosition.y = props.currentPos.y;
      cachedValues.lastToolPosition.z = props.currentPos.z;
      cachedValues.lastDisplayPosition.x = props.currentPos.x;
      cachedValues.lastDisplayPosition.y = props.currentPos.y;
      cachedValues.lastDisplayPosition.z = props.currentPos.z;
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
      
      // When exiting simulation mode, sync back to real CNC position
      if (!isSimulationMode.value) {
        syncToRealCNCPosition();
        clearSimulationState();
      }
    };
    
    const toggleWorkingZone = () => {
      showWorkingZone.value = !showWorkingZone.value;
      if (workingZoneMesh) {
        workingZoneMesh.visible = showWorkingZone.value;
        markDirty('rendering');
      }
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

    
    return {
      threeContainer,
      isAnimating,
      showWorkingZone,
      currentCameraView,
      resetCamera,
      toggleWorkingZone,
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
      executeSimulation,
      webglError,
      errorMessage,
      hasWebglSupport,
      isInitialized,
      retryInitialization,
      // Axis display computed properties
      selectedLinearAxes,
      selectedAxesDisplay,
      axisLengthsDisplay,
      workZoneDisplay
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
}

.info-panel {
  width: 380px !important;
  background-color: var(--color-bg-secondary);
  border-left: var(--border-width-1) solid var(--color-border-secondary);
  padding: var(--space-5);
  padding-right: var(--space-6); /* Extra space from scrollbar */
  overflow-y: auto;
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