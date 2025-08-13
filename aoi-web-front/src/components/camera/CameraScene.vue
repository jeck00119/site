<template>
    <div id="canvas-container" :style="{width: width, height: height}" ref="canvasContainer">
        <canvas :id="canvasId" :style="{width: '100%', height: '100%'}" ref="canvasElement"></canvas>
    </div>
</template>

<script>
import * as fabric from 'fabric';
import { ref, watch, onMounted, toRef, onUnmounted, onBeforeUnmount } from 'vue';

import { useWebSocket, useFabricCanvas, useGraphicsStore, useErrorsStore, useImageSourcesStore } from '@/composables/useStore';
import { DEFAULT_IMAGE_DATA_URI_PREFIX, ImageDataUtils } from '@/utils/imageConstants';
import { createLogger } from '@/utils/logger';
import { addErrorToStore } from '@/utils/errorHandler';
import { canvasRegistry } from '@/utils/canvasRegistry';

export default {
    props: ['width', 'height', 'show', 'feedLocation', 'cameraFeed', 'staticImages', 'id', 'canvasId', 'graphics', 'imageFileName', 'overlay'],

    emits: ['graphics-changed', 'graphic-selected', 'graphic-cleared', 'graphic-modified'],

    setup(props, context) {
        const imageSource = ref(null);
        const canvasContainer = ref(null);
        const canvasElement = ref(null);
        const logger = createLogger('CameraScene');
        const { setCanvas } = useGraphicsStore();
        const { addError } = useErrorsStore();
        const { dispatch: dispatchImageSources, store } = useImageSourcesStore();

        const graphics = toRef(props, 'graphics');
        const feedLocation = toRef(props, 'feedLocation');
        const show = toRef(props, 'show');
        const staticImages = toRef(props, 'staticImages');
        const overlay = toRef(props, 'overlay');
        const imageFileName = toRef(props, 'imageFileName');

        let staticImagesOffset = 0;
        const staticImagesMargin = 20;

        let ws_uid = null;
        
        // Image cache cleanup
        let imageCleanupInterval = null;
        const imageCache = new Map();
        
        // WebSocket connection management
        let webSocketInstance = null;
        
        function connectToCamera() {
            // Disconnect existing connection if any
            if (webSocketInstance) {
                webSocketInstance.disconnect();
                webSocketInstance = null;
            }
            
            ws_uid = crypto.randomUUID();
            const wsUrl = props.feedLocation + `/${ws_uid}`;
            
            // Create new WebSocket connection using the centralized composable
            webSocketInstance = useWebSocket(wsUrl, {
                autoConnect: true,
                reconnectAttempts: 5,
                reconnectInterval: 2000,
                onOpen: onSocketOpen,
                onMessage: imageReceived,
                onError: onSocketError,
                onClose: onSocketClose
            });
        };

        function disconnectFromCamera() {
            if(ws_uid){
                try {
                    dispatchImageSources("imageSources/closeImageSourceSocket", {
                        uid: ws_uid
                    });
                } catch (error) {
                    logger.warn('Error during socket disconnect', error);
                } finally {
                    ws_uid = null;
                }
            }
            
            // Use the centralized disconnect if websocket exists
            if (webSocketInstance) {
                webSocketInstance.disconnect();
                webSocketInstance = null;
            }
        };
        
        // Reconnection is now handled by the useWebSocket composable
        
        function onSocketError(event) {
            logger.webSocket('error', event);
            addError({ title: 'Camera Connection Error', message: 'Failed to connect to camera feed' });
        }
        
        function onSocketClose(event) {
            logger.webSocket('close', { code: event.code, reason: event.reason });
        }

        function onSocketOpen() {
            try {
                logger.webSocket('open');
                if (webSocketInstance && webSocketInstance.isConnected.value) {
                    webSocketInstance.send('eses');
                }
            } catch (error) {
                logger.error('Error sending initial message to camera websocket', error);
                addError({ title: 'Camera Communication Error', message: error });
            }
        }

        function imageReceived(event) {
            try {
                // Validate event data
                if (!event.data || event.data.size === 0) {
                    return;
                }
                
                // The backend sends base64 encoded JPEG data as bytes
                // We need to decode the base64 and create a proper image URL
                const reader = new FileReader();
                reader.onload = function(e) {
                    try {
                        // Convert ArrayBuffer to text (base64 string)
                        const base64String = new TextDecoder().decode(e.target.result);
                        
                        // Create optimized data URL from base64 (backend sends JPEG by default)
                        const imageUrl = ImageDataUtils.createJpegDataURI(base64String);
                        
                        // Clean up previous image from cache
                        if (imageSource.value && imageCache.has(imageSource.value)) {
                            try {
                                URL.revokeObjectURL(imageSource.value);
                            } catch (e) {
                                // Not an object URL, ignore
                            }
                            imageCache.delete(imageSource.value);
                        }
                        
                        // Update image source
                        imageSource.value = imageUrl;
                        imageCache.set(imageUrl, Date.now());
                        
                        // Clean up old cached images periodically
                        cleanupImageCache();
                        
                    } catch (error) {
                        logger.error('Error processing image data from camera', error);
                        addErrorToStore(store, 'Image Processing Error', error);
                    }
                };
                
                reader.onerror = function(error) {
                    logger.error('FileReader error while processing camera image', error);
                    addErrorToStore(store, 'Image Reading Error', error);
                };
                
                reader.readAsArrayBuffer(event.data);
                
            } catch (error) {
                logger.error('Error handling received image from camera', error);
                addErrorToStore(store, 'Camera Image Error', error);
            }
        }
        
        function cleanupImageCache() {
            const now = Date.now();
            const maxAge = 60000; // 1 minute
            
            for (const [url, timestamp] of imageCache.entries()) {
                if (now - timestamp > maxAge) {
                    imageCache.delete(url);
                    // Only revoke object URLs, not data URLs
                    if (url.startsWith('blob:')) {
                        URL.revokeObjectURL(url);
                    }
                }
            }
        }

        function createFabricObject(obj) {
            if (obj.type === 'rect') {
                return new fabric.Rect(obj);
            } else if (obj.type === 'circle') {
                return new fabric.Circle(obj);
            }
            // Add more types if needed
            return null;
        }

        function addRectangles(graphics) {
            // Validate graphics is iterable
            if (!graphics || !Array.isArray(graphics)) {
                logger.debug('Graphics is not a valid array', { graphics, type: typeof graphics });
                return;
            }

            for(const graphicData of graphics)
            {
                const graphic = createFabricObject(graphicData);
                if (graphic) {
                    // Optimize graphics with performance settings
                    graphic.set({
                        objectCaching: true,
                        statefullCache: true,
                        noScaleCache: false
                    });
                    
                    graphic.on('rotating', function(event) {
                        context.emit('graphics-changed', event.transform.target);
                    });

                    graphic.on('scaling', function(event) {
                        context.emit('graphics-changed', event.transform.target);
                    });

                    graphic.on('moving', function(event) {
                        context.emit('graphics-changed', event.transform.target);
                    });

                    graphic.on('modified',  function(event) {
                        context.emit('graphic-modified', event.transform.target);
                    });

                    if (canvas.value) {
                        canvas.value.add(graphic);
                        canvas.value.setActiveObject(graphic);
                        canvas.value.bringObjectToFront(graphic);
                    }
                }
            }
            
            // Single render after all graphics are added
            throttledRender();
        }

        function removeRectangles() {
            if (!canvas.value) return;
            
            const objects = canvas.value.getObjects();

            objects.forEach(function(item, _) {
                if(item.type === 'rect')
                {
                    canvas.value.remove(item);
                }
            });
            throttledRender();
        }

        function removeCircles() {
            if (!canvas.value) return;
            
            const objects = canvas.value.getObjects();

            objects.forEach(function(item, _) {
                if(item.type === 'circle')
                {
                    canvas.value.remove(item);
                }
            });
            throttledRender();
        }

        function graphicsObjectsEqual(g1, g2) {
            return Object.keys(g1).length === Object.keys(g2).length && Object.keys(g1).every(p => g1[p] === g2[p]);
        }

        function graphicsArraysEqual(a1, a2) {
            return a1.length === a2.length && a1.every((o, idx) => graphicsObjectsEqual(o, a2[idx]));
        }

        watch(graphics, (newValue, oldValue) => {
            if(!graphicsArraysEqual(newValue, oldValue))
            {
                removeRectangles();
                removeCircles();
                addRectangles(graphics.value);
                // Render is handled by addRectangles function
            }
        });

        watch(feedLocation, (newValue) => {
            try {
                if(newValue) {
                    disconnectFromCamera();
                    setTimeout(() => {
                        connectToCamera();
                    }, 100);
                } else {
                    disconnectFromCamera();
                }
            } catch (error) {
                logger.error('Error handling feed location change', error);
                addErrorToStore(store, 'Camera Feed Change Error', error);
            }
        });

        watch(show, (newValue) => {
            if(!newValue)
            {
                disconnectFromCamera();
                removeImages();
            }

            if(newValue && props.cameraFeed)
            {
                removeImages();
                connectToCamera();
            }
        });

        watch(staticImages, async (newValue) => {
            if(!show.value)
            {
                staticImagesOffset = 0;
                removeImages();
                if(newValue) {
                    // Process images sequentially to avoid race conditions
                    for(let i = 0; i < newValue.length; i++)
                    {
                        // Skip empty or invalid URLs
                        if(newValue[i] && typeof newValue[i] === 'string' && newValue[i].trim() !== '') {
                            await addStaticImage(newValue[i]);
                        }
                    }
                    
                    // Single render call after all images are added for better performance
                    throttledRender();
                }
            }
        });

        watch(overlay, (newValue) => {
            if(newValue)
            {
                removeImages();
                // Fabric.js v6: Use direct property assignment instead of setOverlayImage
                if (canvas.value) {
                    canvas.value.overlayImage = newValue;
                    throttledRender();
                }
            }
        });

        watch(imageFileName, (newValue) => {
            if(newValue && canvas.value && canvas.value.backgroundImage)
            {
                let link = document.createElement('a');
                link.href = canvas.value.backgroundImage.getSrc().replace(/^data:image\/[^;]/, 'data:application/octet-stream');
                link.download = newValue.split('.')[0] + '.jpeg';
                link.click();
            }
        });

        watch(imageSource, (newValue) => {
            if(show.value && canvas.value && newValue) {
                // Dispose previous background image to prevent memory leaks
                if (canvas.value.backgroundImage) {
                    try {
                        canvas.value.backgroundImage.dispose();
                    } catch (e) {
                        // Image may already be disposed
                    }
                }
                
                // Fabric.js v6: Create FabricImage from HTML Image element with optimizations
                const img = new Image();
                img.onload = function() {
                    if (canvas.value) {
                        try {
                            const fabricImg = new fabric.FabricImage(img, {
                                // Performance optimizations for background image
                                objectCaching: true,
                                statefullCache: true,
                                noScaleCache: false,
                                evented: false
                            });
                            
                            canvas.value.set({ backgroundImage: fabricImg });
                            
                            // Use throttled rendering for smooth performance
                            throttledRender();
                        } catch (err) {
                            logger.error('Error creating Fabric image from camera feed', err);
                            addErrorToStore(store, 'Canvas Rendering Error', err);
                        }
                    }
                };
                img.onerror = function(err) {
                    logger.error('Error loading background image', err);
                    addErrorToStore(store, 'Background Image Error', err);
                };
                
                // Set crossOrigin for better performance and caching
                img.crossOrigin = 'anonymous';
                img.src = newValue;
            }
        });

        function addStaticImage(url) {
            return new Promise((resolve, reject) => {
                if (!canvas.value) {
                    const error = new Error('Canvas not initialized');
                    logger.error('Canvas not initialized when trying to add static image', error);
                    addErrorToStore(store, 'Canvas Error', error);
                    reject(error);
                    return;
                }
                
                if (!url || typeof url !== 'string') {
                    const error = new Error('Invalid URL');
                    logger.error('Invalid URL provided to addStaticImage', { url });
                    addErrorToStore(store, 'Image URL Error', error);
                    reject(error);
                    return;
                }
                
                // Load image using Fabric.js v6 with performance optimizations
                fabric.FabricImage.fromURL(url, {}, {
                    // Performance optimizations
                    crossOrigin: 'anonymous'
                })
                    .then(img => {
                        // Set properties with performance optimizations
                        img.set({
                            top: 0, 
                            left: staticImagesOffset, 
                            selectable: false,
                            evented: false, // Disable event handling for better performance
                            objectCaching: true, // Enable object caching
                            statefullCache: true, // Enable stateful cache
                            noScaleCache: false, // Enable scale cache
                            strokeUniform: true
                        });
                        
                        staticImagesOffset += img.width + staticImagesMargin;
                        if (canvas.value) {
                            canvas.value.add(img);
                            canvas.value.sendObjectToBack(img);
                        }
                        
                        // Don't render here - batch rendering is handled by the caller
                        
                        resolve(img);
                    })
                    .catch(err => {
                        logger.error('Error loading static image with Fabric.js', err);
                        addErrorToStore(store, 'Static Image Loading Error', err);
                        reject(err);
                    });
            });
        }

        function removeImages() {
            if (!canvas.value) return;
            
            const objects = canvas.value.getObjects();

            objects.forEach(function(object, _) {
                if(object.type === 'image')
                {
                    canvas.value.remove(object);
                }
            });

            // Fabric.js v6: Use direct property assignment instead of setBackgroundImage
            canvas.value.backgroundImage = null;
            throttledRender();
        }

        function selectionChanged(obj)
        {
            context.emit('graphic-selected', obj.selected[0]);
        }

        function selectionCleared() {
            context.emit('graphic-cleared');
        }

        // Initialize canvas with centralized composable
        const {
            canvas,
            initCanvas,
            clearCanvas,
            addObjects,
            removeObjects,
            setBackgroundImage,
            throttledRender,
            batchRender
        } = useFabricCanvas(props.canvasId, {
            // Performance optimizations
            renderOnAddRemove: false,
            skipTargetFind: false,
            imageSmoothingEnabled: true,
            enableRetinaScaling: true,
            allowTouchScrolling: false,
            selection: true,
            preserveObjectStacking: true,
            performanceMode: true,
            containerRef: canvasContainer
        });

        onMounted(() => {
            logger.lifecycle('mounted', 'CameraScene component mounted');
            initCanvas();
            
            // Start periodic image cache cleanup
            imageCleanupInterval = setInterval(cleanupImageCache, 30000); // Every 30 seconds

            if (canvas.value) {
                canvas.value.setHeight(canvasContainer.value.clientHeight);
                canvas.value.setWidth(canvasContainer.value.clientWidth);
            }

            const resizeObserver = new ResizeObserver(() => {
                if(canvasContainer.value && canvas.value)
                {
                    canvas.value.setHeight(canvasContainer.value.clientHeight);
                    canvas.value.setWidth(canvasContainer.value.clientWidth);
                }
            });

            resizeObserver.observe(canvasContainer.value);

            if(!props.cameraFeed && props.staticImages)
            {
                staticImagesOffset = 0;
                removeImages();
                // Process images sequentially
                (async () => {
                    for(const img of props.staticImages)
                    {
                        try {
                            await addStaticImage(img);
                        } catch (err) {
                            logger.error('Error adding static image on mount', err);
                            addErrorToStore(store, 'Static Image Mount Error', err);
                        }
                    }
                })();
            }

            if (canvas.value) {
                canvas.value.on('mouse:down', function(opt) {
                    let evt = opt.e;
                    if (evt.altKey === true) {
                        this.isDragging = true;
                        this.selection = false;
                        this.lastPosX = evt.clientX;
                        this.lastPosY = evt.clientY;
                    }
                });
            }

            if (canvas.value) {
                canvas.value.on('mouse:move', function(opt) {
                    if (this.isDragging) {
                        let e = opt.e;
                        let vpt = this.viewportTransform;
                        vpt[4] += e.clientX - this.lastPosX;
                        vpt[5] += e.clientY - this.lastPosY;
                        this.requestRenderAll();
                        this.lastPosX = e.clientX;
                        this.lastPosY = e.clientY;
                    }
                });
            }

            if (canvas.value) {
                canvas.value.on('mouse:up', function() {
                    this.setViewportTransform(this.viewportTransform);
                    this.isDragging = false;
                    this.selection = true;
                });
            }

            if (canvas.value) {
                canvas.value.on("mouse:wheel", (opt) => {
                    let delta = opt.e.deltaY;
                    let zoom = canvas.value.getZoom();
                    zoom *= 0.999 ** delta;
                    if (zoom > 20) zoom = 20;
                    if (zoom < 0.01) zoom = 0.01;
                    canvas.value.zoomToPoint({
                        x: opt.e.offsetX,
                        y: opt.e.offsetY
                    },
                    zoom
                    );
                    opt.e.preventDefault();
                    opt.e.stopPropagation();
                });
            }

            if (canvas.value) {
                canvas.value.on({
                    'selection:updated': selectionChanged,
                    'selection:created': selectionChanged
                });
            }

            if (canvas.value) {
                canvas.value.on({
                    'selection:cleared': selectionCleared
                });
            }

            if(props.cameraFeed && canvas.value) {
                // Register canvas with registry and store ID in Vuex
                canvasRegistry.register(props.canvasId, canvas.value);
                setCanvas(props.canvasId);
            }

            addRectangles(props.graphics);

            if(overlay.value && canvas.value)
            {
                // Fabric.js v6: Use direct property assignment instead of setOverlayImage
                canvas.value.overlayImage = overlay.value;
                throttledRender();
            }
        });

        onBeforeUnmount(() => {
            try {
                logger.lifecycle('beforeUnmount', 'CameraScene component before unmount');
                // Clean up canvas objects
                removeImages();
                removeRectangles();
                removeCircles();
                
                // Dispose canvas background and overlay images
                if (canvas.value) {
                    if (canvas.value.backgroundImage) {
                        try {
                            canvas.value.backgroundImage.dispose();
                        } catch (e) {
                            // Already disposed
                        }
                    }
                    if (canvas.value.overlayImage) {
                        try {
                            canvas.value.overlayImage.dispose();
                        } catch (e) {
                            // Already disposed
                        }
                    }
                }
                
                // Clean up image cache
                for (const [url] of imageCache.entries()) {
                    // Only revoke object URLs, not data URLs
                    if (url.startsWith('blob:')) {
                        URL.revokeObjectURL(url);
                    }
                }
                imageCache.clear();
                
                // Clear cleanup interval
                if (imageCleanupInterval) {
                    clearInterval(imageCleanupInterval);
                    imageCleanupInterval = null;
                }
                
            } catch (error) {
                logger.warn('Error during CameraScene cleanup', error);
            }
        });

        onUnmounted(() => {
            try {
                logger.lifecycle('unmounting', 'CameraScene component unmounting');
                // Disconnect from camera
                disconnectFromCamera();
                
                // Unregister canvas from registry
                if (props.canvasId) {
                    canvasRegistry.unregister(props.canvasId);
                }
                
                // Dispose canvas completely
                if (canvas.value) {
                    canvas.value.dispose();
                }
                
            } catch (error) {
                logger.warn('Error during CameraScene component unmounting', error);
            }
        });

        return {
            canvasContainer,
            canvasElement
        };
    }
}
</script>

<style scoped>
    #canvas-container {
        background-color: rgb(0, 0, 0);
        /* background-color: red; */
    }

    canvas {
        width: 900px;
        height: 755px;
    }
</style>