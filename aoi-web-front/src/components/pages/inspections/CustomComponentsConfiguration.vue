<template>
    <div class="flex-container">
        <div class="playground-container" v-show="playgroundMode">
            <div class="alg-types">
                <div draggable="true" @dragstart="onDragStart" class="alg-box" v-for="t in types" :key="t.name" :data-active="t.name">
                    {{ t.name }}
                </div>
            </div>
            
            <div id="playground-canvas-container" ref="playgroundContainer">
                <canvas id="playground"></canvas>
            </div>
            <div class="control-panel">
                <div class="canvas-actions">
                    <div class="action">
                        <base-action-button width="3.5vw" height="6vh" :show-active="true" @state-changed="setConnectMode">
                            <font-awesome-icon icon="network-wired"/>
                        </base-action-button>
                    </div>
                    <div class="action">
                        <base-action-button width="3.5vw" height="6vh" :show-active="false" @state-changed="deleteCurrentActive">
                            <font-awesome-icon icon="trash-can"/>
                        </base-action-button>
                    </div>
                    <div class="action">
                        <base-action-button width="3.5vw" height="6vh" :show-active="false" @state-changed="saveConfiguration">
                        <div class="button-content-wrapper">
                            <font-awesome-icon icon="sd-card"/>
                            <div style="font-size: large; font-weight: bold;">
                                {{ unsavedChanges }}
                            </div>
                        </div>
                        </base-action-button>
                    </div>
                </div>
            </div>
        </div>
        <div class="components-control-container" v-show="!playgroundMode">
            <div class="list-wrapper">
                <components-list
                    width="100%"
                    height="100%"
                    :components="components"
                    :disable="!currentConfiguration"
                    @save-component="addComponent"
                    @remove-component="remove"
                    @load-component="loadComponent"
                ></components-list>
            </div>
            <div class="control-camera-container">
                <div class="results-vis">
                    <div class="camera-wrapper">
                        <div class="camera-scene-item">
                            <camera-scene
                                width="100%"
                                height="100%"
                                :show="showCamera && !showInputs"
                                :camera-feed="true"
                                :feed-location="feedLocation"
                                :static-images="inputImages"
                                :id="1"
                                canvas-id="camera-scene-canvas"
                                :graphics="currentGraphics"
                                @graphics-changed="updateGraphics"
                            ></camera-scene>
                        </div>
                        <div class="camera-scene-item">
                            <camera-scene
                                width="100%"
                                height="100%"
                                :camera-feed="false"
                                :static-images="outputImages"
                                :id="2"
                                canvas-id="result-canvas"
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
                        @show-camera="changeCameraStatus"
                        @single-run="singleRunComponent"
                        @live-process="liveProcessAlgorithm"
                        @update-image-source="updateImageSource"
                        @algorithm-changed="onAlgorithmChanged"
                        @save-component="saveComponent"
                        @import-path-changed="onImportPathChanged"
                        @download-algorithm="downloadAlgorithm"
                    ></component-control>
                </div>
            </div>

            <div class="results-btn-container" v-if="!showResults">
                <button class="action-button" @click="showResults = true" :disabled="true">
                    <div class="button-container">
                        <div class="button-icon">
                            <v-icon name="vi-file-type-light-json" scale="1"/>
                        </div>
                    </div>
                </button>
            </div>
            <div class="results-container" v-else>
                <json-data-container width="auto" height="29vh" @closed="showResults = false"></json-data-container>
            </div>
        </div>
        <div class="view-actions">
            <div>
                <base-action-button width="3.5vw" height="6vh" :show-active="false" @state-changed="switchMode" :disabled="!currentComponent">
                    <font-awesome-icon :icon="modeIconName"/>
                </base-action-button>
            </div>
        </div>
        <base-notification
            :show="showNotification"
            :timeout="notificationTimeout"
            :message="notificationMessage"
            :icon="notificationIcon"
            :notificationType="notificationType"
            height="15vh"
            color="#CCA152"
            @close="clearNotification"
        />
    </div>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { useStore } from 'vuex';
import { v4 as uuidv4 } from "uuid";
import { logger } from '@/utils/logger';

import * as fabric from 'fabric';

import { RectAlgIO } from '../../../utils/fabric_objects.js';

import ComponentsList from '../../layout/ComponentsList.vue';
import ComponentControl from '../../layout/ComponentControl.vue';
import CameraScene from '../../camera/CameraScene.vue';
import AlgorithmResultTable from '../../layout/AlgorithmResultTable.vue';
import JsonDataContainer from '../../layout/JsonDataRenderer.vue';

import graphic from '../../../utils/graphics';
import { ipAddress, port } from '../../../url';
import useComponents from '../../../hooks/components.ts';
import useNotification, { NotificationType } from '../../../hooks/notifications.ts';
import { ComponentMessages, ConfigurationMessages, GeneralMessages } from '@/constants/notifications';
import { useWebSocket, useFabricCanvas, useLoadingState } from '@/composables/useStore';
import { DEFAULT_IMAGE_DATA_URI_PREFIX, ImageDataUtils } from '../../../utils/imageConstants';

export default{
    components: {
        ComponentsList,
        ComponentControl,
        CameraScene,
        AlgorithmResultTable,
        JsonDataContainer
    },

    setup(){
        const moduleName = 'custom_component';
        const store = useStore();

        // Initialize loading state composable
        const { isLoading, setLoading, withLoading } = useLoadingState();
        
        const {showNotification, notificationMessage, notificationIcon, notificationTimeout, notificationType,
            setTypedNotification, clearNotification} = useNotification();

        // playground variables
        const playgroundMode = ref(false);
        const playgroundContainer = ref(null);
        
        // Initialize Fabric.js canvas using composable
        const {
            canvas: playgroundCanvas,
            initCanvas,
            clearCanvas,
            throttledRender,
            batchRender,
            addObjects,
            removeObjects
        } = useFabricCanvas('playground', {
            isDrawingMode: false,
            selection: true,
            fireRightClick: true,
            stopContextMenu: true,
            containerRef: playgroundContainer
        });
        const algTypesContainer = ref(null);

        const currentDraggedName = ref('');

        const isConnectMode = ref(false);

        const unsavedChanges = ref('');

        let currentCompoundData = null;

        let blockToConnect = null;
        let objectToConnect = null;

        const circleRadius = 8;
        const typeToColor = {
            "NumpyType": "rgb(55, 48, 107)",
            "IntegerType": "rgb(158, 71, 132)",
            "ListType": "rgb(102, 52, 127)",
            "DictType": "rgb(210, 118, 133)"
        }

        // component variables
        const showCamera = ref(false);
        const showInputs = ref(false);
        const showResults = ref(false);

        const feedLocation = ref('');
        const currentImageSourceId = ref('');

        const algorithms = ref([]);
        const algorithmId = ref('');

        const outputImages = ref([]);
        const inputImages = ref([]);

        let graphicsObject = null;
        let currentGraphicsId = -1;

        // WebSocket state
        let liveProcessSocketInstance = null;

        const compoundResult = ref([]);

        const { currentComponent, _, _2, components, load, remove, update, add } = useComponents(moduleName);

        const currentConfiguration = computed(function() {
            return store.getters["configurations/getCurrentConfiguration"];
        });

        const currentUser = computed(function() {
            return store.getters["auth/getCurrentUser"];
        });

        const types = computed(function() {
            return store.getters["algorithms/getBasicAlgorithms"];
        });

        const resultImage = computed(function() {
            const result = store.getters["algorithms/getAlgorithmResult"];
            if(result && result.frame) {
                return Array.isArray(result.frame) ? result.frame[0] : result.frame;
            }
            return '';
        });

        const unwatch = store.watch(
            (_, getters) => getters["algorithms/getAlgorithmResult"],
            (newValue) => {
                compoundResult.value = newValue ? newValue.results : [];

                if(algorithmId.value !== '' && compoundResult.value.length > algorithmId.value)
                {
                    let inputs = compoundResult.value[algorithmId.value].inputs;
                    let outputs = compoundResult.value[algorithmId.value].outputs;

                    inputImages.value = [];
                    outputImages.value = [];

                    for(const output of outputs)
                    {
                        outputImages.value.push(ImageDataUtils.createJpegDataURI(output));
                    }

                    for(const input of inputs)
                    {
                        inputImages.value.push(ImageDataUtils.createJpegDataURI(input));
                    }
                }
            }
        );

        const algorithmAttributes = computed(function() {
            let id = parseInt(algorithmId.value, 10);
            const attributes = store.getters["algorithms/getBasicAlgorithmAttributesAtIndex"](id);
            return attributes;
        });

        const parameters = computed(function() {
            let id = parseInt(algorithmId.value, 10);
            const params = store.getters["algorithms/getCurrentBasicAlgorithmAtIndex"](id);
            return params;
        });

        const currentGraphics = computed(function() {
            let id = parseInt(algorithmId.value, 10);
            const graphics = store.getters["graphics/getCurrentCompoundGraphicsAtIdx"](id);

            if(graphics)
            {
                return graphics;
            }

            return [];
        })

        function switchMode(){
            playgroundMode.value = !playgroundMode.value;
        }

        const modeIconName = computed(function(){
            return playgroundMode.value ? 'play' : 'cubes-stacked';
        });

        function getCurrentType(name){
            return types.value.find(alg => alg.name === name);
        }

        function makeLine(coords, color){
            return new fabric.Line(coords, {
                fill: color || 'white',
                stroke: color || 'white',
                strokeWidth: 4,
                selectable: false,
                evented: false
            });
        }

        function makeCircle(left, top, radius, color){
            let c = new fabric.Circle({
                left: left,
                top: top,
                strokeWidth: 4,
                radius: radius,
                fill: color || '#fff',
                stroke: '#666'
            });

            return c
        }

        function addAlgorithmBlockToCanvas(type, width, height, posX, posY){
            const currentDraggedType = getCurrentType(type);

            const rect = new fabric.Rect({
                fill: '#CC527A',
                width: width,
                height: height,
                objectCaching: true,
                hasControls: false,
                selectable: false,
                originX: 'center',
                originY: 'center'
            });

            const text = new fabric.FabricText(currentDraggedType.name, {
                fontFamily: 'Calibri',
                fontSize: 30,
                originX: 'center',
                originY: 'center',
                fill: 'rgba(255, 255, 255, 1.0)'
            });

            let algType = new fabric.Group([rect, text], {
                left: posX,
                top: posY,
                hasControls: false,
                selectable: true,
                subTargetCheck: true
            });

            const inputCellHeight = height / currentDraggedType.inputs.length;

            for(const [i, input] of currentDraggedType.inputs.entries())
            {
                let inputName = input.name + ": " + input.type;
                let inputRect = new RectAlgIO({
                    fill: typeToColor[input.type],
                    width: 150,
                    height: inputCellHeight,
                    objectCaching: true,
                    hasControls: false,
                    selectable: false,
                    originX: 'left',
                    originY: 'top',
                    left: algType.left,
                    top: algType.top + (i * inputCellHeight),
                    stroke: 'black',
                    strokeWidth: 1,
                    rectType: 'input',
                    label: inputName,
                    valueType: input.type,
                    index: i
                });

                algType.addWithUpdate(inputRect);
            }

            const outputCellHeight = height / currentDraggedType.outputs.length;

            for(const [i, output] of currentDraggedType.outputs.entries())
            {
                let outputName = output.name + ": " + output.type;
                let outputRect = new RectAlgIO({
                    fill: typeToColor[output.type],
                    width: 150,
                    height: outputCellHeight,
                    objectCaching: true,
                    hasControls: false,
                    selectable: false,
                    left: algType.left + algType.width - 150,
                    top: algType.top + (i * outputCellHeight),
                    stroke: 'black',
                    strokeWidth: 1,
                    rectType: 'output',
                    label: outputName,
                    valueType: output.type,
                    index: i
                });

                algType.addWithUpdate(outputRect);
            }

            addObjects(algType);
        }

        function handleDrop(event){
            unsavedChanges.value = '*';

            const canvasX = event.e.layerX;
            const canvasY = event.e.layerY;

            const width = 500;
            const height = 150;

            addAlgorithmBlockToCanvas(currentDraggedName.value, width, height, canvasX - (width / 2), canvasY - (height / 2));
        }

        function checkIfClickInside(object, mouseCoords){
            return mouseCoords.x > object.left 
                    && mouseCoords.y > object.top 
                    && mouseCoords.x < object.left + object.width 
                    && mouseCoords.y < object.top + object.height;
        }

        function handleMouseDown(event){
            if(isConnectMode.value)
            {
                if(event.target)
                {
                    if(event.button === 1)
                    {
                        const center = event.target.getCenterPoint();
                        
                        let algorithmType = null;

                        const objects = event.target.getObjects();
                        objects.forEach(function(item, _){

                            if(item.type === 'text')
                            {
                                algorithmType = item.text;
                            }

                            const realX = center.x + item.left;
                            const realY = center.y + item.top;

                            const toCheck = {
                                top: realY,
                                left: realX,
                                width: item.width,
                                height: item.height
                            };

                            const mouseCoords = {
                                x: event.e.layerX,
                                y: event.e.layerY
                            };

                            if(checkIfClickInside(toCheck, mouseCoords) && item.type === 'rectAlgIO')
                            {
                                let circleX = null;
                                let circleY = null;

                                if(item.get('rectType') === 'input')
                                {
                                    circleX = realX;
                                    circleY = realY + (item.height / 2);
                                }
                                else
                                {
                                    circleX = realX + item.width;
                                    circleY = realY + (item.height / 2);
                                }

                                if(blockToConnect && objectToConnect != event.target)
                                {
                                    if(blockToConnect.item.get('rectType') !== item.get('rectType') && blockToConnect.item.get('valueType') === item.get('valueType'))
                                    {
                                        let circle1 = makeCircle(blockToConnect.circleX - circleRadius, blockToConnect.circleY - circleRadius, circleRadius, typeToColor[item.get('valueType')]);
                                        
                                        let circle2 = makeCircle(circleX - circleRadius, circleY - circleRadius, circleRadius, typeToColor[item.get('valueType')]);

                                        let line1 = null;
                                        let line2 = null;
                                        let line3 = null;
                                        let line4 = null;
                                        let line5 = null;

                                        if(blockToConnect.circleY > circleY) //input of box below clicked first
                                        {
                                            line1 = makeLine([circleX, circleY, circleX + 100, circleY], typeToColor[item.get('valueType')]);
                                            line2 = makeLine([circleX + 100, circleY, circleX + 100, objectToConnect.top - 20], typeToColor[item.get('valueType')]);
                                            line3 = makeLine([circleX + 100, objectToConnect.top - 20, objectToConnect.left - 100, objectToConnect.top - 20], typeToColor[item.get('valueType')]);
                                            line4 = makeLine([objectToConnect.left - 100, blockToConnect.circleY, objectToConnect.left - 100, objectToConnect.top - 20], typeToColor[item.get('valueType')]);
                                            line5 = makeLine([blockToConnect.circleX, blockToConnect.circleY, objectToConnect.left - 100, blockToConnect.circleY], typeToColor[item.get('valueType')]);

                                            circle1.line1 = line5;
                                            circle1.line2 = line4;
                                            circle1.line3 = line3;
                                            circle1.line4 = line2;
                                            circle1.line5 = line1;
                                            circle1.offset = -100;

                                            circle2.line1 = line1;
                                            circle2.line2 = line2;
                                            circle2.line3 = line3;
                                            circle2.line4 = line4;
                                            circle2.line5 = line5;
                                            circle2.offset = 100;
                                        }
                                        else //output of box above clicked first
                                        {
                                            line1 = makeLine([blockToConnect.circleX + 100, blockToConnect.circleY, blockToConnect.circleX, blockToConnect.circleY], typeToColor[item.get('valueType')]);
                                            line2 = makeLine([blockToConnect.circleX + 100, event.target.top - 20, blockToConnect.circleX + 100, blockToConnect.circleY], typeToColor[item.get('valueType')]);
                                            line3 = makeLine([event.target.left - 100, event.target.top - 20, blockToConnect.circleX + 100, event.target.top - 20], typeToColor[item.get('valueType')]);
                                            line4 = makeLine([event.target.left - 100, circleY, event.target.left - 100, event.target.top - 20], typeToColor[item.get('valueType')]);
                                            line5 = makeLine([circleX, circleY, event.target.left - 100, circleY], typeToColor[item.get('valueType')]);

                                            circle1.line1 = line1;
                                            circle1.line2 = line2;
                                            circle1.line3 = line3;
                                            circle1.line4 = line4;
                                            circle1.line5 = line5;
                                            circle1.offset = 100;

                                            circle2.line1 = line5;
                                            circle2.line2 = line4;
                                            circle2.line3 = line3;
                                            circle2.line4 = line2;
                                            circle2.line5 = line1;
                                            circle2.offset = -100;
                                        }

                                        circle1.pairBlock = event.target;
                                        circle1.pairCircle = circle2;

                                        circle2.pairBlock = objectToConnect;
                                        circle2.pairCircle = circle1;

                                        if(blockToConnect.item.get('rectType') === 'input')
                                        {
                                            blockToConnect.item.outputIndex = item.get('index');
                                            blockToConnect.item.circle = circle1;
                                        }
                                        else
                                        {
                                            item.outputIndex = blockToConnect.item.get('index');
                                            item.circle = circle2;
                                        }

                                        objectToConnect.addWithUpdate(circle1);
                                        event.target.addWithUpdate(circle2);

                                        addObjects([line1, line2, line3, line4, line5]);

                                        blockToConnect.item.set({'fill': typeToColor[blockToConnect.item.get('valueType')]});

                                        blockToConnect = null;
                                        objectToConnect = null;

                                        unsavedChanges.value = '*';
                                    }
                                    else
                                    {
                                        blockToConnect.item.set({'fill': typeToColor[blockToConnect.item.get('valueType')]});

                                        item.set({'fill': 'grey'});

                                        objectToConnect = event.target;
                                        blockToConnect = {
                                            item: item,
                                            circleX: circleX,
                                            circleY: circleY,
                                            algorithmType: algorithmType
                                        };
                                    }
                                }
                                else
                                {
                                    if(blockToConnect)
                                    {
                                        blockToConnect.item.set({'fill': typeToColor[blockToConnect.item.get('valueType')]});
                                    }

                                    item.set({'fill': 'grey'});

                                    objectToConnect = event.target;
                                    blockToConnect = {
                                        item: item,
                                        circleX: circleX,
                                        circleY: circleY,
                                        algorithmType: algorithmType
                                    };
                                }
                            }
                        });
                    }
                }
            }
        }

        function onDragStart(e){
            currentDraggedName.value = e.target.dataset.active;
        }

        function setConnectMode(value){
            if(!value)
            {
                if(blockToConnect)
                {
                    blockToConnect.item.set({'fill': typeToColor[blockToConnect.item.get('valueType')]});
                }

                blockToConnect = null;
                objectToConnect = null;
            }
            isConnectMode.value = value;
            setPlaygroundItemsSelectable(!value);
        }

        function deleteCurrentActive(){
            let current = playgroundCanvas.value.getActiveObject();
            if(current)
            {
                const group = current.getObjects();
                group.forEach(function(groupItem, i){
                    if(groupItem.type === 'circle')
                    {
                        groupItem.pairBlock.removeWithUpdate(groupItem.pairCircle);

                        removeObjects([groupItem.line1, groupItem.line2, groupItem.line3, groupItem.line4, groupItem.line5]);
                    }
                });
                removeObjects(current);

                unsavedChanges.value = '*';
            }
        }

        async function saveConfiguration()
        {
            algorithms.value = [];
            let blocks = [];

            const groups = playgroundCanvas.value.getObjects();

            groups.forEach(function(group, i){
                if(group.type === 'group')
                {
                    blocks.push(group);
                }
            });

            blocks.sort(orderBlocks);

            let dataBlocks = []
            let types = []

            blocks.forEach(function(block, idx){
                const items = block.getObjects();
                let data = {
                    blockIndex: [],
                    outputIndex: []
                };

                for(const item of items)
                {
                    if(item.type === 'rectAlgIO' && item.get('rectType') === 'input')
                    {
                        if(item.circle)
                        {
                            const blockIdx = blocks.findIndex(b => b === item.circle.pairBlock);
                            data.blockIndex.splice(item.get('index'), 0, blockIdx);

                            if(blockIdx !== -1)
                            {
                                data.outputIndex.splice(item.get('index'), 0, item.outputIndex);
                            }
                            else
                            {
                                data.outputIndex.splice(item.get('index'), 0, -1);
                            }
                        }
                        else
                        {
                            data.blockIndex.splice(item.get('index'), 0, -1);
                            data.outputIndex.splice(item.get('index'), 0, -1);
                        }
                    }
                    if(item.type === 'text')
                    {
                        types.push(item.text);
                        algorithms.value.push(
                            {
                                uid: idx.toString(),
                                type: item.text
                            }
                        );
                    }
                }

                dataBlocks.push(data);
            });

            unsavedChanges.value = '';

            currentCompoundData = {
                types: types,
                data_blocks: dataBlocks
            }

            store.dispatch("algorithms/setBasicLiveAlgorithm", currentCompoundData);

            store.dispatch("algorithms/resetBasicAlgorithmsAttributes");
            store.dispatch("algorithms/resetCurrentBasicAlgorithms");

            store.dispatch("graphics/resetCompoundGraphicItems");

            await store.dispatch("algorithms/loadSelectedBasicAlgorithmsAttributes", {
                types: types
            });

            store.dispatch("algorithms/loadCurrentBasicAlgorithmsFromAttributes");
        }

        function orderBlocks(a, b){
            if(a.top < b.top)
            {
                return -1;
            }

            if(a.top > b.top)
            {
                return 1;
            }

            if(a.top === b.top)
            {
                if(a.left < b.left)
                {
                    return -1;
                }

                if(a.left > b.left)
                {
                    return 1;
                }

                if(a.left === b.left)
                {
                    return 0;
                }
            }
        }

        function setPlaygroundItemsSelectable(value){
            playgroundCanvas.value.discardActiveObject().renderAll();
            const obj = playgroundCanvas.value.getObjects();
            obj.forEach(function(item, i){
                item.set({selectable: value});
            });
            throttledRender();
        }

        function loadBlocks(types, blocks) {
            const width = 500;
            const height = 150;

            const blockMargin = 30;

            let currentBlockY = 20;
            const currentBlockX = 150;

            clearCanvas();

            for(const type of types)
            {
                addAlgorithmBlockToCanvas(type, width, height, currentBlockX, currentBlockY);

                currentBlockY += height + blockMargin;
            }

            for(const [blockIdx, block] of blocks.entries())
            {
                for(const [inputIdx, pairBlockIdx] of block.blockIndex.entries())
                {
                    if(pairBlockIdx !== -1)
                    {
                        const pairOutputIdx = block.outputIndex[inputIdx];

                        const currentBlock = playgroundCanvas.value.getObjects()[blockIdx];
                        const pairBlock = playgroundCanvas.value.getObjects()[pairBlockIdx];

                        const currentBlockItems = currentBlock.getObjects();
                        const pairBlockItems = pairBlock.getObjects();

                        let currentCircleX = null;
                        let currentCircleY = null;

                        let pairCircleX = null;
                        let pairCircleY = null;

                        let currentInputCircle = null;
                        let pairOutputCircle = null;

                        for(const currentItem of currentBlockItems)
                        {
                            if(currentItem.type === 'rectAlgIO' && currentItem.get('rectType') === 'input' && currentItem.get('index') === inputIdx)
                            {
                                const center = currentBlock.getCenterPoint();

                                const realX = center.x + currentItem.left;
                                const realY = center.y + currentItem.top;

                                currentCircleX = realX;
                                currentCircleY = realY + (currentItem.height / 2);

                                currentInputCircle = makeCircle(currentCircleX - circleRadius, currentCircleY - circleRadius, circleRadius, typeToColor[currentItem.get('valueType')]);

                                currentItem.outputIndex = pairOutputIdx;
                                currentItem.circle = currentInputCircle;

                                currentBlock.addWithUpdate(currentInputCircle);
                            }
                        }

                        for(const pairItem of pairBlockItems)
                        {
                            if(pairItem.type === 'rectAlgIO' && pairItem.get('rectType') === 'output' && pairItem.get('index') === pairOutputIdx)
                            {
                                const center = pairBlock.getCenterPoint();

                                const realX = center.x + pairItem.left;
                                const realY = center.y + pairItem.top;

                                pairCircleX = realX + pairItem.width;
                                pairCircleY = realY + (pairItem.height / 2);

                                pairOutputCircle = makeCircle(pairCircleX - circleRadius, pairCircleY - circleRadius, circleRadius, typeToColor[pairItem.get('valueType')]);
                                pairBlock.addWithUpdate(pairOutputCircle);

                                let line1 = makeLine([pairCircleX + 100, pairCircleY, pairCircleX, pairCircleY], typeToColor[pairItem.get('valueType')]);
                                let line2 = makeLine([pairCircleX + 100, currentBlock.top - 20, pairCircleX + 100, pairCircleY], typeToColor[pairItem.get('valueType')]);
                                let line3 = makeLine([currentBlock.left - 100, currentBlock.top - 20, pairCircleX + 100, currentBlock.top - 20], typeToColor[pairItem.get('valueType')]);
                                let line4 = makeLine([currentBlock.left - 100, currentCircleY, currentBlock.left - 100, currentBlock.top - 20], typeToColor[pairItem.get('valueType')]);
                                let line5 = makeLine([currentCircleX, currentCircleY, currentBlock.left - 100, currentCircleY], typeToColor[pairItem.get('valueType')]);

                                currentInputCircle.line1 = line5;
                                currentInputCircle.line2 = line4;
                                currentInputCircle.line3 = line3;
                                currentInputCircle.line4 = line2;
                                currentInputCircle.line5 = line1;
                                currentInputCircle.offset = -100;

                                pairOutputCircle.line1 = line1;
                                pairOutputCircle.line2 = line2;
                                pairOutputCircle.line3 = line3;
                                pairOutputCircle.line4 = line4;
                                pairOutputCircle.line5 = line5;
                                pairOutputCircle.offset = 100;

                                addObjects([line1, line2, line3, line4, line5]);

                                currentInputCircle.pairBlock = pairBlock;
                                currentInputCircle.pairCircle = pairOutputCircle;

                                pairOutputCircle.pairBlock = currentBlock;
                                pairOutputCircle.pairCircle = currentInputCircle;
                            }
                        }
                    }
                }
            }
        }

        // components
        // methods for component handling

        function addComponent(name) {
            try{
                logger.debug('Saving component', { name });
                add(name);

                store.dispatch("log/addEvent", {
                    type: moduleName.toUpperCase().replace(/_/g, ' '),
                    user: currentUser.value ? currentUser.value.username : 'Unknown',
                    title: moduleName.toUpperCase().replace(/_/g, ' ') + ' Added',
                    description: `New ` + moduleName.replace(/_/g, ' ') +  ` added: ${name}`
                });
                
                logger.info('Component saved successfully', { name });
            }catch(err) {
                logger.error('Failed to save component', err);
                setTypedNotification(
                    ComponentMessages.UPDATE_FAILED,
                    NotificationType.ERROR,
                    3000
                );
            }
            
        }

        async function loadComponent(id) {
            try {
                logger.debug('Loading component', { id });
                if(id)
                {
                    await load(id);

                    const types = currentComponent.value.algorithms.map(algorithm => algorithm.algorithmType);

                    algorithms.value = [];

                    for(const [idx, type] of types.entries())
                    {
                        algorithms.value.push({
                            uid: idx.toString(),
                            type: type
                        });
                    }

                    loadBlocks(types, currentComponent.value.blocks);

                    currentCompoundData = {
                        types: types,
                        data_blocks: currentComponent.value.blocks
                    }

                    store.dispatch("algorithms/setAlgorithmResult", null);

                    store.dispatch("algorithms/resetBasicAlgorithmsAttributes");
                    store.dispatch("algorithms/resetCurrentBasicAlgorithms");

                    store.dispatch("graphics/resetCompoundGraphicItems");

                    await store.dispatch("algorithms/setBasicLiveAlgorithm", currentCompoundData);

                    await store.dispatch("algorithms/updateCurrentBasicAlgorithmFromConfig", currentComponent.value.uid);

                    await store.dispatch("algorithms/loadSelectedBasicAlgorithmsAttributes", {
                        types: types
                    });

                    const parametersList = currentComponent.value.algorithms.map(algorithm => algorithm.parameters);

                    store.dispatch("algorithms/loadCurrentBasicAlgorithmFromConfig", parametersList);

                    resetOnLoad();
                    
                    logger.info('Component loaded successfully', { id, types });
                }
                else
                {
                    logger.debug('Resetting component state');
                    store.dispatch("algorithms/resetBasicAlgorithmsAttributes");
                    store.dispatch("algorithms/resetCurrentBasicAlgorithms");
                    store.dispatch("algorithms/setAlgorithmResult", null);
                    store.dispatch("components/setCurrentComponent", null);
                    store.dispatch("graphics/resetCompoundGraphicItems");

                    showCamera.value = false;
                }
            } catch(err) {
                logger.error('Failed to load component', err);
                addErrorToStore(store, 'Component Load Error', err);
                setTypedNotification(
                    ComponentMessages.LOAD_FAILED,
                    NotificationType.ERROR,
                    3000
                );
            }
            
        };

        function onAlgorithmChanged(id){
            algorithmId.value = id;
            
            if(algorithmId.value === "0")
            {
                showInputs.value = false;
            }
            else
            {
                showInputs.value = true;
            }

            if(compoundResult.value.length > id)
            {
                let inputs = compoundResult.value[id].inputs;
                let outputs = compoundResult.value[id].outputs;

                inputImages.value = [];
                outputImages.value = [];

                for(const output of outputs)
                {
                    outputImages.value.push(ImageDataUtils.createJpegDataURI(output));
                }

                for(const input of inputs)
                {
                    inputImages.value.push(ImageDataUtils.createJpegDataURI(input));
                }
            }
        }

        function changeCameraStatus() {
            showCamera.value = !showCamera.value;
        }

        async function singleRunComponent(imageSourceUid) {
            const compoundGraphicItems = store.getters["graphics/getCurrentCompoundGraphics"];
            const canvas = store.getters["graphics/getCanvas"];

            for(const [idx, graphics] of compoundGraphicItems.entries())
            {
                if(graphics.length !== 0)
                {
                    const data = graphic.getGraphicsProps(graphics, canvas);

                    store.dispatch("algorithms/updateCurrentBasicAlgorithmProperty", {
                        idx: idx,
                        name: 'graphics',
                        value: data
                    });
                }
            }

            store.dispatch("algorithms/singleProcessAlgorithmCamera", {
                uid: imageSourceUid,
                type: moduleName
            });
        }

        async function liveProcessAlgorithm(state) {
            if(state)
            {
                const compoundGraphicItems = store.getters["graphics/getCurrentCompoundGraphics"];
                const canvas = store.getters["graphics/getCanvas"];

                for(const [idx, graphics] of compoundGraphicItems.entries())
                {
                    if(graphics.length !== 0)
                    {
                        const data = graphic.getGraphicsProps(graphics, canvas);

                        store.dispatch("algorithms/updateCurrentBasicAlgorithmProperty", {
                            idx: idx,
                            name: 'graphics',
                            value: data
                        });
                    }
                }

                let id = uuidv4();
                let url = `ws://${ipAddress}:${port}/algorithm/basic/live_algorithm_result/${currentImageSourceId.value}/${id}/ws`;

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

            store.dispatch("algorithms/setAlgorithmResult", {
                frame: recvData.frame ? ImageDataUtils.createJpegDataURI(recvData.frame) : '',
                results: recvData.results,
                data: recvData.data
            });

            if(graphicsObject)
            {
                liveProcessSocketInstance.send(JSON.stringify({
                    command: 'set',
                    idx: currentGraphicsId,
                    key: 'graphics',
                    value: graphicsObject
                }));
                graphicsObject = null;
                currentGraphicsId = -1;
            }
            else
            {
                liveProcessSocketInstance.send(JSON.stringify({command: ''}));
            }
        }

        function updateGraphics() {
            let currentId  = parseInt(algorithmId.value);
            const graphicItems = store.getters["graphics/getCurrentCompoundGraphicsAtIdx"](currentId);
            const canvas = store.getters["graphics/getCanvas"];

            graphicsObject = graphic.getGraphicsProps(graphicItems, canvas);
            currentGraphicsId = currentId;
        }

        function updateImageSource(imageSourceId) {
            if(imageSourceId)
            {
                currentImageSourceId.value = imageSourceId;
                feedLocation.value = `ws://${ipAddress}:${port}/image_source/${imageSourceId}/ws`;
            }
        }

        function saveComponent(payload) {
            const algorithms = [];
            let blocks = [];

            if(currentCompoundData)
            {
                const compoundGraphicItems = store.getters["graphics/getCurrentCompoundGraphics"];
                const canvas = store.getters["graphics/getCanvas"];

                for(const [idx, graphics] of compoundGraphicItems.entries())
                {
                    if(graphics.length !== 0)
                    {
                        const data = graphic.getGraphicsProps(graphics, canvas);

                        store.dispatch("algorithms/updateCurrentBasicAlgorithmPropertyLocal", {
                            idx: idx,
                            name: 'graphics',
                            value: data
                        });
                    }
                }
                for(const [idx, type] of currentCompoundData.types.entries())
                {
                    const parameters = store.getters["algorithms/getCurrentBasicAlgorithmAtIndex"](idx);
                    algorithms.push({
                        algorithmType: type,
                        parameters: parameters
                    });
                }

                blocks = currentCompoundData.data_blocks;
            }

            const component = {
                uid: currentComponent.value.uid,
                name: payload.name,
                imageSourceUid: payload.imageSourceUid,
                algorithms: algorithms,
                blocks: blocks
            };

            update(component).then(() => {
                store.dispatch("log/addEvent", {
                    type: moduleName.toUpperCase(),
                    user: currentUser.value ? currentUser.value.username : "Unknown",
                    title: moduleName.toUpperCase() + ' Modified',
                    description: `${currentComponent.value.name} was modified.`
                });

                setTypedNotification(
                    ConfigurationMessages.SAVED,
                    NotificationType.SUCCESS,
                    3000
                );
            }).catch(err => {
                logger.error('Failed to save configuration', err);
                setTypedNotification(
                    ComponentMessages.UPDATE_FAILED,
                    NotificationType.ERROR,
                    3000
                );
            });
        }

        function downloadAlgorithm(){
            let dataToSave = {
                algorithms: null,
                blocks: null
            };

            if(currentComponent)
            {
                dataToSave.algorithms = currentComponent.value.algorithms;
                dataToSave.blocks = currentComponent.value.blocks;
            }
            
            let text = JSON.stringify(dataToSave);

            const currentDate = new Date();

            let suffix = currentDate.getDate() + "_" + (currentDate.getMonth() + 1) + "_"
                            + currentDate.getFullYear() + "_" + currentDate.getHours() + "_"
                            + currentDate.getMinutes() + "_" + currentDate.getSeconds() + ".json"

            let filename = "compound_algorithm_" + suffix;

            let element = document.createElement('a');
            element.setAttribute('href', 'data:application/json;charset=utf-8,' + encodeURIComponent(text));
            element.setAttribute('download', filename);

            element.style.display = 'none';
            document.body.appendChild(element);

            element.click();
            document.body.removeChild(element);
        }

        function onImportPathChanged(path){
            let fileread = new FileReader();
            fileread.onload = async function(e) {
                let content = e.target.result;
                const compoundAlgorithm = JSON.parse(content);

                const types = compoundAlgorithm.algorithms.map(algorithm => algorithm.algorithmType);

                algorithms.value = [];

                for(const [idx, type] of types.entries())
                {
                    algorithms.value.push({
                        uid: idx.toString(),
                        type: type
                    });
                }

                loadBlocks(types, compoundAlgorithm.blocks);

                currentCompoundData = {
                    types: types,
                    data_blocks: compoundAlgorithm.blocks
                };

                const parametersList = compoundAlgorithm.algorithms.map(algorithm => algorithm.parameters);

                store.dispatch("algorithms/setAlgorithmResult", null);

                store.dispatch("algorithms/resetBasicAlgorithmsAttributes");
                store.dispatch("algorithms/resetCurrentBasicAlgorithms");

                store.dispatch("graphics/resetCompoundGraphicItems");

                await store.dispatch("algorithms/setBasicLiveAlgorithm", currentCompoundData);

                await store.dispatch("algorithms/updateCurrentBasicAlgorithmFromDict", parametersList);

                await store.dispatch("algorithms/loadSelectedBasicAlgorithmsAttributes", {
                    types: types
                });

                store.dispatch("algorithms/loadCurrentBasicAlgorithmFromConfig", parametersList);

                resetOnLoad();
            };

            fileread.readAsText(path);
        }

        function resetOnLoad() {
            showCamera.value = false;
            inputImages.value = [];
            outputImages.value = [];
            algorithmId.value = '';
        }

        onMounted(() => {
            logger.lifecycle('mounted', 'CustomComponentsConfiguration component mounted');
            initCanvas();

            playgroundCanvas.value.on('drop', handleDrop);
            playgroundCanvas.value.on('mouse:down', handleMouseDown);

            playgroundCanvas.value.on("mouse:wheel", (opt) => {
                let delta = opt.e.deltaY;
                let zoom = playgroundCanvas.value.getZoom();
                zoom *= 0.999 ** delta;
                if (zoom > 20) zoom = 20;
                if (zoom < 0.01) zoom = 0.01;
                playgroundCanvas.value.zoomToPoint({
                    x: opt.e.offsetX,
                    y: opt.e.offsetY
                },
                zoom
                );
                opt.e.preventDefault();
                opt.e.stopPropagation();
            });

            playgroundCanvas.value.on('object:moving', function(e) {
                unsavedChanges.value = '*';

                let p = e.target;
                
                if(p)
                {
                    const objects = p.getObjects();
                    objects.forEach(function(item, i){
                        if(item.type === 'circle')
                        {
                            const center = p.getCenterPoint();

                            const realX = center.x + item.left;
                            const realY = center.y + item.top;
                            if(item.offset > 0)
                            {
                                item.line1 && item.line1.set({
                                    'x1': realX + (circleRadius / 2) + item.offset,
                                    'y1': realY + (circleRadius),
                                    'x2': realX + (circleRadius / 2),
                                    'y2': realY + (circleRadius)
                                });
                                item.line2 && item.line2.set({
                                    'x1': realX + (circleRadius / 2) + item.offset,
                                    'y1': item.line2.get('y1'),
                                    'x2': realX + (circleRadius / 2) + item.offset,
                                    'y2': realY + (circleRadius)
                                });
                                item.line3 && item.line3.set({
                                    'x2': realX + (circleRadius / 2) + item.offset,
                                    'y2': item.line3.get('y2')
                                });
                            }
                            else
                            {
                                item.line1 && item.line1.set({
                                    'x1': realX + (circleRadius / 2),
                                    'y1': realY + (circleRadius),
                                    'x2': realX + (circleRadius / 2) + item.offset,
                                    'y2': realY + (circleRadius)
                                });
                                item.line2 && item.line2.set({
                                    'x1': realX + (circleRadius / 2) + item.offset,
                                    'y1': realY + (circleRadius),
                                    'x2': realX + (circleRadius / 2) + item.offset,
                                    'y2': p.top - 20
                                });
                                item.line3 && item.line3.set({
                                    'x1': realX + (circleRadius / 2) + item.offset,
                                    'y1': p.top - 20,
                                    'x2': item.line4.get('x1'),
                                    'y2': p.top - 20
                                });
                                item.line4 && item.line4.set({
                                    'y1': p.top - 20,
                                    'y2': item.line5.get('y2')
                                });
                            }

                            throttledRender();
                        }
                    })
                }
            });

            if(currentConfiguration.value)
            {
                store.dispatch("components/loadComponents", {
                    type: moduleName
                });
            }
        });

        onBeforeUnmount(() => {
            logger.lifecycle('beforeUnmount', 'CustomComponentsConfiguration component before unmount');
            unwatch();
            store.dispatch("algorithms/resetBasicAlgorithmsAttributes");
            store.dispatch("algorithms/resetCurrentBasicAlgorithms");
            store.dispatch("algorithms/setAlgorithmResult", null);
            store.dispatch("components/setComponents", []);
            store.dispatch("components/setCurrentComponent", null);
            store.dispatch("graphics/resetCompoundGraphicItems");
            logger.lifecycle('cleanup', 'CustomComponentsConfiguration cleanup completed');
        });

        return {
            moduleName,
            playgroundContainer,
            algTypesContainer,
            types,
            unsavedChanges,
            playgroundMode,
            modeIconName,
            currentComponent,
            algorithms,
            components,
            algorithmAttributes,
            parameters,
            currentGraphics,
            algorithmId,
            showCamera,
            showInputs,
            showResults,
            isLoading,
            feedLocation,
            resultImage,
            outputImages,
            inputImages,
            compoundResult,
            currentConfiguration,
            showNotification,
            notificationIcon,
            notificationMessage,
            notificationTimeout,
            notificationType,
            updateGraphics,
            switchMode,
            onDragStart,
            setConnectMode,
            deleteCurrentActive,
            saveConfiguration,
            addComponent,
            remove,
            loadComponent,
            onAlgorithmChanged,
            changeCameraStatus,
            singleRunComponent,
            liveProcessAlgorithm,
            updateImageSource,
            saveComponent,
            downloadAlgorithm,
            onImportPathChanged,
            clearNotification
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
    height: 100%;
    color: white;
    margin: 0;
}

.components-control-container{
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

.playground-container{
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 100%;
    color: white;
    margin: 0;
}

#playground-canvas-container {
    width: 65vw;
    height: 90vh;
    background-color: black;
    margin-right: 1vw;
}

#alg-types-container {
    width: 25vw;
    height: 90vh;
    background-color: black;
    margin-right: 1vh;
}

.alg-types {
    width: 20vw;
    min-height: 90vh;
    background-color: rgb(188, 155, 155);
    margin-right: 1vh;
    display: flex;
    flex-direction: column;
    flex-wrap: nowrap;
    /* overflow-y: auto; - moved scrolling to body level */
}

.alg-box{
    height: 10vh;
    width: 90%;
    background-color: #CC527A;
    margin: 1vh auto;
    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: center;
    border-radius: 10px;
    box-shadow: 0 2px 12px #6a4d57;
    font-size: large;
    font-weight: bold;
}

.control-panel {
    width: 6vw;
    height: 90vh;
    background-color: inherit;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: center;
}

.action {
    margin-bottom: 0.5vh;
}

.button-content-wrapper{
    display: flex;
    justify-content: center;
    align-items: center;
}

.view-actions{
    position: fixed;
    top: 85vh;
    left: 95%;
    z-index: 5;
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

.results-btn-container {
    position: absolute;
    top: 87%;
    left: 81%;
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

</style>