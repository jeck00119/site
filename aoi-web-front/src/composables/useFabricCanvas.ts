/**
 * Fabric.js Canvas Composable
 * 
 * Provides centralized canvas initialization and management for Fabric.js.
 * Standardizes canvas setup across CameraScene, MaskScene, and CustomComponentsConfiguration.
 */

import { ref, onUnmounted, watch } from 'vue';
import * as fabric from 'fabric';

interface CanvasOptions {
  selection?: boolean;
  fireRightClick?: boolean;
  stopContextMenu?: boolean;
  isDrawingMode?: boolean;
  width?: number;
  height?: number;
  performanceMode?: boolean;
  containerRef?: { value: HTMLElement | null };
  scaleX?: number;
  scaleY?: number;
  stretch?: boolean;
  backgroundColor?: string;
  format?: string;
  quality?: number;
  multiplier?: number;
  [key: string]: any;
}

/**
 * Create and manage a Fabric.js canvas instance
 * 
 * @param canvasId - The HTML canvas element ID
 * @param options - Canvas configuration options
 * @returns Canvas instance and utility functions
 */
export function useFabricCanvas(canvasId: string, options: CanvasOptions = {}): any {
  const canvas = ref<fabric.Canvas | null>(null);
  const isInitialized = ref(false);
  
  // Default optimized settings for performance
  const defaultOptions = {
    // Performance optimizations
    renderOnAddRemove: false,
    imageSmoothingEnabled: true,
    enableRetinaScaling: true,
    skipOffscreen: true,
    stateful: false,
    
    // Interaction settings
    selection: options.selection !== undefined ? options.selection : true,
    fireRightClick: options.fireRightClick || false,
    stopContextMenu: options.stopContextMenu || false,
    isDrawingMode: options.isDrawingMode || false,
    
    // Canvas dimensions (can be overridden)
    width: options.width || 800,
    height: options.height || 600,
    
    // Additional custom options
    ...options
  };
  
  /**
   * Initialize the canvas with optimized settings
   */
  const initCanvas = () => {
    if (isInitialized.value) {
      console.warn(`Canvas ${canvasId} is already initialized`);
      return;
    }
    
    try {
      // Create canvas with merged options
      canvas.value = new fabric.Canvas(canvasId, defaultOptions);
      
      // Apply additional performance settings
      if (options.performanceMode !== false) {
        // Batch rendering for better performance
        canvas.value.renderOnAddRemove = false;
        
        // Optimize object caching
        fabric.Object.prototype.objectCaching = true;
        fabric.Object.prototype.noScaleCache = false;
        fabric.Object.prototype.strokeUniform = true;
      }
      
      isInitialized.value = true;
      
      // Set up resize observer if container provided
      if (options.containerRef) {
        setupResizeObserver(options.containerRef);
      }
      
    } catch (error) {
      console.error(`Failed to initialize canvas ${canvasId}:`, error);
      throw error;
    }
  };
  
  /**
   * Throttled render function for better performance
   */
  let renderTimeout: NodeJS.Timeout | null = null;
  const throttledRender = () => {
    if (renderTimeout) {
      clearTimeout(renderTimeout);
    }
    renderTimeout = setTimeout(() => {
      if (canvas.value) {
        canvas.value.renderAll();
      }
      renderTimeout = null;
    }, 16); // ~60fps
  };
  
  /**
   * Batch render multiple operations
   */
  const batchRender = (operations: () => void) => {
    if (!canvas.value) return;
    
    // Disable rendering during batch operations
    canvas.value.renderOnAddRemove = false;
    
    try {
      // Execute all operations
      operations();
    } finally {
      // Re-enable and trigger single render
      canvas.value.renderOnAddRemove = defaultOptions.renderOnAddRemove;
      canvas.value.requestRenderAll();
    }
  };
  
  /**
   * Clear all objects from canvas
   */
  const clearCanvas = () => {
    if (!canvas.value) return;
    
    batchRender(() => {
      canvas.value!.clear();
      canvas.value!.set({ backgroundColor: options.backgroundColor || null });
    });
  };
  
  /**
   * Add object(s) to canvas with batch rendering
   */
  const addObjects = (objects: fabric.Object | fabric.Object[]) => {
    if (!canvas.value) return;
    
    const objectArray = Array.isArray(objects) ? objects : [objects];
    
    batchRender(() => {
      objectArray.forEach(obj => {
        if (obj && canvas.value) {
          canvas.value.add(obj);
        }
      });
    });
  };
  
  /**
   * Remove object(s) from canvas with batch rendering
   */
  const removeObjects = (objects: fabric.Object | fabric.Object[]) => {
    if (!canvas.value) return;
    
    const objectArray = Array.isArray(objects) ? objects : [objects];
    
    batchRender(() => {
      objectArray.forEach(obj => {
        if (obj && canvas.value) {
          canvas.value.remove(obj);
        }
      });
    });
  };
  
  /**
   * Set background image with proper scaling
   */
  const setBackgroundImage = (imageUrl: string, options: CanvasOptions = {}) => {
    if (!canvas.value || !imageUrl) return;
    
    return fabric.FabricImage.fromURL(imageUrl, {}, {
        crossOrigin: 'anonymous'
      })
        .then((img) => {
          if (!canvas.value) {
            throw new Error('Canvas not available');
          }
          
          // Default scaling to fit canvas
          const scaleX = options.scaleX || (canvas.value.width / img.width);
          const scaleY = options.scaleY || (canvas.value.height / img.height);
          
          img.set({
            scaleX: options.stretch ? scaleX : Math.min(scaleX, scaleY),
            scaleY: options.stretch ? scaleY : Math.min(scaleX, scaleY),
            ...options
          });
          
          canvas.value.set({ backgroundImage: img });
          canvas.value.renderAll();
          return img;
        });
  };
  
  /**
   * Export canvas as data URL
   */
  const toDataURL = (options: CanvasOptions = {}) => {
    if (!canvas.value) return null;
    
    return canvas.value.toDataURL({
      format: (options.format || 'jpeg') as any,
      quality: options.quality || 0.9,
      multiplier: options.multiplier || 1,
      ...options
    });
  };
  
  /**
   * Set up resize observer for responsive canvas
   */
  const setupResizeObserver = (containerRef: { value: HTMLElement | null }) => {
    if (!containerRef || !containerRef.value) return;
    
    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const { width, height } = entry.contentRect;
        resizeCanvas(width, height);
      }
    });
    
    resizeObserver.observe(containerRef.value);
    
    // Clean up on unmount
    onUnmounted(() => {
      resizeObserver.disconnect();
    });
  };
  
  /**
   * Resize canvas maintaining aspect ratio
   */
  const resizeCanvas = (width: number, height: number) => {
    if (!canvas.value) return;
    
    canvas.value.setDimensions({
      width: width,
      height: height
    });
    
    canvas.value.calcOffset();
    canvas.value.renderAll();
  };
  
  /**
   * Dispose canvas and clean up resources
   */
  const dispose = () => {
    if (renderTimeout) {
      clearTimeout(renderTimeout);
      renderTimeout = null;
    }
    
    if (canvas.value) {
      try {
        // Clear all objects
        canvas.value.clear();
        
        // Remove all event listeners
        canvas.value.off();
        
        // Dispose the canvas
        canvas.value.dispose();
        
      } catch (error) {
        console.warn(`Error disposing canvas ${canvasId}:`, error);
      } finally {
        canvas.value = null;
        isInitialized.value = false;
      }
    }
  };
  
  // Auto-dispose on component unmount
  onUnmounted(() => {
    dispose();
  });
  
  return {
    // Canvas instance
    canvas,
    isInitialized,
    
    // Core functions
    initCanvas,
    clearCanvas,
    dispose,
    
    // Rendering functions
    throttledRender,
    batchRender,
    
    // Object management
    addObjects,
    removeObjects,
    
    // Image handling
    setBackgroundImage,
    toDataURL,
    
    // Canvas manipulation
    resizeCanvas
  };
}

// Export as default for convenience
export default useFabricCanvas;