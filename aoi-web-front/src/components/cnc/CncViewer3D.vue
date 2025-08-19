<template>
  <div class="viewer-container">
    <div class="viewer-header">
      <h2>CNC Digital Twin - {{ cncConfig.cncType.toUpperCase() }}</h2>
      <div class="viewer-controls">
        <button @click="resetCamera" class="control-button">
          <font-awesome-icon icon="home" />
          Reset View
        </button>
        <button @click="toggleAnimation" class="control-button">
          <font-awesome-icon :icon="isAnimating ? 'pause' : 'play'" />
          {{ isAnimating ? 'Pause' : 'Animate' }}
        </button>
        <button @click="toggleWorkingZone" class="control-button">
          <font-awesome-icon icon="cog" />
          Working Zone
        </button>
        <button @click="switchCameraView" class="control-button">
          <font-awesome-icon icon="cog" />
          {{ currentCameraView }}
        </button>
        <button @click="closeViewer" class="close-button">
          <font-awesome-icon icon="home" />
          Close
        </button>
      </div>
    </div>
    
    <div class="viewer-content">
      <div class="three-container" ref="threeContainer">
        <!-- Dynamic axis labels positioned by 3D coordinates -->
        <div class="axis-labels" ref="axisLabels">
          <div class="axis-label x-label" ref="xLabel">X</div>
          <div class="axis-label y-label" ref="yLabel">Y</div>
          <div class="axis-label z-label" ref="zLabel">Z</div>
        </div>
      </div>
      
      <div class="info-panel">
        <div class="position-info">
          <h4>Current Position</h4>
          <div class="position-row">
            <span class="axis">X:</span>
            <span class="value">{{ currentPos.x.toFixed(3) }}mm</span>
          </div>
          <div class="position-row">
            <span class="axis">Y:</span>
            <span class="value">{{ currentPos.y.toFixed(3) }}mm</span>
          </div>
          <div class="position-row">
            <span class="axis">Z:</span>
            <span class="value">{{ currentPos.z.toFixed(3) }}mm</span>
          </div>
        </div>
        
        <div class="config-info">
          <h4>Configuration</h4>
          <div class="config-row">
            <span class="label">Type:</span>
            <span class="value">{{ cncConfig.cncType }}</span>
          </div>
          <div class="config-row">
            <span class="label">Axes:</span>
            <span class="value">{{ cncConfig.xAxisLength }}×{{ cncConfig.yAxisLength }}×{{ cncConfig.zAxisLength }}mm</span>
          </div>
          <div class="config-row">
            <span class="label">Work Zone:</span>
            <span class="value">{{ cncConfig.workingZoneX }}×{{ cncConfig.workingZoneY }}×{{ cncConfig.workingZoneZ }}mm</span>
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
    }
  },
  emits: ['close'],
  setup(props, { emit }) {
    const threeContainer = ref(null);
    const axisLabels = ref(null);
    const xLabel = ref(null);
    const yLabel = ref(null);
    const zLabel = ref(null);
    
    // Three.js objects
    let scene = null;
    let camera = null;
    let renderer = null;
    let controls = null;
    let animationId = null;
    
    // CNC components
    let cncGroup = null;
    let toolHead = null;
    let workingZoneMesh = null;
    let xAxisMesh = null;
    let yAxisMesh = null;
    let zAxisMesh = null;
    
    // State
    const isAnimating = ref(true);
    const showWorkingZone = ref(true);
    
    // Camera views
    const cameraViews = ['Top', 'Side'];
    const currentCameraIndex = ref(0);
    const currentCameraView = computed(() => cameraViews[currentCameraIndex.value]);
    
    // Initialize Three.js scene
    const initThreeJS = () => {
      if (!threeContainer.value) return;
      
      // Scene setup
      scene = new THREE.Scene();
      scene.background = new THREE.Color(0x1a1a1a);
      
      // Camera setup
      const aspect = threeContainer.value.clientWidth / threeContainer.value.clientHeight;
      camera = new THREE.PerspectiveCamera(60, aspect, 1, 50000);
      
      // Set initial camera position
      setCameraPosition(currentCameraView.value);
      
      // Renderer setup
      renderer = new THREE.WebGLRenderer({ antialias: true });
      renderer.setSize(threeContainer.value.clientWidth, threeContainer.value.clientHeight);
      threeContainer.value.appendChild(renderer.domElement);
      
      // Lighting
      setupLighting();
      
      // Create CNC rig
      createCNCRig();
      
      // Controls (basic rotation for now)
      setupControls();
      
      // Start animation loop
      animate();
      
      logger.info('Three.js CNC viewer initialized');
    };
    
    const setupLighting = () => {
      // Ambient light (main illumination)
      const ambientLight = new THREE.AmbientLight(0x404040, 0.8);
      scene.add(ambientLight);
      
      // Directional light (no shadows)
      const directionalLight = new THREE.DirectionalLight(0xffffff, 0.6);
      directionalLight.position.set(
        props.cncConfig.xAxisLength,
        props.cncConfig.yAxisLength,
        props.cncConfig.zAxisLength * 2
      );
      scene.add(directionalLight);
      
      // Fill light
      const fillLight = new THREE.DirectionalLight(0x6699ff, 0.4);
      fillLight.position.set(-props.cncConfig.xAxisLength, props.cncConfig.yAxisLength, props.cncConfig.zAxisLength);
      scene.add(fillLight);
    };
    
    const createCNCRig = () => {
      cncGroup = new THREE.Group();
      
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
      
      // Working zone visualization
      if (showWorkingZone.value) {
        createWorkingZone();
      }
      
      scene.add(cncGroup);
      
      logger.info(`${props.cncConfig.cncType.toUpperCase()} CNC rig 3D model created`);
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
    
    const createSimpleAxisVisualization = () => {
      // Simple axis materials
      const xAxisMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000 }); // Red for X
      const yAxisMaterial = new THREE.MeshBasicMaterial({ color: 0x00ff00 }); // Green for Y  
      const zAxisMaterial = new THREE.MeshBasicMaterial({ color: 0x0000ff }); // Blue for Z
      const toolMaterial = new THREE.MeshBasicMaterial({ color: 0xffff00 }); // Yellow for tool
      const originMaterial = new THREE.MeshBasicMaterial({ color: 0xffffff }); // White for origin
      
      // Origin point (0,0,0)
      const originGeometry = new THREE.SphereGeometry(5);
      const originSphere = new THREE.Mesh(originGeometry, originMaterial);
      originSphere.position.set(0, 0, 0);
      cncGroup.add(originSphere);
      
      // Create axes using lines instead of cylinders for precise positioning
      // X-Axis (Red) - horizontal line from origin
      if (props.cncConfig.xAxisLength > 0) {
        const xPoints = [
          new THREE.Vector3(0, 0, 0),  // Start at origin
          new THREE.Vector3(props.cncConfig.xAxisLength, 0, 0)  // End at X length
        ];
        const xGeometry = new THREE.BufferGeometry().setFromPoints(xPoints);
        const xLine = new THREE.Line(xGeometry, new THREE.LineBasicMaterial({ 
          color: 0xff0000, 
          linewidth: 4 
        }));
        cncGroup.add(xLine);
        
        // X-Axis arrow and label
        const xArrowGeometry = new THREE.ConeGeometry(5, 15, 8);
        const xArrow = new THREE.Mesh(xArrowGeometry, xAxisMaterial);
        xArrow.position.set(props.cncConfig.xAxisLength + 10, 0, 0);
        xArrow.rotation.z = -Math.PI / 2; // Point along X-axis
        cncGroup.add(xArrow);
        
      }
      
      // Y-Axis (Green) - horizontal line from origin  
      if (props.cncConfig.yAxisLength > 0) {
        const yPoints = [
          new THREE.Vector3(0, 0, 0),  // Start at origin
          new THREE.Vector3(0, props.cncConfig.yAxisLength, 0)  // End at Y length
        ];
        const yGeometry = new THREE.BufferGeometry().setFromPoints(yPoints);
        const yLine = new THREE.Line(yGeometry, new THREE.LineBasicMaterial({ 
          color: 0x00ff00, 
          linewidth: 4 
        }));
        cncGroup.add(yLine);
        
        // Y-Axis arrow and label
        const yArrowGeometry = new THREE.ConeGeometry(5, 15, 8);
        const yArrow = new THREE.Mesh(yArrowGeometry, yAxisMaterial);
        yArrow.position.set(0, props.cncConfig.yAxisLength + 10, 0);
        yArrow.rotation.x = Math.PI / 2; // Point along Y-axis
        cncGroup.add(yArrow);
        
      }
      
      // Z-Axis (Blue) - vertical line from origin
      if (props.cncConfig.zAxisLength > 0) {
        const zPoints = [
          new THREE.Vector3(0, 0, 0),  // Start at origin
          new THREE.Vector3(0, 0, props.cncConfig.zAxisLength)  // End at Z length
        ];
        const zGeometry = new THREE.BufferGeometry().setFromPoints(zPoints);
        const zLine = new THREE.Line(zGeometry, new THREE.LineBasicMaterial({ 
          color: 0x0000ff, 
          linewidth: 4 
        }));
        cncGroup.add(zLine);
        
        // Z-Axis arrow and label
        const zArrowGeometry = new THREE.ConeGeometry(5, 15, 8);
        const zArrow = new THREE.Mesh(zArrowGeometry, zAxisMaterial);
        zArrow.position.set(0, 0, props.cncConfig.zAxisLength + 10);
        // No rotation needed - cone points up by default
        cncGroup.add(zArrow);
        
      }
      
      // Tool head (Yellow) - shows current position and moves with commands
      const toolGeometry = new THREE.SphereGeometry(15);
      toolHead = new THREE.Mesh(toolGeometry, toolMaterial);
      toolHead.position.set(props.currentPos.x, props.currentPos.y, props.currentPos.z);
      cncGroup.add(toolHead);
      
      // Tool crosshairs for better visibility
      const crosshairMaterial = new THREE.MeshBasicMaterial({ color: 0x000000 });
      
      // Horizontal crosshair (X direction)
      const hCrosshairGeometry = new THREE.CylinderGeometry(1, 1, 40);
      const hCrosshair = new THREE.Mesh(hCrosshairGeometry, crosshairMaterial);
      hCrosshair.rotation.z = Math.PI / 2;
      toolHead.add(hCrosshair);
      
      // Vertical crosshair (Y direction) 
      const vCrosshairGeometry = new THREE.CylinderGeometry(1, 1, 40);
      const vCrosshair = new THREE.Mesh(vCrosshairGeometry, crosshairMaterial);
      vCrosshair.rotation.x = Math.PI / 2;
      toolHead.add(vCrosshair);
      
      // Z crosshair (Z direction)
      const zCrosshairGeometry = new THREE.CylinderGeometry(1, 1, 40);
      const zCrosshair = new THREE.Mesh(zCrosshairGeometry, crosshairMaterial);
      toolHead.add(zCrosshair);
      
      // Simple base plane to show work surface (optional, can be toggled)
      const basePlaneGeometry = new THREE.PlaneGeometry(
        Math.max(props.cncConfig.xAxisLength, 100),
        Math.max(props.cncConfig.yAxisLength, 100)
      );
      const basePlaneMaterial = new THREE.MeshBasicMaterial({ 
        color: 0x444444, 
        transparent: true, 
        opacity: 0.1,
        side: THREE.DoubleSide
      });
      const basePlane = new THREE.Mesh(basePlaneGeometry, basePlaneMaterial);
      basePlane.position.set(
        props.cncConfig.xAxisLength / 2, 
        props.cncConfig.yAxisLength / 2, 
        -2  // Position slightly below Z=0 to avoid interference
      );
      basePlane.rotation.x = -Math.PI / 2; // Lay flat on XY plane
      basePlane.visible = false; // Hide by default
      cncGroup.add(basePlane);
    };
    
    const createWorkingZone = () => {
      const workingZoneGeometry = new THREE.BoxGeometry(
        props.cncConfig.workingZoneX,
        props.cncConfig.workingZoneY,
        props.cncConfig.workingZoneZ
      );
      const workingZoneMaterial = new THREE.MeshBasicMaterial({
        color: 0x00aa00,  // Darker green to be less intrusive
        opacity: 0.05,    // Much more transparent
        transparent: true,
        wireframe: true
      });
      workingZoneMesh = new THREE.Mesh(workingZoneGeometry, workingZoneMaterial);
      // Position working zone starting from origin (0,0,0)
      workingZoneMesh.position.set(
        props.cncConfig.workingZoneX / 2,
        props.cncConfig.workingZoneY / 2,
        props.cncConfig.workingZoneZ / 2
      );
      workingZoneMesh.visible = false; // Hide by default, can be toggled
      cncGroup.add(workingZoneMesh);
    };
    
    const setupControls = () => {
      let isLeftMouseDown = false;
      let isMiddleMouseDown = false;
      let mouseX = 0;
      let mouseY = 0;
      
      const onMouseDown = (event) => {
        event.preventDefault();
        mouseX = event.clientX;
        mouseY = event.clientY;
        
        if (event.button === 0) { // Left mouse button
          isLeftMouseDown = true;
        } else if (event.button === 1) { // Middle mouse button (wheel)
          isMiddleMouseDown = true;
        }
      };
      
      const onMouseUp = (event) => {
        if (event.button === 0) { // Left mouse button
          isLeftMouseDown = false;
        } else if (event.button === 1) { // Middle mouse button
          isMiddleMouseDown = false;
        }
      };
      
      const onMouseMove = (event) => {
        if (!isLeftMouseDown && !isMiddleMouseDown) return;
        
        const deltaX = event.clientX - mouseX;
        const deltaY = event.clientY - mouseY;
        
        if (isLeftMouseDown) {
          // Left mouse: Pan camera view (left/right/up/down)
          const panSpeed = 2;
          
          // Get camera's right vector (for horizontal panning)
          const rightVector = new THREE.Vector3();
          rightVector.crossVectors(camera.up, camera.getWorldDirection(new THREE.Vector3()));
          rightVector.normalize();
          
          // Get camera's up vector (for vertical panning)
          const upVector = camera.up.clone();
          
          // Calculate pan movement
          const panX = rightVector.clone().multiplyScalar(deltaX * panSpeed);
          const panY = upVector.clone().multiplyScalar(deltaY * panSpeed);
          
          // Apply panning to camera position
          camera.position.add(panX);
          camera.position.add(panY);
          
        } else if (isMiddleMouseDown) {
          // Middle mouse: Rotate camera around the CNC center
          const spherical = new THREE.Spherical();
          spherical.setFromVector3(camera.position.clone().sub(new THREE.Vector3(
            props.cncConfig.xAxisLength / 2,
            props.cncConfig.yAxisLength / 2,
            props.cncConfig.zAxisLength / 2
          )));
          
          spherical.theta -= deltaX * 0.01;
          spherical.phi += deltaY * 0.01;
          spherical.phi = Math.max(0.1, Math.min(Math.PI - 0.1, spherical.phi));
          
          const center = new THREE.Vector3(
            props.cncConfig.xAxisLength / 2,
            props.cncConfig.yAxisLength / 2,
            props.cncConfig.zAxisLength / 2
          );
          
          camera.position.setFromSpherical(spherical).add(center);
          camera.lookAt(center);
        }
        
        mouseX = event.clientX;
        mouseY = event.clientY;
      };
      
      // Prevent context menu on right click
      const onContextMenu = (event) => {
        event.preventDefault();
      };
      
      renderer.domElement.addEventListener('mousedown', onMouseDown);
      renderer.domElement.addEventListener('mouseup', onMouseUp);
      renderer.domElement.addEventListener('mousemove', onMouseMove);
      renderer.domElement.addEventListener('contextmenu', onContextMenu);
      
      // Zoom with mouse wheel
      const onWheel = (event) => {
        event.preventDefault();
        const scale = event.deltaY > 0 ? 1.1 : 0.9;
        const center = new THREE.Vector3(
          props.cncConfig.xAxisLength / 2,
          props.cncConfig.yAxisLength / 2,
          props.cncConfig.zAxisLength / 2
        );
        
        // Zoom towards/away from center
        const direction = camera.position.clone().sub(center).normalize();
        const distance = camera.position.distanceTo(center);
        const newDistance = distance * scale;
        
        camera.position.copy(center).add(direction.multiplyScalar(newDistance));
      };
      
      renderer.domElement.addEventListener('wheel', onWheel);
    };
    
    const updateAxisLabels = () => {
      if (!camera || !renderer || !xLabel.value || !yLabel.value || !zLabel.value) return;
      
      const canvas = renderer.domElement;
      const canvasRect = canvas.getBoundingClientRect();
      
      // Convert 3D world positions to screen coordinates
      const vector = new THREE.Vector3();
      
      // X-Axis label position (at end of X axis)
      vector.set(props.cncConfig.xAxisLength + 30, 0, 0);
      vector.project(camera);
      const xScreenX = (vector.x * 0.5 + 0.5) * canvasRect.width;
      const xScreenY = (vector.y * -0.5 + 0.5) * canvasRect.height;
      xLabel.value.style.left = `${Math.max(10, Math.min(xScreenX - 10, canvasRect.width - 30))}px`;
      xLabel.value.style.top = `${Math.max(10, Math.min(xScreenY - 10, canvasRect.height - 30))}px`;
      
      // Y-Axis label position (at end of Y axis)
      vector.set(0, props.cncConfig.yAxisLength + 30, 0);
      vector.project(camera);
      const yScreenX = (vector.x * 0.5 + 0.5) * canvasRect.width;
      const yScreenY = (vector.y * -0.5 + 0.5) * canvasRect.height;
      yLabel.value.style.left = `${Math.max(10, Math.min(yScreenX - 10, canvasRect.width - 30))}px`;
      yLabel.value.style.top = `${Math.max(10, Math.min(yScreenY - 10, canvasRect.height - 30))}px`;
      
      // Z-Axis label position (at end of Z axis)
      vector.set(0, 0, props.cncConfig.zAxisLength + 30);
      vector.project(camera);
      const zScreenX = (vector.x * 0.5 + 0.5) * canvasRect.width;
      const zScreenY = (vector.y * -0.5 + 0.5) * canvasRect.height;
      zLabel.value.style.left = `${Math.max(10, Math.min(zScreenX - 10, canvasRect.width - 30))}px`;
      zLabel.value.style.top = `${Math.max(10, Math.min(zScreenY - 10, canvasRect.height - 30))}px`;
    };

    const animate = () => {
      if (!isAnimating.value) return;
      
      animationId = requestAnimationFrame(animate);
      
      // Simple animation - just update tool head position
      if (toolHead) {
        toolHead.position.set(props.currentPos.x, props.currentPos.y, props.currentPos.z);
      }
      
      // Update axis labels positions
      updateAxisLabels();
      
      renderer.render(scene, camera);
    };
    
    // Camera positioning functions
    const setCameraPosition = (viewType) => {
      const maxX = props.cncConfig.xAxisLength;
      const maxY = props.cncConfig.yAxisLength;
      const maxZ = props.cncConfig.zAxisLength;
      
      // Center point for all views
      const centerX = maxX / 2;
      const centerY = maxY / 2;
      const centerZ = maxZ / 2;
      
      // Distance for camera positioning
      const distance = Math.max(maxX, maxY, maxZ) * 1.5;
      
      switch (viewType) {
        case 'Top':
          // Top view - looking down at XY plane (perfect for seeing X and Y axes)
          camera.position.set(centerX, centerY, distance);
          camera.lookAt(centerX, centerY, 0);
          break;
          
        case 'Side':
          // Side view - looking from front/back to see Z axis vertically (XZ plane)
          camera.position.set(centerX, -distance, centerZ);
          camera.lookAt(centerX, centerY, centerZ);
          break;
          
        default:
          // Default to top view
          camera.position.set(centerX, centerY, distance);
          camera.lookAt(centerX, centerY, 0);
      }
    };
    
    const resetCamera = () => {
      setCameraPosition(currentCameraView.value);
      updateAxisLabels();
    };
    
    const switchCameraView = () => {
      currentCameraIndex.value = (currentCameraIndex.value + 1) % cameraViews.length;
      setCameraPosition(currentCameraView.value);
      updateAxisLabels();
    };
    
    const toggleAnimation = () => {
      isAnimating.value = !isAnimating.value;
      if (isAnimating.value) {
        animate();
      }
    };
    
    const toggleWorkingZone = () => {
      showWorkingZone.value = !showWorkingZone.value;
      if (workingZoneMesh) {
        workingZoneMesh.visible = showWorkingZone.value;
      }
    };
    
    const closeViewer = () => {
      emit('close');
    };
    
    // Handle window resize
    const onWindowResize = () => {
      if (!threeContainer.value || !camera || !renderer) return;
      
      const width = threeContainer.value.clientWidth;
      const height = threeContainer.value.clientHeight;
      
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
    };
    
    // Lifecycle
    onMounted(() => {
      initThreeJS();
      window.addEventListener('resize', onWindowResize);
    });
    
    onUnmounted(() => {
      if (animationId) {
        cancelAnimationFrame(animationId);
      }
      if (renderer) {
        renderer.dispose();
      }
      window.removeEventListener('resize', onWindowResize);
    });
    
    // Watch for position changes
    watch(() => props.currentPos, (newPos) => {
      // Position updates will be handled in the animation loop
    }, { deep: true });
    
    return {
      threeContainer,
      axisLabels,
      xLabel,
      yLabel,
      zLabel,
      isAnimating,
      showWorkingZone,
      currentCameraView,
      resetCamera,
      toggleAnimation,
      toggleWorkingZone,
      switchCameraView,
      closeViewer
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
  gap: var(--space-2);
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
  width: 250px;
  background-color: var(--color-bg-secondary);
  border-left: var(--border-width-1) solid var(--color-border-secondary);
  padding: var(--space-4);
  overflow-y: auto;
}

.position-info,
.config-info {
  margin-bottom: var(--space-4);
}

.position-info h4,
.config-info h4 {
  margin: 0 0 var(--space-3) 0;
  color: var(--color-primary);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-bold);
}

.position-row,
.config-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-2);
  padding: var(--space-1);
  background-color: var(--color-bg-tertiary);
  border-radius: var(--border-radius-base);
}

.axis,
.label {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
}

.value {
  font-family: var(--font-family-mono);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

/* Axis Labels Overlay */
.axis-labels {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 100;
}

.axis-label {
  position: absolute;
  font-size: 20px;
  font-weight: bold;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
  padding: 4px 8px;
  border-radius: 4px;
  backdrop-filter: blur(2px);
  pointer-events: none;
  z-index: 10;
}

.x-label {
  color: #ff0000;
  background-color: rgba(255, 0, 0, 0.2);
  border: 2px solid #ff0000;
}

.y-label {
  color: #00ff00;
  background-color: rgba(0, 255, 0, 0.2);
  border: 2px solid #00ff00;
}

.z-label {
  color: #0000ff;
  background-color: rgba(0, 0, 255, 0.2);
  border: 2px solid #0000ff;
}

</style>