<template>
    <div class="mask-header">
        <div class="close">
            <button @click="close()">&#10006;</button>
        </div>
        <div class="title">
            ROI Mask ({{ isEditMode ? 'Edit Mode' : 'Normal Mode' }})
        </div>
    </div>
    <div class="mask-body">
        <div class="mask-scene-wrapper">
            <div id="canvas-container" :style="{width: width, height: height}" ref="canvasContainer">
                <canvas :id="canvasId" :style="{width: width, height: height}"></canvas>
            </div>
        </div>
        <div class="mask-control">
            <base-color-picker width="100%" :current="color" @update-value="updateColor"></base-color-picker>
            <base-button-rectangle width="80%" @state-changed="toggleEditMode">
                <div class="button-container">
                    <div class="button-icon">
                        <v-icon name="md-modeeditoutline-sharp" scale="1.5"/>
                    </div>
                </div>
            </base-button-rectangle>
            <base-button-rectangle width="80%" @state-changed="removePoints">
                <div class="button-container">
                    <div class="button-icon">
                        <v-icon name="fc-cancel" scale="1.5"/>
                    </div>
                </div>
            </base-button-rectangle>
            <base-button-rectangle width="80%" @state-changed="deleteSelected">
                <div class="button-container">
                    <div class="button-icon">
                        <v-icon name="md-delete-round" scale="1.5"/>
                    </div>
                </div>
            </base-button-rectangle>
            <base-button-rectangle width="80%" @state-changed="save">
                <div class="button-container">
                    <div class="button-icon">
                        <v-icon name="ri-save-3-fill" scale="1.5"/>
                    </div>
                </div>
            </base-button-rectangle>
        </div>
    </div>
</template>

<script>
import * as fabric from 'fabric';
import { ref, onMounted, onBeforeUnmount, toRef, watch } from 'vue';

import { ipAddress, port } from '../../url';
import { uuid } from 'vue3-uuid';
import { useWebSocket, useFabricCanvas } from '@/composables/useStore';
import { DEFAULT_IMAGE_DATA_URI_PREFIX, ImageDataUtils } from '../../utils/imageConstants';

export default {
    props: ['graphics', 'imageSourceId', 'width', 'height', 'canvasId'],

    emits: ['closed', 'save'],

    setup(props, context) {
        const canvasContainer = ref(null);
        
        // Initialize Fabric.js canvas using composable
        const {
            canvas,
            initCanvas,
            clearCanvas,
            throttledRender,
            batchRender,
            addObjects,
            removeObjects
        } = useFabricCanvas(props.canvasId, {
            containerRef: canvasContainer
        });

        let polyPoints = [];
        let canvasPoints = [];

        const isEditMode = ref(false);

        const color = ref("#000000");

        const graphicsRect = toRef(props, 'graphics');
        const imageSourceId = toRef(props, 'imageSourceId');

        // Initialize WebSocket connection
        const wsUid = uuid.v4();
        const wsUrl = `ws://${ipAddress}:${port}/mask/${wsUid}/crop_roi/ws`;
        const { socket, isConnected, connect, disconnect, send } = useWebSocket(wsUrl, {
            autoConnect: false,
            onOpen: onSocketOpen,
            onMessage: roiReceived
        });

        watch(graphicsRect, (current) => {
            if(current)
            {
                if(isConnected.value)
                {
                    let loadFromImageSource = false;
                    if(imageSourceId.value)
                    {
                        loadFromImageSource = true;
                    }

                    send(JSON.stringify({
                        command: 'set',
                        image_source_uid: imageSourceId.value,
                        load_from_image_source: loadFromImageSource,
                        graphics: current
                    }));
                }

                removePoints();
                removePolygons();
                loadMasks(current.masks, current.masksColors);
            }
            else
            {
                removePoints();
                removePolygons();
                // Fabric.js v6: Use direct property assignment instead of setBackgroundImage
                canvas.value.backgroundImage = null;
                throttledRender();
            }
        });

        watch(imageSourceId, (current) => {
            if(isConnected.value)
            {
                send(JSON.stringify({
                    command: 'set',
                    image_source_uid: current,
                    graphics: graphicsRect.value
                }));
            }
        });

        watch(isEditMode, (current) => {
            if(!current)
            {
                removePoints();
            }
        });

        function updateColor(_, value) {
            color.value = value;
        }

        function loadMasks(masks, masksColors) {
            for(let i = 0; i < masks.length; i++)
            {
                const polyPoints = [];

                for(const points of masks[i])
                {
                    polyPoints.push({
                        x: points[0],
                        y: points[1]
                    });
                }

                const redHex = masksColors[i][0].toString(16).padStart(2, '0');
                const greenHex = masksColors[i][1].toString(16).padStart(2, '0');
                const blueHex = masksColors[i][2].toString(16).padStart(2, '0');

                const hexString = '#' + redHex + greenHex + blueHex;

                let polygon = new fabric.Polygon(polyPoints, {
                    fill: hexString
                });

                addObjects(polygon);
            }
        }

        function connectToCropROISocket()
        {
            connect();
        }

        function disconnectFromCropROISocket()
        {
            if(isConnected.value)
            {
                send(JSON.stringify({command: "disconnect"}));
            }
            
            disconnect();
            removePoints();
            removePolygons();
        }

        function onSocketOpen() {
            if(isConnected.value)
            {
                send(JSON.stringify({
                    command: 'set',
                    image_source_uid: imageSourceId.value,
                    graphics: graphicsRect.value
                }));
            }
        }

        function roiReceived(event) {
            let recvData = JSON.parse(event.data);
            // Fabric.js v6: Use direct property assignment instead of setBackgroundImage
            canvas.value.backgroundImage = ImageDataUtils.createJpegDataURI(recvData.roi);
            throttledRender();
        }

        function addPolyPoint(mouseEvent) {
            let pointer = canvas.value.getPointer(mouseEvent);

            polyPoints.push({
                x: pointer.x,
                y: pointer.y
            });

            let c = new fabric.Circle({
                left: pointer.x - 2,
                top: pointer.y - 2,
                strokeWidth: 2,
                radius: 2,
                fill: color.value,
                stroke: '#666'
            });

            canvasPoints.push(c);
            addObjects(c);
        }

        function removePointsFromCanvas() {
            if(canvasPoints.length > 0) {
                removeObjects(canvasPoints);
            }

            canvasPoints = [];
        }

        function removePoints() {
            removePointsFromCanvas();
            polyPoints = [];
        }

        function removePolygons() {
            const objects = canvas.value.getObjects();
            const polygonsToRemove = objects.filter(object => object.type === 'polygon');
            
            if(polygonsToRemove.length > 0) {
                removeObjects(polygonsToRemove);
            }
        }

        function deleteSelected() {
            const activeObject = canvas.value.getActiveObject();
            if(activeObject) {
                removeObjects(activeObject);
            }
        }

        function toggleEditMode() {
            isEditMode.value = !isEditMode.value;
        }

        function save() {
            const polygons = [];
            const objects = canvas.value.getObjects();

            objects.forEach(function(object){
                if(object.type === 'polygon')
                {
                    polygons.push(object);
                }
            });

            context.emit('save', polygons);
        }

        function close() {
            context.emit('closed');
        }

        onMounted(() => {
            initCanvas();

            canvas.value.on('mouse:down', function(opt) {
                let evt = opt.e;
                if (evt.altKey === true) {
                    this.isDragging = true;
                    this.selection = false;
                    this.lastPosX = evt.clientX;
                    this.lastPosY = evt.clientY;
                }
            });

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

            canvas.value.on('mouse:up', function(options) {
                this.setViewportTransform(this.viewportTransform);
                this.isDragging = false;
                this.selection = true;

                if(isEditMode.value)
                {
                    addPolyPoint(options.e)
                }
            });

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

            canvas.value.on('mouse:dblclick', function() {
                if(isEditMode.value)
                {
                    removePointsFromCanvas();

                    // last two elements have the same value since mouse:up is fired twice during dblclick event
                    polyPoints.pop();

                    let polygon = new fabric.Polygon(polyPoints, {
                        fill: color.value
                    });

                    addObjects(polygon);

                    polyPoints = [];
                }
            });

            connectToCropROISocket();

            if(graphicsRect.value)
            {
                loadMasks(graphicsRect.value.masks, graphicsRect.value.masksColors);
            }
        });

        onBeforeUnmount(() => {
            disconnectFromCropROISocket();
        });

        return {
            canvasContainer,
            isEditMode,
            color,
            updateColor,
            toggleEditMode,
            removePoints,
            deleteSelected,
            save,
            close
        }
    }
}
</script>

<style scoped>
#canvas-container {
    background-color: rgb(0, 0, 0);
}

.mask-header .close {
    position: absolute;
    top: 0;
    right: 0;
}

.mask-header {
    width: 100%;
    height: 15%;
}

.title {
    display: flex;
    justify-content: flex-start;
    align-items: center;
    width: 100%;
    height: 100%;
    font-weight: bold;
    padding-left: 5px;
}

.mask-body {
    display: flex;
    height: 85%;
    width: 100%;
}

.mask-scene-wrapper {
    width: 85%;
    height: 100%;
    /* background-color: violet; */
}

.mask-control {
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    align-items: center;
    /* background-color: red; */
    width: 15%;
    height: 100%;
}

.close > button {
    background-color: black;
}

.button-container {
    display: flex;
    width: 100%;
    height: 4vh;
    padding: 4px;
    justify-content: center;
    align-items: center;
}

.button-icon {
    height: 100%;
    display: flex;
    align-items: center;
}
</style>