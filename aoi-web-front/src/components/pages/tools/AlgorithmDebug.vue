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
import { ref, computed, watch, onBeforeUnmount } from 'vue';
import { useStore } from 'vuex';
import { uuid } from "vue3-uuid";

import CameraScene from '../../camera/CameraScene.vue';
import DirectoryFilesList from '../../layout/DirectoryFilesList.vue';
import AlgorithmDebugControl from '../../layout/AlgorithmDebugControl.vue';
import MaskScene from '../../layout/MaskScene.vue';

import graphic from '../../../utils/graphics.js';
import { ipAddress, port } from '../../../url';
import useAlgorithms from '../../../hooks/algorithms.js';
import useGraphics from '../../../hooks/graphics.js';

import useNotification from '../../../hooks/notifications.js'
import * as fabric from 'fabric';

export default {
    components: {
        CameraScene,
        DirectoryFilesList,
        AlgorithmDebugControl,
        MaskScene
    },

    setup() {
        const show = ref(false);
        const showMasks = ref(false);

        const feedLocation = ref('');
        const currentImageSourceId = ref(null);

        const imageEncoding = ref('');

        const disableActions = ref(true);

        let liveProcessSocket = null;

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

        const store = useStore();

        const {showNotification, notificationMessage, notificationIcon, notificationTimeout, 
            setNotification, clearNotification} = useNotification();

        const { selectedGraphic, graphicsObject, _, graphicItems,
            canvas, updateGraphics, selectionChanged, selectionCleared, selectionModified,
            saveMasks } = useGraphics();

        const { _2, algorithms, currentAlgorithm, algorithmAttributes, parameters,
            resultImage, outputImages, _3, _4, _5, loadUIandAlgorithm, _6,
            _7, download, _8, _9, _10, liveResultMsgRecv, setLiveAlgorithmSocket } = useAlgorithms(null, null, currentImageSourceId, null, graphicsObject, ipAddress, port);

        const referenceAlgorithms = computed(function () {
            return store.getters["algorithms/getReferenceAlgorithms"].map(alg => alg.type);
        });

        const currentReferenceAlgorithm = computed(function () {
            return store.getters["algorithms/getCurrentReferenceAlgorithm"];
        });

        const referenceAlgorithmAttributes = computed(function () {
            return store.getters["algorithms/getCurrentReferenceAlgorithmAttributes"];
        });

        const referenceParameters = computed(function () {
            if (currentReferenceAlgorithm.value)
                return currentReferenceAlgorithm.value.parameters;
            else
                return [];
        });

        const algorithmGraphics = computed(function () {
            return store.getters["graphics/getCurrentGraphics"];
        });

        const referenceGraphics = computed(function () {
            return store.getters["graphics/getCurrentReferenceGraphics"];
        });

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
            return (!currentAlgorithm.value && !currentReferenceAlgorithm.value) || (!currentImageSourceId.value && !imageEncoding.value);
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
                        objectCaching: false,
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
                        objectCaching: false,
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
                store.dispatch("algorithms/setStaticImage", newValue);
            }
            else {
                store.dispatch("algorithms/setStaticImage", null);
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
                store.dispatch("algorithms/setCurrentReferenceAlgorithm", null);
                store.dispatch("algorithms/setCurrentReferenceAlgorithmAttributes", null);
                store.dispatch("graphics/resetReferenceGraphicItems");
                store.dispatch("algorithms/setAlgorithmResult", null);
                store.dispatch("algorithms/resetLiveAlgorithmReference");
            }
        });

        function algorithmChanged(value) {
            currentAlgorithmName.value = value;
        }

        watch(currentAlgorithmName, (newValue) => {
            if (newValue) {
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

                if (currentTab.value === tabs.value[0]) {
                    algorithm = store.getters["algorithms/getReferenceAlgorithmByType"](loadedAlgorithm.value.type);
                }
                else {
                    algorithm = store.getters["algorithms/getAlgorithmByType"](loadedAlgorithm.value.type);
                }

                if (algorithm !== undefined) {
                    if (algorithm.type === currentAlgorithmName.value) {
                        if (currentTab.value === tabs.value[0]) {
                            store.dispatch("algorithms/loadCurrentReferenceAlgorithmFromObject", loadedAlgorithm.value.parameters);
                        }
                        else {
                            store.dispatch("algorithms/loadCurrentAlgorithmFromObject", loadedAlgorithm.value.parameters);
                        }

                        loadedAlgorithm.value = null;
                    }
                    else {
                        if (currentTab.value === tabs.value[0]) {
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

        async function loadReferenceAlgorithmUI(type) {
            await store.dispatch("algorithms/loadReferenceAlgorithm", {
                type: type
            });

            await store.dispatch("algorithms/setReferenceAlgorithm", {
                type: type
            });

            store.dispatch("algorithms/loadCurrentReferenceAlgorithmFromParameters", {
                attributes: referenceAlgorithmAttributes.value,
                type: type
            });
        }

        async function onAlgorithmChanged(type) {
            await loadUIandAlgorithm(type, null);

            if (loadedAlgorithm.value) {
                store.dispatch("algorithms/loadCurrentAlgorithmFromObject", loadedAlgorithm.value.parameters);
                loadedAlgorithm.value = null;
            }
        }

        async function onReferenceAlgorithmChanged(type) {
            await loadReferenceAlgorithmUI(type);

            if (loadedAlgorithm.value) {
                store.dispatch("algorithms/loadCurrentReferenceAlgorithmFromObject", loadedAlgorithm.value.parameters);
                loadedAlgorithm.value = null;
            }
        }

        function updateImageSource(id) {
            currentImageSourceId.value = id;

            if (id) {
                feedLocation.value = `ws://${ipAddress}:${port}/image_source/${id}/ws`;
                disableActions.value = false;
            }
            else {
                disableActions.value = true;
            }
        }

        function startCamera() {
            show.value = true;
        }

        function stopCamera() {
            show.value = false;
        }

        async function singleRunAlgorithm() {
            const data = graphic.getGraphicsProps(graphicItems.value, canvas.value);

            await store.dispatch("algorithms/updateCurrentAlgorithmProperty", {
                name: 'graphics',
                value: data
            });

            await store.dispatch("algorithms/setLiveAlgorithmReference");

            if (currentReferenceAlgorithm.value) {
                await store.dispatch("algorithms/updateCurrentReferenceAlgorithmProperty", {
                    name: 'golden_position',
                    value: referenceToSave.value[currentReferencePointIdx.value]
                });
            }

            if (selectedTabSource.value === "Image Source") {
                store.dispatch("algorithms/singleProcessAlgorithmCamera", {
                    uid: currentImageSourceId.value,
                    type: "component"
                }).catch((err) => {
                    setNotification(3000, err, 'bi-exclamation-circle-fill');

                    store.dispatch("errors/addError", {
                        id: uuid.v4(),
                        title: "Algorithm Debug Error",
                        description: err
                    });
                });
            }
            else {
                store.dispatch("algorithms/singleProcessAlgorithmStatic", {
                    type: "component"
                }).catch((err) => {
                    setNotification(3000, err, 'bi-exclamation-circle-fill');
                    
                    store.dispatch("errors/addError", {
                        id: uuid.v4(),
                        title: "Algorithm Debug Error",
                        description: err
                    });
                });
            }
        }

        async function liveProcessAlgorithm(state) {
            if (state) {
                const data = graphic.getGraphicsProps(graphicItems.value, canvas.value);

                await store.dispatch("algorithms/updateCurrentAlgorithmProperty", {
                    name: 'graphics',
                    value: data
                });

                await store.dispatch("algorithms/setLiveAlgorithmReference");

                if (currentReferenceAlgorithm.value) {
                    await store.dispatch("algorithms/updateCurrentReferenceAlgorithmProperty", {
                        name: 'golden_position',
                        value: referenceToSave.value[currentReferencePointIdx.value]
                    });
                }

                let url = null;
                let id = uuid.v4();

                if (selectedTabSource.value === "Image Source") {
                    url = `ws://${ipAddress}:${port}/algorithm/live_algorithm_result/${currentImageSourceId.value}/${id}/ws`;
                }
                else {
                    url = `ws://${ipAddress}:${port}/algorithm/live_algorithm_result/${id}/ws`;
                }

                liveProcessSocket = new WebSocket(url);

                liveProcessSocket.addEventListener('open', onSocketOpen);
                liveProcessSocket.addEventListener('message', liveResultMsgRecv);

                setLiveAlgorithmSocket(liveProcessSocket);
            }
            else {
                if (liveProcessSocket) {
                    liveProcessSocket.send(JSON.stringify({ command: "disconnect" }));

                    liveProcessSocket.removeEventListener('open', onSocketOpen);
                    liveProcessSocket.removeEventListener('message', liveResultMsgRecv);

                    liveProcessSocket.close();
                    liveProcessSocket = null;

                    setLiveAlgorithmSocket(liveProcessSocket);
                }
            }
        }

        async function singleRunReference() {
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

            if (selectedTabSource.value === "Image Source") {
                await store.dispatch("algorithms/singleProcessReferenceCamera", {
                    uid: currentImageSourceId.value,
                    type: "component"
                }).catch((err) => {
                    setNotification(3000, err, 'bi-exclamation-circle-fill');

                    store.dispatch("errors/addError", {
                        id: uuid.v4(),
                        title: "Algorithm Debug Error",
                        description: err
                    });
                });
            }
            else {
                await store.dispatch("algorithms/singleProcessReferenceStatic", {
                    type: "component"
                }).catch((err) => {
                    setNotification(3000, err, 'bi-exclamation-circle-fill');

                    store.dispatch("errors/addError", {
                        id: uuid.v4(),
                        title: "Algorithm Debug Error",
                        description: err
                    });
                });
            }
        }

        async function liveProcessReference(state) {
            if (state) {
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

                let url = null;
                let id = uuid.v4();

                if (selectedTabSource.value === "Image Source") {
                    url = `ws://${ipAddress}:${port}/algorithm/live_reference/${currentImageSourceId.value}/${id}/ws`;
                }
                else {
                    url = `ws://${ipAddress}:${port}/algorithm/live_reference/${id}/ws`;
                }

                liveProcessSocket = new WebSocket(url);

                liveProcessSocket.addEventListener('open', onSocketOpen);
                liveProcessSocket.addEventListener('message', liveResultMsgRecv);

                setLiveAlgorithmSocket(liveProcessSocket);
            }
            else {
                if (liveProcessSocket) {
                    liveProcessSocket.send(JSON.stringify({ command: "disconnect" }));

                    liveProcessSocket.removeEventListener('open', onSocketOpen);
                    liveProcessSocket.removeEventListener('message', liveResultMsgRecv);

                    liveProcessSocket.close();
                    liveProcessSocket = null;

                    setLiveAlgorithmSocket(liveProcessSocket);
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
                objectCaching: false,
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

        onBeforeUnmount(() => {
            resultsWatch();
            store.dispatch("algorithms/setCurrentAlgorithm", null);
            store.dispatch("algorithms/setCurrentAlgorithmAttributes", null);
            store.dispatch("algorithms/setCurrentReferenceAlgorithm", null);
            store.dispatch("algorithms/setCurrentReferenceAlgorithmAttributes", null);
            store.dispatch("graphics/resetReferenceGraphicItems");
            store.dispatch("graphics/resetGraphicsItems");
            store.dispatch("algorithms/setAlgorithmResult", null);
            store.dispatch("algorithms/resetLiveAlgorithmReference");
        });

        return {
            algorithms,
            referenceAlgorithms,
            currentImageSourceId,
            currentAlgorithm,
            currentReferenceAlgorithm,
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