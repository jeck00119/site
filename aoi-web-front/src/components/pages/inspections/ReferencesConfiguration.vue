<template>
    <div class="flex-container">
        <div class="list-wrapper">
            <components-list
                width="100%"
                height="100%"
                :components="components"
                :retrieving="componentsRetrieving"
                :disable="!currentConfiguration"
                @load-component="loadComponent"
                @remove-component="removeComponent"
                @save-component="addComponent"
            ></components-list>
        </div>
        <div class="control-camera-container">
            <div class="results-vis">
                <div class="camera-wrapper">
                    <div class="camera-scene-item">
                        <camera-scene
                            width="100%"
                            height="100%"
                            :show="showCamera"
                            :camera-feed="true"
                            :feed-location="feedLocation"
                            :static-images="[]"
                            :id="1"
                            canvas-id="camera-scene-canvas"
                            :graphics="currentGraphics"
                            @graphics-changed="updateGraphics"
                            @graphic-selected="selectionChanged"
                            @graphic-cleared="selectionCleared"
                            @graphic-modified="selectionModified"
                        ></camera-scene>
                    </div>
                    <div class="camera-scene-item">
                        <camera-scene
                            width="100%"
                            height="100%"
                            :camera-feed="false"
                            :static-images="outputImages"
                            :id="2" canvas-id="result-canvas"
                            :graphics="[]"
                        ></camera-scene>
                    </div>
                </div>
            </div>
            <div class="control">
                <component-control
                    :type="moduleName"
                    :current-component="currentComponent"
                    :algorithm-attributes="algorithmAttributes"
                    :algorithm-parameters="parameters"
                    :availableAlgorithms="algorithms"
                    :algorithm-id="algorithmId"
                    :component-loading="componentLoading"
                    @show-camera="changeCameraStatus"
                    @single-run="singleRunComponent"
                    @live-process="liveProcessAlgorithm"
                    @update-image-source="updateImageSource"
                    @algorithm-changed="onAlgorithmChanged"
                    @import-path-changed="onImportPathChanged"
                    @save-component="saveComponent"
                    @download-algorithm="downloadAlgorithm"
                    @save-ref-changed="saveRefChanged"
                ></component-control>
            </div>
        </div>
        <button
            class="rounded-button"
            @click="showMasks = true"
            v-if="!showMasks"
            :disabled="!currentComponent"
        >ROI</button>
        <div class="roi-masks" v-else>
            <mask-scene
                :graphics="selectedGraphic"
                :image-source-id="currentImageSourceId"
                canvas-id="mask-scene"
                width="100%"
                height="100%"
                @closed="showMasks = false"
                @save="saveMasks"
            ></mask-scene>
        </div>
        <div class="results-btn-container" v-if="!showResults">
            <button class="action-button" @click="showResults = true" :disabled="!data">
                <div class="button-container">
                    <div class="button-icon">
                        <v-icon name="vi-file-type-light-json" scale="1"/>
                    </div>
                </div>
            </button>
        </div>
        <div class="results-container" v-else>
            <json-data-container width="auto" height="29vh" :data="data" @closed="showResults = false"></json-data-container>
        </div>
        <base-notification :show="showNotification" :timeout="5000" height="15vh">
            <div class="message-wrapper">
                <div class="icon-wrapper">
                    <v-icon :name="notificationIcon" scale="2.5" animation="float" />
                </div>
                <div class="text-wrapper">
                    {{ notificationMessage }}
                </div>
            </div>
        </base-notification>
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
    </div>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { useStore } from 'vuex';
// // import { useAlgorithmsStore } from '../../../hooks/algorithms.js';
// // import { useComponentsStore } from '../../../hooks/components.js';
// // import { useGraphicsStore } from '../../../hooks/graphics.js';
import { useConfigurationsStore, useAlgorithmsStore, useComponentsStore, useGraphicsStore, useAuthStore, useLogStore } from '@/composables/useStore';
// // import { useAuthStore } from '../../../hooks/auth.js';
// // import { useLogStore } from '../../../hooks/log.js';
import { uuid } from "vue3-uuid";
import { createLogger } from '@/utils/logger';

import graphic from '../../../utils/graphics.js';

import ComponentsList from '../../layout/ComponentsList.vue';
import ComponentControl from '../../layout/ComponentControl.vue';
import CameraScene from '../../camera/CameraScene.vue';
import AlgorithmResultTable from '../../layout/AlgorithmResultTable.vue';
import MaskScene from '../../layout/MaskScene.vue';
import JsonDataContainer from '../../layout/JsonDataRenderer.vue';
import { ipAddress, port } from '../../../url';
import useNotification from '../../../hooks/notifications.ts';
import { useWebSocket } from '@/composables/useStore';
import { DEFAULT_IMAGE_DATA_URI_PREFIX, ImageDataUtils } from '../../../utils/imageConstants';

export default{
    components: {
        ComponentsList,
        ComponentControl,
        CameraScene,
        AlgorithmResultTable,
        MaskScene,
        JsonDataContainer
    },

    setup() {
        const logger = createLogger('ReferencesConfiguration');
        const moduleName = 'reference';

        const showMasks = ref(false);
        const showResults = ref(false);

        const currentComponent = ref(null);

        const showCamera = ref(false);

        const feedLocation = ref('');
        const currentImageSourceId = ref('');

        const componentLoading = ref(false);
        const componentsRetrieving = ref(false);

        const loadedAlgorithm = ref(null);
        const algorithmId = ref('');
        const algIsConfigured = ref(false);

        const referenceToSave = ref([]);
        const currentReferencePointIdx = ref(-1);
        const showSelectReferenceDialog = ref(false);

        const referenceOverlay = ref(null);
        const hole = ref(null);
        const circleRefPoint = ref(null);

        const saveRef = ref(false);

        const error = ref('');

        let graphicsObject = null;
        const selectedGraphic = ref(null);
        const selectedRect = ref(null);

        // WebSocket state
        let liveProcessSocketInstance = null;

        const {showNotification, notificationMessage, notificationIcon, notificationTimeout, 
            setNotification, clearNotification} = useNotification();

        const store = useStore();
        const algorithmsStore = useAlgorithmsStore();
        const componentsStore = useComponentsStore();
        const graphicsStore = useGraphicsStore();
        const configurationsStore = useConfigurationsStore();
        const authStore = useAuthStore();
        const logStore = useLogStore();

        // These are already computed refs from the composables


        const currentConfiguration = configurationsStore.currentConfiguration;

        const currentUser = authStore.currentUser;

        const algorithms = algorithmsStore.referenceAlgorithms;

        const components = computed(function() {
            const c = componentsStore.references;
            componentsRetrieving.value = false;
            return Array.isArray(c) ? c : [];
        });

        const resultImage = computed(function() {
            const result = store.getters["algorithms/getAlgorithmResult"];
            if(result && result.frame)
            {
                if(Array.isArray(result.frame) && result.frame.length === 0)
                {
                    return '';
                }
                else if(Array.isArray(result.frame))
                {
                    return result.frame[0];
                }
                else
                {
                    // Handle single frame case
                    return result.frame;
                }
            }
            return '';
        });

        const outputImages = computed(function() {
            const result = algorithmsStore.algorithmResult;
            let outputImages = [];
            if(result && result.frame)
            {
                outputImages = Array.isArray(result.frame) ? result.frame : [result.frame];
            }
            return outputImages;
        });

        const data = computed(function() {
            const result = algorithmsStore.algorithmResult;
            return result ? result.data : null;
        });

        const resultsWatch = store.watch(
            (_, getters) => getters["algorithms/getAlgorithmResult"],
            async (newValue) => {
                if(newValue && newValue.reference)
                {
                    if(saveRef.value)
                    {
                        referenceToSave.value = [];
                        for(let reference of newValue.reference)
                        {
                            referenceToSave.value.push([reference.x, reference.y]);
                        }
                        currentReferencePointIdx.value = 0;
                    }
                }
                else
                {
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

        async function getImageSize(imageEncoding) {
            return new Promise(function(resolved, rejected) {
                let i = new Image();

                i.onload = function() {
                    resolved({width: i.width, height: i.height});
                };

                i.src = imageEncoding;
            });
        }

        const currentAlgorithm = computed(function() {
            return store.getters["algorithms/getCurrentReferenceAlgorithm"];
        });

        const algorithmAttributes = computed(function() {
            return store.getters["algorithms/getCurrentReferenceAlgorithmAttributes"];
        });

        const parameters = computed(function() {
            if(currentAlgorithm.value)
                return currentAlgorithm.value.parameters;
            else
                return [];
        });

        const currentGraphics = computed(function() {
            return store.getters["graphics/getCurrentReferenceGraphics"];
        });

        async function loadComponent(id) {
            componentLoading.value = true;
            try{
                logger.debug('Loading reference component', { id });
                if(id)
                {
                    await store.dispatch("components/loadComponent", {
                        uid: id,
                        type: moduleName
                    });

                    const current = store.getters["components/getCurrentComponent"];

                    currentComponent.value = current;
                    componentLoading.value = false;

                    if(currentComponent.value.algorithmUid)
                    {
                        algIsConfigured.value = true;
                    }

                    const algorithm = store.getters["algorithms/getReferenceAlgorithmByType"](current.algorithmType);

                    if(algorithm)
                    {
                        if(algorithmId.value === algorithm.uid)
                        {
                            loadUIandAlgorithm(algorithm.type, currentComponent.value.algorithmUid);
                        }
                        else
                        {
                            algorithmId.value = algorithm.uid;
                        }
                    }
                    else
                    {
                        algorithmId.value = '';
                    }
                    
                    logger.info('Reference component loaded successfully', { id, algorithmType: current.algorithmType });
                }
                else
                {
                    logger.debug('Resetting reference component state');
                    store.dispatch("algorithms/setCurrentReferenceAlgorithm", null);
                    store.dispatch("algorithms/setAlgorithmResult", null);
                    store.dispatch("components/setCurrentComponent", null);
                    store.dispatch("graphics/resetReferenceGraphicItems");

                    showCamera.value = false;
                }
            }
            catch(err) {
                logger.error('Failed to load reference component', err);
                setNotification(3000, "Error while trying to load component.", 'bi-exclamation-circle-fill');
            }
        };

        function removeComponent(id) {
            try {
                store.dispatch("components/removeComponent", {
                    uid: id,
                    type: moduleName
                });
                currentComponent.value = null;
            }catch(err) {
                setNotification(3000, "Error while trying to remove component.", 'bi-exclamation-circle-fill');
            }
        }

        async function updateComponent(component) {
            await store.dispatch("components/updateComponent", {
                type: moduleName,
                data: component
            });
        }

        function addComponent(name) {
            try {
                store.dispatch("components/addReference", {
                    name: name,
                    type: moduleName
                });

                store.dispatch("log/addEvent", {
                    type: moduleName.toUpperCase(),
                    user: currentUser.value ? currentUser.value.username : 'Unknown',
                    title: moduleName.toUpperCase() + ' Added',
                    description: `New ` + moduleName +  ` added: ${name}`
                });
            }catch(err) {
                setNotification(3000, "Error while trying to add component.", 'bi-exclamation-circle-fill');
            }
        }

        function changeCameraStatus(value) {
            showCamera.value = value;
        }

        async function singleRunComponent(imageSourceUid) {
            const graphicItems = store.getters["graphics/getCurrentReferenceGraphics"];
            const canvas = store.getters["graphics/getCanvas"];

            const data = graphic.getGraphicsProps(graphicItems, canvas);

            await store.dispatch("algorithms/updateCurrentReferenceAlgorithmProperty", {
                name: 'graphics',
                value: data
            });

            currentReferencePointIdx.value = 0;

            await store.dispatch("algorithms/updateCurrentReferenceAlgorithmProperty", {
                name: 'reference_point_idx',
                value: currentReferencePointIdx.value
            });

            try {
                await store.dispatch("algorithms/singleProcessReferenceCamera", {
                    uid: imageSourceUid,
                    type: moduleName
                });
            }catch(err) {
                setNotification(3000, err, 'bi-exclamation-circle-fill');
            }
        }

        async function liveProcessAlgorithm(state) {
            if(state)
            {
                const graphicItems = store.getters["graphics/getCurrentReferenceGraphics"];
                const canvas = store.getters["graphics/getCanvas"];

                const data = graphic.getGraphicsProps(graphicItems, canvas);

                await store.dispatch("algorithms/updateCurrentReferenceAlgorithmProperty", {
                    name: 'graphics',
                    value: data
                });

                currentReferencePointIdx.value = 0;

                await store.dispatch("algorithms/updateCurrentReferenceAlgorithmProperty", {
                    name: 'reference_point_idx',
                    value: currentReferencePointIdx.value
                });

                let id = uuid.v4();
                let url = `ws://${ipAddress}:${port}/algorithm/live_reference/${currentImageSourceId.value}/${id}/ws`;

                liveProcessSocketInstance = useWebSocket(url, {
                    autoConnect: true,
                    onOpen: onSocketOpen,
                    onMessage: liveResultMsgRecv
                });
            }
            else
            {
                if(liveProcessSocketInstance)
                {
                    liveProcessSocketInstance.send(JSON.stringify({command: "disconnect"}));
                    liveProcessSocketInstance.disconnect();
                    liveProcessSocketInstance = null;
                }
            }
        }

        function closeSelectReferenceDialog() {
            showSelectReferenceDialog.value = false;

            store.dispatch("algorithms/updateCurrentReferenceAlgorithmProperty", {
                name: 'reference_point_idx',
                value: currentReferencePointIdx.value
            });
        }

        function onSocketOpen() {
            if(liveProcessSocketInstance)
            {
                liveProcessSocketInstance.send(JSON.stringify({
                    command: ''
                }));
            }
        }

        function liveResultMsgRecv(event) {
            let recvData = JSON.parse(event.data);

            let outputImages = [];
            if (recvData.frame && Array.isArray(recvData.frame)) {
                for(const frame of recvData.frame)
                {
                    outputImages.push(ImageDataUtils.createJpegDataURI(frame));
                }
                recvData.frame = outputImages;
            } else {
                // Handle single frame or undefined case
                recvData.frame = recvData.frame ? [ImageDataUtils.createJpegDataURI(recvData.frame)] : [];
            }

            store.dispatch("algorithms/setAlgorithmResult", recvData);

            if(graphicsObject)
            {
                liveProcessSocketInstance.send(JSON.stringify({
                    command: 'set',
                    key: 'graphics',
                    value: graphicsObject
                }));
                graphicsObject = null;
            }
            else
            {
                liveProcessSocketInstance.send(JSON.stringify({command: ''}));
            }
        }

        function updateGraphics() {
            const graphicItems = store.getters["graphics/getCurrentReferenceGraphics"];
            const canvas = store.getters["graphics/getCanvas"];

            graphicsObject = graphic.getGraphicsProps(graphicItems, canvas);
        }

        function selectionChanged(rect) {
            const canvas = store.getters["graphics/getCanvas"];
            let data = graphic.getRectProps(rect, canvas);

            selectedRect.value = rect;
            selectedGraphic.value = data;
        }

        function selectionCleared() {
            selectedRect.value = null;
            selectedGraphic.value = null;
        }

        function selectionModified(obj) {
            if(obj === selectedRect.value)
            {
                const canvas = store.getters["graphics/getCanvas"];
                let data = graphic.getRectProps(obj, canvas);

                selectedGraphic.value = data;
            }
        }

        function updateImageSource(imageSourceId) {
            currentImageSourceId.value = imageSourceId;
            feedLocation.value = `ws://${ipAddress}:${port}/image_source/${imageSourceId}/ws`;
        }

        async function loadUIandAlgorithm(type, uid)
        {
            await store.dispatch("algorithms/loadReferenceAlgorithm", {
                type: type
            });

            await store.dispatch("algorithms/setReferenceAlgorithm", {
                type: type
            });

            if(algIsConfigured.value)
            {
                store.dispatch("algorithms/loadCurrentReferenceAlgorithm", {
                    uid: uid
                });
                algIsConfigured.value = false;
            }
            else
            {
                store.dispatch("algorithms/loadCurrentReferenceAlgorithmFromParameters", {
                    attributes: algorithmAttributes.value,
                    type: type
                });
            }
        }

        function onAlgorithmChanged(id){
            algorithmId.value = id;

            const algorithm = store.getters["algorithms/getReferenceAlgorithmById"](id);

            if(algorithm)
            {
                loadUIandAlgorithm(algorithm.type, currentComponent.value.algorithmUid);

                if(loadedAlgorithm.value)
                {
                    store.dispatch("algorithms/loadCurrentReferenceAlgorithmFromObject", loadedAlgorithm.value.parameters);
                    loadedAlgorithm.value = null;
                }
            }
            else
            {
                store.dispatch("algorithms/setCurrentReferenceAlgorithm", null);
                store.dispatch("algorithms/setCurrentReferenceAlgorithmAttributes", []);
                store.dispatch("graphics/resetReferenceGraphicItems");
                store.dispatch("algorithms/setAlgorithmResult", null);
            }
        }

        function onImportPathChanged(path){
            let fileread = new FileReader();
            fileread.onload = function(e) {
                let content = e.target.result;
                loadedAlgorithm.value = JSON.parse(content);

                const algorithm = store.getters["algorithms/getReferenceAlgorithmByType"](loadedAlgorithm.value.type);

                if(algorithm !== undefined)
                {
                    if(algorithm.uid === algorithmId.value)
                    {
                        store.dispatch("algorithms/loadCurrentReferenceAlgorithmFromObject", loadedAlgorithm.value.parameters);
                        loadedAlgorithm.value = null;
                    }
                    else
                    {
                        algorithmId.value = algorithm.uid;
                    }
                }
            };

            fileread.readAsText(path);
        }

        async function saveComponent(payload){
            const graphicItems = store.getters["graphics/getCurrentReferenceGraphics"];
            const canvas = store.getters["graphics/getCanvas"];

            const data = graphic.getGraphicsProps(graphicItems, canvas);

            store.dispatch("algorithms/updateCurrentReferenceAlgorithmGraphics", data);
            
            // Ensure we have a valid golden_position value
            const goldenPositionValue = (referenceToSave.value && 
                                       currentReferencePointIdx.value >= 0 && 
                                       currentReferencePointIdx.value < referenceToSave.value.length) 
                                       ? referenceToSave.value[currentReferencePointIdx.value] 
                                       : [0, 0];
            
            await store.dispatch("algorithms/updateCurrentReferenceAlgorithmProperty", {
                    name: 'golden_position',
                    value: goldenPositionValue
            });

            const currentAlgorithm = store.getters["algorithms/getCurrentReferenceAlgorithm"];

            const component = {
                uid: currentComponent.value.uid,
                name: payload.name,
                imageSourceUid: payload.imageSourceUid,
                algorithmUid: currentAlgorithm.uid,
                algorithmType: currentAlgorithm.type
            };

            updateComponent(component).then(() => {
                const algorithm = store.getters["algorithms/getConfiguredAlgorithmById"](currentAlgorithm.uid);

                if(algorithm)
                {
                    store.dispatch("algorithms/updateConfiguredAlgorithm", currentAlgorithm).then(() => {
                        store.dispatch("log/addEvent", {
                            type: moduleName.toUpperCase(),
                            user: currentUser.value ? currentUser.value.username : "Unknown",
                            title: moduleName.toUpperCase() + ' Modified',
                            description: `${currentComponent.value.name} was modified.`
                        });

                        setNotification(3000, "Configuration saved.", 'fc-ok');
                    }).catch(() => {
                        setNotification(3000, "Error while trying to save component.", 'bi-exclamation-circle-fill');
                    });
                }
                else
                {
                    store.dispatch("algorithms/addConfiguredAlgorithm", currentAlgorithm).then(() => {
                        store.dispatch("log/addEvent", {
                            type: moduleName.toUpperCase(),
                            user: currentUser.value ? currentUser.value.username : "Unknown",
                            title: moduleName.toUpperCase() + ' Modified',
                            description: `${currentComponent.value.name} was modified.`
                        });

                        setNotification(3000, "Configuration saved.", 'fc-ok');
                    }).catch(() => {
                        setNotification(3000, "Error while trying to save component.", 'bi-exclamation-circle-fill');
                    });
                }
            }).catch(() => {
                setNotification(3000, "Error while trying to save component.", 'bi-exclamation-circle-fill');
            });
        }

        function downloadAlgorithm(){
            let text = JSON.stringify(currentAlgorithm.value);
            let filename = "algorithm.json";

            let element = document.createElement('a');
            element.setAttribute('href', 'data:application/json;charset=utf-8,' + encodeURIComponent(text));
            element.setAttribute('download', filename);

            element.style.display = 'none';
            document.body.appendChild(element);

            element.click();
            document.body.removeChild(element);
        }

        function saveRefChanged(value) {
            saveRef.value = value;
        }

        function saveMasks(polygons) {
            const masks = [];
            const masksColors = [];

            for(const polygon of polygons)
            {
                const points = [];

                const canvas = store.getters["graphics/getCanvas"];
                const updatedPoints = graphic.getUpdatedPolygonPoints(polygon, canvas);

                for(let i = 0; i < updatedPoints.length; i++)
                {
                    points.push([updatedPoints[i].x, updatedPoints[i].y]);
                }

                masks.push(points);

                let hexColor = polygon.fill;

                let r = parseInt(hexColor.substring(1, 3), 16);
                let g = parseInt(hexColor.substring(3, 5), 16);
                let b = parseInt(hexColor.substring(5, 7), 16);

                masksColors.push([r, g, b]);
            }
            selectedRect.value.set({masks: masks, masksColors: masksColors})

            const canvas = store.getters["graphics/getCanvas"];

            let data = graphic.getRectProps(selectedRect.value, canvas);
            selectedGraphic.value = data;
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

        onMounted(() => {
            if(currentConfiguration.value)
            {
                componentsRetrieving.value = true;
                store.dispatch("components/loadComponents", {
                    type: moduleName
                });
            }
        });

        onBeforeUnmount(() => {
            resultsWatch();
            store.dispatch("algorithms/setCurrentReferenceAlgorithm", null);
            store.dispatch("algorithms/setAlgorithmResult", null);
            store.dispatch("components/setReferences", []);
            store.dispatch("components/setCurrentComponent", null);
            store.dispatch("graphics/resetReferenceGraphicItems");
        });

        return {
            moduleName,
            components,
            algorithms,
            currentImageSourceId,
            currentComponent,
            currentAlgorithm,
            algorithmAttributes,
            parameters,
            currentGraphics,
            showCamera,
            resultImage,
            outputImages,
            feedLocation,
            data,
            componentLoading,
            componentsRetrieving,
            algorithmId,
            currentConfiguration,
            selectedGraphic,
            showMasks,
            showResults,
            showNotification,
            notificationIcon,
            notificationMessage,
            notificationTimeout,
            showSelectReferenceDialog,
            referenceToSave,
            currentReferencePointIdx,
            referenceOverlay,
            hole,
            circleRefPoint,
            updateGraphics,
            loadComponent,
            removeComponent,
            addComponent,
            changeCameraStatus,
            singleRunComponent,
            liveProcessAlgorithm,
            updateImageSource,
            onAlgorithmChanged,
            onImportPathChanged,
            saveComponent,
            downloadAlgorithm,
            saveRefChanged,
            downloadAlgorithm,
            selectionChanged,
            selectionCleared,
            selectionModified,
            saveMasks,
            clearNotification,
            changeReferencePoint,
            closeSelectReferenceDialog
        };
    }
}
</script>

<style scoped>
.flex-container {
    display: flex;
    flex-direction: column;
    width: 100%;
    height: 95%;
    color: white;
    margin: 0;
}

.list-wrapper {
    margin: 1%;
    height: 9%;
}

.control-camera-container {
    display: flex;
    height: 90%;
}

.results-vis{
    display: flex;
    flex-direction: column;
    width: 100%;
    height: 100%;
}

.control {
    display: flex;
    flex-direction: column;
}

.results-table-wrapper {
    width: 98%;
    margin: 0% 1%;
}

.camera-wrapper{
    display: flex;
    height: 100%;
}

.camera-scene-item {
    margin-right: 1%;
    height: 100%;
    width: 98%;
}

.rounded-button {
    border-radius: 0 10px 10px 0;
    background-color: rgb(204, 161, 82);
    border: none;
    color: white;
    padding: 10px 20px;
    position: absolute;
    width: 5vw;
    top: 55%;
    left: 0%;
}

button:disabled,
button[disabled]{
  border: 1px solid #999999;
  background-color: #cccccc;
  color: #666666;
  cursor: not-allowed;
}

.action-button {
    width: 100%;
    height: 100%;
    background-color: rgb(0, 0, 0);
    border: none;
    /* padding: 5% 35%; */
    border-radius: inherit;
    margin-right: 2%;
}

.button-container {
    display: flex;
    width: 100%;
    height: 100%;
    justify-content: center;
    align-items: center;
    color: rgb(204, 161, 82);
}

.button-icon {
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
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

.results-btn-container {
    position: absolute;
    top: 88%;
    left: 95%;
    width: 4%;
    height: 4%;
    z-index: 20;
    background-color: rgb(0, 0, 0);
    border-radius: 5px;
}

.results-container {
    position: absolute;
    top: 55%;
    left: 70vw;
    width: 30vw;
    height: 35%;
    z-index: 20;
    background-color: rgb(21, 20, 20);
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
    width: 5vw;
    margin: 0% 2%;
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

.action-control {
    margin: 0;
    width: 100%;
    display: flex;
    justify-content: flex-end;
    height: 5.5vh;
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
</style>