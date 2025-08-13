<template>
    <div class="flex-container">
        <div class="camera-wrapper">
            <div class="camera-scene-item">
                <camera-scene width="45vw" height="45vh" :show="show" :camera-feed="true" :feed-location="feedLocation"
                    :static-images="[imageEncoding]" canvas-id="camera-scene-canvas" :graphics="currentGraphics"
                    @graphics-changed="updateGraphics" @graphic-selected="selectionChanged"
                    @graphic-cleared="selectionCleared" @graphic-modified="selectionModified"></camera-scene>
            </div>
            <div class="camera-scene-item">
                <camera-scene width="45vw" height="45vh" :camera-feed="false" :static-images="outputImages"
                    canvas-id="result-canvas" :graphics="[]"></camera-scene>
            </div>
        </div>
        <div class="actions-wrapper">
            <div class="file-selector">
                <directory-files-list width="45vw" height="45vh" @files-dropped="readImage"
                    @image-source-changed="updateImageSource" @start-camera="startCamera" @stop-camera="stopCamera"
                    @reset-camera-scene="resetCameraScene"></directory-files-list>
            </div>
            <div class="algorithm-control">
                <algorithm-debug-control :algorithms="algorithms" :reference-algorithms="referenceAlgorithms"
                    :current-algorithm="currentAlgorithm" :algorithm-attributes="algorithmAttributes"
                    :parameters="parameters" :current-reference-algorithm="currentReferenceAlgorithm"
                    :reference-algorithm-attributes="referenceAlgorithmAttributes"
                    :reference-parameters="referenceParameters" width="45vw" height="45vh"
                    :disable-actions="disableProcessButton" @reference-changed="referenceChanged"
                    @algorithm-changed="algorithmChanged" @import-path-changed="importPathChanged"
                    @download-algorithm="downloadAlgorithm" @single-run="singleRunAlgorithm"
                    @live-process="liveProcessAlgorithm" @single-run-reference="singleRunReference"
                    @live-process-reference="liveProcessReference" @tab-changed="tabChangedDebug"></algorithm-debug-control>
            </div>
        </div>
        <button class="rounded-button" @click="showMasks = true" v-if="!showMasks" :disabled="disableRoiMasks">ROI</button>
        <div class="roi-masks" v-else>
            <mask-scene :graphics="selectedGraphic" :image-source-id="currentImageSourceId" canvas-id="mask-scene"
                width="100%" height="100%" @closed="showMasks = false" @save="saveMasks"></mask-scene>
        </div>
        <base-dialog
            :show="showSelectReferenceDialog"
            title="Multiple potential references found. Choose one."
            height="50vh"
            @close="closeSelectReferenceDialog"
        >
            <template #default>
                <camera-scene width="100%" height="35vh" :camera-feed="false" :static-images="[]" :overlay="resultImage !== undefined ? resultImage : ''"
                    canvas-id="reference-canvas" :graphics="[referenceOverlay, hole, circleRefPoint]">
                </camera-scene>
                <div class="choices">
                    <button class="reference-choice" v-for="idx in referenceToSave.length" :key="idx" :class="{'selected-reference': currentReferencePointIdx === idx - 1}" @click="changeReferencePoint(idx - 1)">{{idx}}</button>
                </div>
            </template>
            <template #actions>
                <div class="action-control">
                    <base-button width="7vw" mode="flat" @click="closeSelectReferenceDialog">Ok</base-button>
                </div>
            </template>
        </base-dialog>
        <base-notification
            :show="showNotification"
            height="15vh"
            :timeout="notificationTimeout"
            @close="clearNotification"
        >
            <div class="message-wrapper">
                <div class="icon-wrapper">
                    <v-icon :name="notificationIcon" scale="2.5" animation="pulse"/>
                </div>
                <div class="text-wrapper">
                    {{ notificationMessage }}
                </div>
            </div>
        </base-notification>
    </div>
</template>

<script>
// Vue and utilities
import { ref, computed, watch, onBeforeUnmount, onMounted } from 'vue';
import { useStore } from 'vuex';
import { uuid } from "vue3-uuid";
import * as fabric from 'fabric';

// Component imports
import CameraScene from '../../camera/CameraScene.vue';
import DirectoryFilesList from '../../layout/DirectoryFilesList.vue';
import AlgorithmDebugControl from '../../layout/AlgorithmDebugControl.vue';
import MaskScene from '../../layout/MaskScene.vue';

// CENTRALIZED IMPORTS - Using all modern centralized patterns
import { useFabricCanvas } from '@/composables/useFabricCanvas';
import graphic from '@/utils/graphics.js';
import { 
    useAlgorithmsStore, 
    useGraphicsStore, 
    useConfigurationsStore, 
    useImageSourcesStore, 
    useErrorsStore,
    useWebSocket, 
    useLoadingState,
    useAuthStore
} from '@/composables/useStore';
import { api } from '@/utils/api';
import { addErrorToStore, handleApiError } from '@/utils/errorHandler';
import { createLogger } from '@/utils/logger';

export default {
    components: {
        CameraScene,
        DirectoryFilesList,
        AlgorithmDebugControl,
        MaskScene
    },

    setup() {
        // CENTRALIZED LOGGING
        const logger = createLogger('AlgorithmDebug');
        logger.lifecycle('setup', 'Initializing AlgorithmDebug with centralized patterns');

        // CENTRALIZED STORE COMPOSABLES - All using modern patterns
        const store = useStore(); // For backward compatibility with existing functions
        const algorithmsStore = useAlgorithmsStore();
        const graphicsStore = useGraphicsStore();
        const configurationsStore = useConfigurationsStore();
        const imageSourcesStore = useImageSourcesStore();
        const errorsStore = useErrorsStore();
        const authStore = useAuthStore();

        // CENTRALIZED LOADING STATE
        const { isLoading, setLoading, withLoading } = useLoadingState();

        // CENTRALIZED FABRIC CANVAS MANAGEMENT
        const { 
            canvas, 
            initializeCanvas, 
            addBackgroundImage, 
            renderCanvas,
            dispose 
        } = useFabricCanvas('camera-scene-canvas', {
            width: 800,
            height: 600,
            selection: true
        });

        // Component state
        const show = ref(false);
        const showMasks = ref(false);
        const feedLocation = ref('');
        const currentImageSourceId = ref(null);
        const imageEncoding = ref('');
        const disableActions = ref(true);
        const selectedTabSource = ref("Image Source");
        const selectedTabDebug = ref("References");
        const importFilePath = ref('');
        const loadedAlgorithm = ref(null);
        const currentReferenceName = ref(null);
        const currentAlgorithmName = ref(null);
        const referenceToSave = ref([]);
        const currentReferencePointIdx = ref(-1);
        const showSelectReferenceDialog = ref(false);
        const referenceOverlay = ref(null);
        const hole = ref(null);
        const circleRefPoint = ref(null);

        // CENTRALIZED WEBSOCKET MANAGEMENT
        let liveProcessSocket = null;

        // CENTRALIZED NOTIFICATION SYSTEM (migrate from old hook)
        const showNotification = ref(false);
        const notificationMessage = ref('');
        const notificationIcon = ref('');
        const notificationTimeout = ref(3000);

        const setNotification = (timeout, message, icon) => {
            notificationTimeout.value = timeout || 3000;
            notificationMessage.value = message || '';
            notificationIcon.value = icon || 'info';
            showNotification.value = true;
        };

        const clearNotification = () => {
            showNotification.value = false;
            notificationMessage.value = '';
            notificationIcon.value = '';
        };

        // CENTRALIZED COMPUTED PROPERTIES - Using centralized store composables
        const algorithms = computed(() => {
            // Get algorithms directly from the centralized store
            // These are already computed refs from the composables

            const algs = algorithmsStore.algorithms;
            
            // Ensure we always return an array
            let result = [];
            if (Array.isArray(algs)) {
                result = algs;
            } else if (!algs) {
                result = [];
            }
            
            logger.debug('algorithms computed:', { 
                count: result.length,
                algorithms: result
            });
            
            return result;
        });

        const configuredAlgorithms = computed(() => {
            // Get configured algorithms directly from the centralized store
            const configAlgs = algorithmsStore.configuredAlgorithms;
            
            // Ensure we always return an array
            let result = [];
            if (Array.isArray(configAlgs)) {
                result = configAlgs;
            } else if (!configAlgs) {
                result = [];
            }
            
            logger.debug('configuredAlgorithms computed:', { 
                count: result.length,
                algorithms: result
            });
            
            // Debug: Log the actual structure of configured algorithms
            if (result.length > 0) {
                logger.debug('First configured algorithm structure:', { 
                    algorithm: result[0], 
                    keys: Object.keys(result[0]),
                    uid: result[0].uid,
                    type: result[0].type,
                    stringified: JSON.stringify(result[0])
                });
            }
            
            return result;
        });

        const currentAlgorithm = algorithmsStore.currentAlgorithm;
        const algorithmAttributes = computed(() => {
            // Get the algorithm attributes (UI schema) from the store
            const attrs = algorithmsStore.algorithmAttributes;
            
            // Ensure we always return an array
            let result = [];
            if (Array.isArray(attrs)) {
                result = attrs;
            } else if (!attrs) {
                result = [];
            }
            
            logger.debug('algorithmAttributes computed:', { 
                count: result.length,
                attributes: result 
            });
            
            return result;
        });
        const resultImage = computed(() => {
            const result = algorithmsStore.algorithmResult;
            if(result && result.frame) {
                if(Array.isArray(result.frame) && result.frame.length === 0) {
                    return '';
                }
                else if(Array.isArray(result.frame)) {
                    return result.frame[0];
                }
                else {
                    return result.frame;
                }
            }
            return '';
        });
        
        const outputImages = computed(() => {
            const result = algorithmsStore.algorithmResult;
            let outputImages = [];
            if(result && result.frame) {
                outputImages = Array.isArray(result.frame) ? result.frame : [result.frame];
            }
            return outputImages;
        });
        const parameters = computed(() => {
            if(currentAlgorithm.value && currentAlgorithm.value.parameters)
                return currentAlgorithm.value.parameters;
            else
                return [];
        });
        
        // CENTRALIZED GRAPHICS MANAGEMENT
        const graphicItems = computed(() => graphicsStore.graphicsItems || []);
        const selectedGraphic = graphicsStore.selectedGraphic;
        const graphicsObject = ref(null);
        
        // CENTRALIZED GRAPHICS FUNCTIONS - Using centralized utilities
        function updateGraphics() {
            try {
                // Use centralized canvas from useFabricCanvas
                if (canvas.value && graphicItems.value) {
                    // This would use centralized graphics utility if available
                    // For now, maintain compatibility with existing system
                    const graphicsData = {
                        items: graphicItems.value,
                        canvas: canvas.value
                    };
                    graphicsObject.value = graphicsData;
                    logger.debug('Graphics updated via centralized pattern');
                }
            } catch (error) {
                logger.error('Failed to update graphics', error);
                addErrorToStore(errorsStore, 'Graphics Update Error', error);
            }
        }
        
        function selectionChanged(rect) {
            try {
                if (rect && canvas.value) {
                    // Use centralized graphics store for selection
                    graphicsStore.selectGraphic(rect);
                    logger.debug('Selection changed via centralized pattern');
                }
            } catch (error) {
                logger.error('Failed to handle selection change', error);
                addErrorToStore(errorsStore, 'Graphics Selection Error', error);
            }
        }
        
        function selectionCleared() {
            try {
                graphicsStore.selectGraphic(null);
                logger.debug('Selection cleared via centralized pattern');
            } catch (error) {
                logger.error('Failed to clear selection', error);
                addErrorToStore(errorsStore, 'Graphics Clear Error', error);
            }
        }
        
        function selectionModified(obj) {
            try {
                if (obj === selectedGraphic.value) {
                    graphicsStore.selectGraphic(obj);
                    logger.debug('Selection modified via centralized pattern');
                }
            } catch (error) {
                logger.error('Failed to handle selection modification', error);
                addErrorToStore(errorsStore, 'Graphics Modification Error', error);
            }
        }
        
        function saveMasks(polygons) {
            const masks = [];
            const masksColors = [];
            
            for (const polygon of polygons) {
                const points = [];
                const updatedPoints = graphic.getUpdatedPolygonPoints(polygon, canvas.value);
                
                for (let i = 0; i < updatedPoints.length; i++) {
                    points.push([updatedPoints[i].x, updatedPoints[i].y]);
                }
                
                masks.push(points);
                
                let hexColor = polygon.fill;
                let r = parseInt(hexColor.substring(1, 3), 16);
                let g = parseInt(hexColor.substring(3, 5), 16);
                let b = parseInt(hexColor.substring(5, 7), 16);
                
                masksColors.push([r, g, b]);
            }
            
            if (selectedGraphic.value) {
                selectedGraphic.value.masks = masks;
                selectedGraphic.value.masksColors = masksColors;
                let data = graphic.getRectProps(selectedGraphic.value, canvas.value);
                centralGraphicsStore.selectGraphic(data);
            }
        }
        
        // CENTRALIZED API CALLS - Using centralized API utility
        async function loadUIandAlgorithm(type, uid) {
            logger.debug('loadUIandAlgorithm started', { type, uid });
            try {
                await withLoading(async () => {
                    logger.debug('Loading algorithm via centralized API', { type, uid });
                    
                    // ALWAYS load the UI schema first (parameter definitions)
                    await algorithmsStore.loadAlgorithm({ type });
                    
                    // Set the live algorithm on the backend
                    await algorithmsStore.setLiveAlgorithm({ type });
                    
                    if (uid) {
                        // Load the saved algorithm data (including saved parameter values)
                        await algorithmsStore.loadCurrentAlgorithm({ uid });
                    } else {
                        // For new algorithms, create default parameters from the UI schema
                        // Wait for algorithm attributes to be loaded before using them
                        await new Promise(resolve => setTimeout(resolve, 100)); // Small delay for reactive updates
                        
                        const attributes = algorithmsStore.algorithmAttributes;
                        logger.debug('Creating new algorithm from attributes:', { attributes });
                        
                        if (attributes && attributes.length > 0) {
                            algorithmsStore.loadCurrentAlgorithmFromParameters({
                                attributes: attributes,
                                type: type
                            });
                        } else {
                            logger.warn('No algorithm attributes available after loading algorithm', { type, attributes });
                        }
                    }
                    
                    logger.info('Algorithm loaded successfully via centralized pattern');
                    logger.debug('Algorithm state after load:', { 
                        algorithmAttributes: algorithmAttributes.value,
                        currentAlgorithm: algorithmsStore.currentAlgorithm,
                        parameters: parameters.value
                    });
                });
            } catch (error) {
                logger.error('Failed to load algorithm', error);
                addErrorToStore(errorsStore, 'Algorithm Load Error', error);
                setNotification(5000, `Failed to load algorithm: ${error.message}`, 'bi-exclamation-circle-fill');
            }
        }
        
        function download(algorithm) {
            let text = JSON.stringify(algorithm);
            const currentDate = new Date();
            
            let suffix = currentDate.getDate() + "_" + (currentDate.getMonth() + 1) + "_"
                + currentDate.getFullYear() + "_" + currentDate.getHours() + "_"
                + currentDate.getMinutes() + "_" + currentDate.getSeconds() + ".json";
                
            let filename = algorithm.type.replace(/\s/g, '') + suffix;
            
            let element = document.createElement('a');
            element.setAttribute('href', 'data:application/json;charset=utf-8,' + encodeURIComponent(text));
            element.setAttribute('download', filename);
            
            element.style.display = 'none';
            document.body.appendChild(element);
            
            element.click();
            document.body.removeChild(element);
        }
        
        // CENTRALIZED WEBSOCKET MESSAGE HANDLING
        function liveResultMsgRecv(event) {
            try {
                logger.debug('Received WebSocket message via centralized handler');
                const recvData = JSON.parse(event.data);
                
                let outputImages = [];
                if (recvData.frame && Array.isArray(recvData.frame)) {
                    for(const frame of recvData.frame) {
                        outputImages.push(`data:image/jpeg;base64,${frame}`);
                    }
                } else {
                    if (recvData.frame) {
                        outputImages.push(`data:image/jpeg;base64,${recvData.frame}`);
                    }
                }
                
                // Use centralized store dispatch
                algorithmsStore.setAlgorithmResult({
                    frame: outputImages,
                    data: recvData.data
                });
                
                // CENTRALIZED WEBSOCKET COMMUNICATION
                if(graphicsObject.value && liveProcessSocket) {
                    liveProcessSocket.send(JSON.stringify({
                        command: 'set',
                        key: 'graphics',
                        value: graphicsObject.value
                    }));
                    graphicsObject.value = null;
                    logger.debug('Graphics data sent via centralized WebSocket');
                } else if (liveProcessSocket) {
                    liveProcessSocket.send(JSON.stringify({command: ''}));
                }
                
            } catch (error) {
                logger.error('Failed to process WebSocket message', error);
                addErrorToStore(errorsStore, 'WebSocket Message Error', error);
            }
        }
        
        function setLiveAlgorithmSocket(socket) {
            liveProcessSocket = socket;
            logger.debug('Live algorithm socket set via centralized pattern');
        }

        const referenceAlgorithms = computed(() => {
            // Get reference algorithms from the centralized store
            const refAlgs = algorithmsStore.referenceAlgorithms;
            
            // Ensure we have an array before calling map
            let algorithms = [];
            if (Array.isArray(refAlgs)) {
                algorithms = refAlgs;
            } else if (!refAlgs) {
                algorithms = [];
            }
            
            // Extract only the type names for the dropdown
            const result = algorithms.map(alg => alg?.type).filter(type => type);
            
            logger.debug('referenceAlgorithms computed:', { 
                count: result.length,
                types: result
            });
            
            return result;
        });

        const currentReferenceAlgorithm = algorithmsStore.currentReferenceAlgorithm;

        const referenceAlgorithmAttributes = computed(() => {
            const attrs = algorithmsStore.currentReferenceAlgorithmAttributes;
            return Array.isArray(attrs) ? attrs : [];
        });

        const referenceParameters = computed(function () {
            if (currentReferenceAlgorithm?.value && currentReferenceAlgorithm.value.parameters)
                return currentReferenceAlgorithm.value.parameters;
            else
                return [];
        });

        const algorithmGraphics = computed(() => graphicsStore.currentGraphics || []);

        const referenceGraphics = computed(() => graphicsStore.currentReferenceGraphics || []);

        const currentGraphics = computed(function () {
            if (selectedTabDebug.value === "References")
                return referenceGraphics.value;
            else
                return algorithmGraphics.value;
        });

        const disableProcessButton = computed(function () {
            if (selectedTabSource.value === "Image Source") {
                return disableActions.value;
            }
            else {
                if (imageEncoding.value !== '') {
                    return false;
                }
                else {
                    return true;
                }
            }
        });

        const disableRoiMasks = computed(function () {
            return (!currentAlgorithm.value && !currentReferenceAlgorithm?.value) || (!currentImageSourceId.value && !imageEncoding.value);
        });

        const resultsWatch = store.watch(
            (_, getters) => getters["algorithms/getAlgorithmResult"],
            async (newValue) => {
                if (newValue && newValue.reference) {
                    referenceToSave.value = [];
                    for(let reference of newValue.reference)
                    {
                        referenceToSave.value.push([reference.x, reference.y]);
                    }
                    currentReferencePointIdx.value = 0;
                }
                else{
                    referenceToSave.value = [];
                }

                if(referenceToSave.value.length > 1)
                {
                    let imageDimensions = await getImageSize(newValue.frame);

                    referenceOverlay.value = null;
                    
                    const rect = new fabric.Rect({
                        left: 0,
                        top: 0,
                        fill: 'rgba(71, 74, 72, 0.8)',
                        width: imageDimensions.width,
                        height: imageDimensions.height,
                        objectCaching: true,
                        selectable: false,
                        hasControls: false,
                        hasBorders: false,
                        lockMovementX: true,
                        lockMovementY: true,
                        globalCompositeOperation: 'source-over'
                    });

                    referenceOverlay.value = rect;

                    const h = new fabric.Rect({
                        left: Math.floor(referenceToSave.value[0][0]) - 25,
                        top: Math.floor(referenceToSave.value[0][1]) - 25,
                        fill: '#451245',
                        width: 50,
                        height: 50,
                        objectCaching: true,
                        selectable: false,
                        hasControls: false,
                        hasBorders: false,
                        lockMovementX: true,
                        lockMovementY: true,
                        globalCompositeOperation: 'destination-out'
                    });

                    hole.value = h;

                    const c = new fabric.Circle({
                        left: Math.floor(referenceToSave.value[0][0]),
                        top: Math.floor(referenceToSave.value[0][1]),
                        radius: 1,
                        fill: 'rgb(255, 0, 0)',
                        strokeWidth: 0,
                        hasControls: false,
                        selectable: false,
                        lockMovementX: true,
                        lockMovementY: true
                    });

                    circleRefPoint.value = c;

                    showSelectReferenceDialog.value = true;
                }
            }
        );

        function readImage(files) {
            let reader = new FileReader();
            reader.onloadend = function () {
                imageEncoding.value = reader.result;
            }
            reader.readAsDataURL(files[0]);
        }

        async function getImageSize(imageEncoding) {
            return new Promise(function(resolved, rejected) {
                let i = new Image();

                i.onload = function() {
                    resolved({width: i.width, height: i.height});
                };

                i.src = imageEncoding;
            });
        }

        watch(imageEncoding, (newValue) => {
            if (newValue !== '') {
                algorithmsStore.setStaticImage(newValue);
            }
            else {
                algorithmsStore.setStaticImage(null);
            }
        });

        function referenceChanged(value) {
            currentReferenceName.value = value;
        }

        watch(currentReferenceName, (newValue) => {
            if (newValue) {
                onReferenceAlgorithmChanged(newValue);
            }
            else {
                algorithmsStore.setCurrentReferenceAlgorithm(null);
                algorithmsStore.setCurrentReferenceAlgorithmAttributes([]);
                graphicsStore.resetReferenceGraphicItems();
                algorithmsStore.setAlgorithmResult(null);
                algorithmsStore.resetLiveAlgorithmReference();
            }
        });

        function algorithmChanged(value) {
            logger.debug('Algorithm selection changed', { newAlgorithm: value });
            currentAlgorithmName.value = value;
        }

        watch(currentAlgorithmName, (newValue) => {
            logger.debug('currentAlgorithmName watcher triggered', { newValue, oldValue: currentAlgorithmName.value });
            if (newValue) {
                logger.debug('Calling onAlgorithmChanged', { algorithm: newValue });
                onAlgorithmChanged(newValue);
            }
        });

        function importPathChanged(event) {
            importFilePath.value = event.target.files[0];
        }

        watch(importFilePath, (newValue) => {
            let fileread = new FileReader();
            fileread.onload = function (e) {
                let content = e.target.result;
                loadedAlgorithm.value = JSON.parse(content);

                let algorithm = null;

                if (selectedTabDebug.value === "References") {
                    algorithm = algorithmsStore.getReferenceAlgorithmByType(loadedAlgorithm.value.type);
                }
                else {
                    algorithm = algorithmsStore.getAlgorithmByType(loadedAlgorithm.value.type);
                }

                if (algorithm !== undefined) {
                    if (algorithm.type === currentAlgorithmName.value) {
                        if (selectedTabDebug.value === "References") {
                            algorithmsStore.loadCurrentReferenceAlgorithmFromObject(loadedAlgorithm.value.parameters);
                        }
                        else {
                            algorithmsStore.loadCurrentAlgorithmFromObject(loadedAlgorithm.value.parameters);
                        }

                        loadedAlgorithm.value = null;
                    }
                    else {
                        if (selectedTabDebug.value === "References") {
                            currentReferenceName.value = algorithm.type;
                        }
                        else {
                            currentAlgorithmName.value = algorithm.type;
                        }
                    }
                }
            };

            fileread.readAsText(newValue);
        });

        // Watch for FPS changes in the current image source to trigger WebSocket reconnection
        watch(() => {
            if (currentImageSourceId.value) {
                const imageSource = imageSourcesStore.getImageSourceById(currentImageSourceId.value);
                return imageSource?.fps;
            }
            return null;
        }, async (newFps, oldFps) => {
            if (newFps !== oldFps && newFps != null && currentImageSourceId.value) {
                logger.debug('Image source FPS changed, reconnecting WebSocket', { newFps, oldFps, imageSourceId: currentImageSourceId.value });
                await updateImageSource(currentImageSourceId.value);
            }
        });

        async function loadReferenceAlgorithmUI(type) {
            await algorithmsStore.loadReferenceAlgorithm({
                type: type
            });

            await algorithmsStore.setReferenceAlgorithm({
                type: type
            });

            algorithmsStore.loadCurrentReferenceAlgorithmFromParameters({
                attributes: referenceAlgorithmAttributes.value,
                type: type
            });
        }

        async function onAlgorithmChanged(type) {
            logger.debug('onAlgorithmChanged called', { type });
            
            // For the Detections tab, we need to check if we're selecting a generic algorithm
            // or re-selecting a configured algorithm
            const isConfigured = configuredAlgorithms.value.some(alg => alg.type === type);
            
            if (isConfigured) {
                // This is a configured algorithm with saved data
                const configuredAlg = configuredAlgorithms.value.find(alg => alg.type === type);
                logger.debug('Loading configured algorithm:', { configuredAlg, type });
                await loadUIandAlgorithm(type, configuredAlg.uid);
            } else {
                // This is a generic algorithm type - create new instance
                logger.debug('Loading generic algorithm type:', type);
                await loadUIandAlgorithm(type, null);
            }

            if (loadedAlgorithm.value) {
                algorithmsStore.loadCurrentAlgorithmFromObject(loadedAlgorithm.value.parameters);
                loadedAlgorithm.value = null;
            }
            
            // Debug the state after loading
            logger.debug('Algorithm state after loading:', {
                currentAlgorithm: algorithmsStore.currentAlgorithm,
                algorithmAttributes: algorithmAttributes.value,
                parameters: parameters.value
            });
        }

        async function onReferenceAlgorithmChanged(type) {
            await loadReferenceAlgorithmUI(type);

            if (loadedAlgorithm.value) {
                algorithmsStore.loadCurrentReferenceAlgorithmFromObject(loadedAlgorithm.value.parameters);
                loadedAlgorithm.value = null;
            }
        }

        async function updateImageSource(id) {
            try {
                currentImageSourceId.value = id;

                if (id) {
                    // CENTRALIZED URL CONSTRUCTION - Use centralized API for dynamic URL
                    const baseUrl = await api.getBaseUrl();
                    const wsBaseUrl = baseUrl.replace('http', 'ws');
                    
                    // Get image source data to include FPS parameter
                    const imageSource = imageSourcesStore.getImageSourceById(id);
                    
                    if (imageSource) {
                        // Include FPS parameter for proper frame rate control
                        const fps = imageSource.fps || 1; // Default to 1 FPS if not specified
                        let wsUrl;
                        
                        if (imageSource.image_source_type === "static") {
                            wsUrl = `${wsBaseUrl}/image_source/${id}/${imageSource.image_generator_uid}/${fps}/ws`;
                        } else if (imageSource.image_source_type === "dynamic") {
                            wsUrl = `${wsBaseUrl}/image_source/${id}/${imageSource.camera_uid}/${fps}/ws`;
                        } else {
                            // Fallback to old format if type is unknown
                            wsUrl = `${wsBaseUrl}/image_source/${id}/ws`;
                        }
                        
                        feedLocation.value = wsUrl;
                        logger.debug('Image source updated with FPS control', { id, fps, type: imageSource.image_source_type, feedLocation: feedLocation.value });
                    } else {
                        // Fallback if image source not found in store
                        feedLocation.value = `${wsBaseUrl}/image_source/${id}/ws`;
                        logger.warn('Image source not found in store, using fallback URL without FPS', { id });
                    }
                    
                    disableActions.value = false;
                }
                else {
                    disableActions.value = true;
                    feedLocation.value = '';
                    logger.debug('Image source cleared');
                }
            } catch (error) {
                logger.error('Failed to update image source', error);
                addErrorToStore(errorsStore, 'Image Source Error', error);
            }
        }

        function startCamera() {
            show.value = true;
        }

        function stopCamera() {
            show.value = false;
        }

        // CENTRALIZED ALGORITHM PROCESSING
        async function singleRunAlgorithm() {
            try {
                await withLoading(async () => {
                    logger.debug('Starting single algorithm run via centralized pattern');
                    
                    // Use centralized graphics processing
                    const graphicsData = {
                        items: graphicItems.value,
                        canvas: canvas.value
                    };

                    // CENTRALIZED API CALLS instead of direct store dispatch
                    await api.post('/algorithm/__API__/edit_live_algorithm', {
                        key: 'graphics',
                        value: graphicsData
                    });
                    
                    await algorithmsStore.setLiveAlgorithmReference();

                    if (currentReferenceAlgorithm.value) {
                        // Ensure we have a valid golden_position value
                        const goldenPositionValue = (referenceToSave.value && 
                                                   currentReferencePointIdx.value >= 0 && 
                                                   currentReferencePointIdx.value < referenceToSave.value.length) 
                                                   ? referenceToSave.value[currentReferencePointIdx.value] 
                                                   : [0, 0];
                        
                        await api.post('/algorithm/__API__/edit_reference_algorithm', {
                            key: 'golden_position',
                            value: goldenPositionValue
                        });
                    }

                    // CENTRALIZED API PROCESSING
                    let apiEndpoint;
                    let requestData;
                    
                    if (selectedTabSource.value === "Image Source") {
                        apiEndpoint = `/algorithm/__API__/single_process_algorithm_camera/${currentImageSourceId.value}/component`;
                        requestData = {};
                    } else {
                        apiEndpoint = '/algorithm/__API__/single_process_algorithm_static/component';
                        requestData = {};
                    }

                    const response = await api.post(apiEndpoint, requestData);
                    
                    if (response.ok) {
                        logger.info('Algorithm processed successfully via centralized API');
                        setNotification(2000, 'Algorithm processed successfully', 'bi-check-circle-fill');
                    } else {
                        throw new Error(`Algorithm processing failed: ${response.statusText}`);
                    }
                });
            } catch (error) {
                logger.error('Failed to process algorithm', error);
                addErrorToStore(errorsStore, 'Algorithm Processing Error', error);
                setNotification(5000, `Algorithm processing failed: ${error.message}`, 'bi-exclamation-circle-fill');
            }
        }

        async function liveProcessAlgorithm(state) {
            if (state) {
                    if (!canvas.value) {
                    logger.warn('Canvas not available for graphics processing');
                    return;
                }
            const data = graphic.getGraphicsProps(graphicItems.value, canvas.value);

                await algorithmsStore.updateCurrentAlgorithmProperty({
                    name: 'graphics',
                    value: data
                });
                await algorithmsStore.setLiveAlgorithmReference();

                if (currentReferenceAlgorithm.value) {
                    // Ensure we have a valid golden_position value
                    const goldenPositionValue = (referenceToSave.value && 
                                               currentReferencePointIdx.value >= 0 && 
                                               currentReferencePointIdx.value < referenceToSave.value.length) 
                                               ? referenceToSave.value[currentReferencePointIdx.value] 
                                               : [0, 0];
                    
                    await algorithmsStore.updateCurrentReferenceAlgorithmProperty({
                    name: 'golden_position',
                    value: goldenPositionValue
                });
                }

                let url = null;
                let id = uuid.v4();

                const baseUrl = await api.getBaseUrl();
                const wsBaseUrl = baseUrl.replace('http', 'ws');
                
                if (selectedTabSource.value === "Image Source") {
                    url = `${wsBaseUrl}/algorithm/live_algorithm_result/${currentImageSourceId.value}/${id}/ws`;
                }
                else {
                    url = `${wsBaseUrl}/algorithm/live_algorithm_result/${id}/ws`;
                }

                // Use centralized WebSocket composable
                liveProcessSocket = useWebSocket(url, {
                    autoConnect: true,
                    reconnectAttempts: 3,
                    reconnectInterval: 2000,
                    onOpen: onSocketOpen,
                    onMessage: liveResultMsgRecv
                });

                setLiveAlgorithmSocket(liveProcessSocket.socket.value);
            }
            else {
                if (liveProcessSocket) {
                    liveProcessSocket.send(JSON.stringify({ command: "disconnect" }));
                    liveProcessSocket.disconnect();
                    liveProcessSocket = null;
                    setLiveAlgorithmSocket(null);
                }
            }
        }

        async function singleRunReference() {
            const graphicItems = graphicsStore.currentReferenceGraphics;
            
            if (!canvas.value) {
                logger.warn('Canvas not available for reference graphics processing');
                return;
            }

            const data = graphic.getGraphicsProps(graphicItems, canvas.value);

            await algorithmsStore.updateCurrentReferenceAlgorithmProperty({
                name: 'graphics',
                value: data
            });

            currentReferencePointIdx.value = 0;

            await algorithmsStore.updateCurrentReferenceAlgorithmProperty({
                name: 'reference_point_idx',
                value: currentReferencePointIdx.value
            });

            if (selectedTabSource.value === "Image Source") {
                await algorithmsStore.singleProcessReferenceCamera({
                    uid: currentImageSourceId.value,
                    type: "component"
                }).catch((err) => {
                    logger.error('Failed to process reference algorithm with camera', err);
                    errorsStore.addError({
                        id: uuid.v4(),
                        title: 'Reference Algorithm Debug Error',
                        description: err
                    });
                    setNotification(3000, err, 'bi-exclamation-circle-fill');
                });
            }
            else {
                await algorithmsStore.singleProcessReferenceStatic({
                    type: "component"
                }).catch((err) => {
                    logger.error('Failed to process reference algorithm with static image', err);
                    errorsStore.addError({
                        id: uuid.v4(),
                        title: 'Reference Algorithm Debug Error',
                        description: err
                    });
                    setNotification(3000, err, 'bi-exclamation-circle-fill');
                });
            }
        }

        async function liveProcessReference(state) {
            if (state) {
                const graphicItems = graphicsStore.currentReferenceGraphics;
                
                if (!canvas.value) {
                    logger.warn('Canvas not available for live reference processing');
                    return;
                }

                const data = graphic.getGraphicsProps(graphicItems, canvas.value);

                await algorithmsStore.updateCurrentReferenceAlgorithmProperty({
                name: 'graphics',
                value: data
            });

                currentReferencePointIdx.value = 0;

                await algorithmsStore.updateCurrentReferenceAlgorithmProperty({
                name: 'reference_point_idx',
                value: currentReferencePointIdx.value
            });

                let url = null;
                let id = uuid.v4();

                const baseUrl = await api.getBaseUrl();
                const wsBaseUrl = baseUrl.replace('http', 'ws');
                
                if (selectedTabSource.value === "Image Source") {
                    url = `${wsBaseUrl}/algorithm/live_reference/${currentImageSourceId.value}/${id}/ws`;
                }
                else {
                    url = `${wsBaseUrl}/algorithm/live_reference/${id}/ws`;
                }

                // Use centralized WebSocket composable
                liveProcessSocket = useWebSocket(url, {
                    autoConnect: true,
                    reconnectAttempts: 3,
                    reconnectInterval: 2000,
                    onOpen: onSocketOpen,
                    onMessage: liveResultMsgRecv
                });

                setLiveAlgorithmSocket(liveProcessSocket.socket.value);
            }
            else {
                if (liveProcessSocket) {
                    liveProcessSocket.send(JSON.stringify({ command: "disconnect" }));
                    liveProcessSocket.disconnect();
                    liveProcessSocket = null;
                    setLiveAlgorithmSocket(null);
                }
            }
        }

        function closeSelectReferenceDialog() {
            showSelectReferenceDialog.value = false;

            algorithmsStore.updateCurrentReferenceAlgorithmProperty({
                name: 'reference_point_idx',
                value: currentReferencePointIdx.value
            });
        }

        function onSocketOpen() {
            if (liveProcessSocket) {
                liveProcessSocket.send(JSON.stringify({
                    command: ''
                }));
            }
        }

        function resetCameraScene(currentTab) {
            selectedTabSource.value = currentTab;
            if (currentTab === "Image Source") {
                imageEncoding.value = '';
            }
            else {
                show.value = false;
            }
        }

        function tabChangedDebug(value) {
            selectedTabDebug.value = value;
        }

        function downloadAlgorithm() {
            let algorithm = null;

            if (selectedTabDebug.value === "References") {
                algorithm = currentReferenceAlgorithm.value;
            }
            else {
                algorithm = currentAlgorithm.value;
            }

            download(algorithm);
        }

        function changeReferencePoint(idx) {
            currentReferencePointIdx.value = idx;

            const h = new fabric.Rect({
                left: Math.floor(referenceToSave.value[idx][0]) - 25,
                top: Math.floor(referenceToSave.value[idx][1]) - 25,
                fill: '#451245',
                width: 50,
                height: 50,
                objectCaching: true,
                selectable: false,
                hasControls: false,
                hasBorders: false,
                lockMovementX: true,
                lockMovementY: true,
                globalCompositeOperation: 'destination-out'
            });

            hole.value = h;

            const c = new fabric.Circle({
                left: Math.floor(referenceToSave.value[idx][0]),
                top: Math.floor(referenceToSave.value[idx][1]),
                radius: 1,
                fill: 'rgb(255, 0, 0)',
                strokeWidth: 0,
                hasControls: false,
                selectable: false,
                lockMovementX: true,
                lockMovementY: true
            });

            circleRefPoint.value = c;
        }

        // COMPREHENSIVE ALGORITHM DEBUG FUNCTION
        async function debugAlgorithms() {
            try {
                logger.debug('=== COMPREHENSIVE ALGORITHM DEBUG ===');
                logger.debug('Debugging all algorithm types...');
                
                // Debug generic algorithms (from /algorithm/types)
                const genericAlgorithms = algorithmsStore.algorithms.value;
                logger.debug('=== GENERIC ALGORITHMS (/algorithm/types) ===');
                logger.debug('Generic algorithms count:', Array.isArray(genericAlgorithms) ? genericAlgorithms.length : 'not an array');
                logger.debug('Generic algorithms actual values:', Array.isArray(genericAlgorithms) ? genericAlgorithms : 'undefined or not array');
                if (Array.isArray(genericAlgorithms) && genericAlgorithms.length > 0) {
                    logger.debug('First generic algorithm:', {
                        algorithm: genericAlgorithms[0],
                        keys: Object.keys(genericAlgorithms[0]),
                        type: genericAlgorithms[0].type,
                        uid: genericAlgorithms[0].uid
                    });
                }
                
                // Debug configured algorithms (from /algorithm)
                const configuredAlgorithms = algorithmsStore.configuredAlgorithms.value;
                logger.debug('=== CONFIGURED ALGORITHMS (/algorithm) ===');
                logger.debug('Configured algorithms count:', Array.isArray(configuredAlgorithms) ? configuredAlgorithms.length : 'not an array');
                logger.debug('Configured algorithms actual values:', Array.isArray(configuredAlgorithms) ? configuredAlgorithms : 'undefined or not array');
                if (configuredAlgorithms.length > 0) {
                    logger.debug('First configured algorithm DETAILED:', {
                        algorithm: configuredAlgorithms[0],
                        keys: Object.keys(configuredAlgorithms[0]),
                        uid: configuredAlgorithms[0].uid,
                        type: configuredAlgorithms[0].type,
                        name: configuredAlgorithms[0].name,
                        parameters: configuredAlgorithms[0].parameters,
                        stringified: JSON.stringify(configuredAlgorithms[0])
                    });
                    
                    // Check all configured algorithms
                    configuredAlgorithms.forEach((alg, index) => {
                        logger.debug(`Configured algorithm ${index}:`, {
                            uid: alg.uid,
                            type: alg.type,
                            name: alg.name,
                            hasParameters: !!alg.parameters,
                            parametersKeys: alg.parameters ? Object.keys(alg.parameters) : 'none'
                        });
                    });
                }
                
                // Debug reference algorithms
                const referenceAlgorithms = algorithmsStore.referenceAlgorithms.value;
                logger.debug('=== REFERENCE ALGORITHMS (/algorithm/reference/types) ===');
                logger.debug('Reference algorithms count:', Array.isArray(referenceAlgorithms) ? referenceAlgorithms.length : 'not an array');
                logger.debug('Reference algorithms structure:', referenceAlgorithms);
                
                // Compare what we're using in the UI
                logger.debug('=== UI DATA SOURCES ===');
                logger.debug('Using for dropdown:', algorithmsStore.configuredAlgorithms.value);
                logger.debug('Current selected algorithm name:', currentAlgorithmName.value);
                logger.debug('Current algorithm attributes:', algorithmsStore.algorithmAttributes.value);
                logger.debug('Current algorithm parameters:', parameters.value);
                
                // Debug the current configuration
                const currentConfig = configurationsStore.currentConfiguration.value;
                logger.debug('=== CONFIGURATION DEBUG ===');
                logger.debug('Current configuration:', currentConfig);
                
                logger.debug('=== END COMPREHENSIVE DEBUG ===');
                
            } catch (error) {
                logger.error('Failed to load algorithms:', error);
            }
        }

        onMounted(async () => {
            logger.lifecycle('mounted', 'AlgorithmDebug component mounted');
            
            // Check if algorithms are already loaded, if not load them
            try {
                // First check if algorithms are already available
                const currentAlgorithms = algorithmsStore.algorithms.value;
                const currentConfiguredAlgorithms = algorithmsStore.configuredAlgorithms.value;
                const currentReferenceAlgorithms = algorithmsStore.referenceAlgorithms.value;
                
                logger.debug('Checking existing algorithm data:', {
                    algorithms: Array.isArray(currentAlgorithms) ? currentAlgorithms.length : 'not loaded',
                    configuredAlgorithms: Array.isArray(currentConfiguredAlgorithms) ? currentConfiguredAlgorithms.length : 'not loaded',
                    referenceAlgorithms: Array.isArray(currentReferenceAlgorithms) ? currentReferenceAlgorithms.length : 'not loaded'
                });
                
                // Only load if not already available
                const loadPromises = [];
                
                if (!Array.isArray(currentAlgorithms) || currentAlgorithms.length === 0) {
                    logger.debug('Loading generic algorithms');
                    loadPromises.push(algorithmsStore.loadAlgorithms());
                }
                
                if (!Array.isArray(currentReferenceAlgorithms) || currentReferenceAlgorithms.length === 0) {
                    logger.debug('Loading reference algorithms');
                    loadPromises.push(algorithmsStore.loadReferenceAlgorithms());
                }
                
                if (!Array.isArray(currentConfiguredAlgorithms) || currentConfiguredAlgorithms.length === 0) {
                    logger.debug('Loading configured algorithms');
                    loadPromises.push(algorithmsStore.loadConfiguredAlgorithms());
                }
                
                // Always ensure image sources are loaded
                loadPromises.push(imageSourcesStore.loadImageSources());
                
                if (loadPromises.length > 0) {
                    await Promise.all(loadPromises);
                    logger.debug('Missing algorithms and image sources loaded in AlgorithmDebug');
                    
                    // Check what we actually got after loading
                    const afterLoadAlgorithms = algorithmsStore.algorithms.value;
                    const afterLoadConfiguredAlgorithms = algorithmsStore.configuredAlgorithms.value;
                    const afterLoadReferenceAlgorithms = algorithmsStore.referenceAlgorithms.value;
                    
                    logger.debug('After loading - checking algorithm data:', {
                        algorithms: Array.isArray(afterLoadAlgorithms) ? afterLoadAlgorithms.length : 'still not loaded',
                        configuredAlgorithms: Array.isArray(afterLoadConfiguredAlgorithms) ? afterLoadConfiguredAlgorithms.length : 'still not loaded',
                        referenceAlgorithms: Array.isArray(afterLoadReferenceAlgorithms) ? afterLoadReferenceAlgorithms.length : 'still not loaded'
                    });
                } else {
                    logger.debug('All algorithms already available, skipping load');
                }
                
                // Wait a bit for reactive updates to propagate
                await new Promise(resolve => setTimeout(resolve, 200));
                
                // Run comprehensive algorithm debugging
                await debugAlgorithms();
                
            } catch (error) {
                logger.error('Failed to load algorithms in AlgorithmDebug', error);
            }
            
            // Auto-load configuration if none are loaded
            const currentConfig = configurationsStore.currentConfiguration;
            if (!currentConfig) {
                try {
                    logger.debug('Loading configuration and algorithms');
                    
                    // Load configurations list first
                    await configurationsStore.loadConfigurations();
                    
                    // Get the first available configuration
                    const configurations = configurationsStore.configurations;
                    if (configurations.length > 0) {
                        const defaultConfig = configurations[0];
                        
                        // Load the configuration
                        await configurationsStore.loadConfiguration(defaultConfig);
                        
                        logger.info('Configuration and algorithms loaded successfully');
                    }
                } catch (error) {
                    logger.error('Failed to auto-load configuration', error);
                    errorsStore.addError({
                        id: uuid.v4(),
                        title: 'Configuration Load Error',
                        description: error
                    });
                }
            } else {
                // Configuration already loaded, ensure image sources are loaded
                try {
                    await imageSourcesStore.loadImageSources();
                    logger.debug('Image sources loaded');
                } catch (error) {
                    logger.error('Failed to load image sources', error);
                    errorsStore.addError({
                        id: uuid.v4(),
                        title: 'Image Sources Load Error',
                        description: error
                    });
                }
            }
        });

        onBeforeUnmount(() => {
            logger.lifecycle('beforeUnmount', 'AlgorithmDebug component before unmount');
            
            // Clean up WebSocket if it exists
            if (liveProcessSocket) {
                logger.webSocket('disconnecting');
                liveProcessSocket.disconnect();
                liveProcessSocket = null;
            }
            
            resultsWatch();
            algorithmsStore.setCurrentAlgorithm(null);
            algorithmsStore.setCurrentAlgorithmAttributes([]);
            algorithmsStore.setCurrentReferenceAlgorithm(null);
            algorithmsStore.setCurrentReferenceAlgorithmAttributes([]);
            graphicsStore.resetReferenceGraphicItems();
            graphicsStore.resetGraphicsItems();
            algorithmsStore.setAlgorithmResult(null);
            algorithmsStore.resetLiveAlgorithmReference();
            
            logger.lifecycle('cleanup', 'AlgorithmDebug cleanup completed');
        });

        return {
            algorithms,
            configuredAlgorithms,
            referenceAlgorithms,
            currentImageSourceId,
            currentAlgorithm,
            currentReferenceAlgorithm,
            type: computed(() => currentAlgorithm?.value?.type || ''),
            algorithmAttributes,
            referenceAlgorithmAttributes,
            parameters,
            referenceParameters,
            imageEncoding,
            show,
            feedLocation,
            resultImage,
            outputImages,
            currentGraphics,
            isLoading,
            disableActions,
            disableProcessButton,
            selectedGraphic,
            showMasks,
            disableRoiMasks,
            showNotification,
            notificationMessage,
            notificationIcon,
            notificationTimeout,
            showSelectReferenceDialog,
            referenceToSave,
            currentReferencePointIdx,
            referenceOverlay,
            hole,
            circleRefPoint,
            closeSelectReferenceDialog,
            setNotification,
            clearNotification,
            referenceChanged,
            algorithmChanged,
            readImage,
            updateImageSource,
            startCamera,
            stopCamera,
            singleRunAlgorithm,
            resetCameraScene,
            liveProcessAlgorithm,
            singleRunReference,
            liveProcessReference,
            updateGraphics,
            tabChangedDebug,
            importPathChanged,
            downloadAlgorithm,
            selectionChanged,
            selectionCleared,
            selectionModified,
            saveMasks,
            changeReferencePoint
        }
    }
}
</script>

<style scoped>
.flex-container {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    color: white;
    margin: auto;
    flex-direction: column;
}

.camera-wrapper {
    display: flex;
}

.actions-wrapper {
    display: flex;
}

.camera-scene-item {
    margin: 5px;
}

.file-selector {
    margin: 5px;
}

.algorithm-control {
    margin: 5px;
}

.rounded-button {
    border-radius: 0 10px 10px 0;
    background-color: #000000;
    border: none;
    color: rgb(204, 161, 82);
    padding: 10px 20px;
    position: absolute;
    width: 5vw;
    top: 55%;
    left: -2%;
}

button:disabled,
button[disabled] {
    border: 1px solid #999999;
    background-color: #cccccc;
    color: #666666;
    cursor: not-allowed;
}

.roi-masks {
    position: absolute;
    top: 55%;
    left: 0;
    width: 30vw;
    height: 35%;
    z-index: 20;
    background-color: rgb(0, 0, 0);
}

.choices {
    padding: 1% 0%;
    display: flex;
    justify-content: flex-start;
    height: 6.5vh;
    overflow-x: scroll;
}

.reference-choice {
    background-color: #000000;
    border: 1px solid gray;
    color: white;
}

.reference-choice:hover {
    background-color: #2c2c2c;
}

.selected-reference {
    background-color: green;
}

.selected-reference:hover {
    background-color: rgb(22, 155, 22);
}

button {
    width: 5vw;
    margin: 0% 2%;
}

.action-control {
    margin: 0;
    width: 100%;
    display: flex;
    justify-content: flex-end;
    height: 5.5vh;
}

.message-wrapper {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.icon-wrapper {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 3%;
}

.text-wrapper {
    font-size: 100%;
    width: 95%;
    text-align: center;
}

.choices::-webkit-scrollbar {
    width: 10px;
    height: 5px;
}

.choices::-webkit-scrollbar-track {
    background: #888; 
}

.choices::-webkit-scrollbar-thumb {
    background: rgb(204, 161, 82); 
}

.choices::-webkit-scrollbar-thumb:hover {
    background: rgb(234, 189, 105); 
}
</style>
