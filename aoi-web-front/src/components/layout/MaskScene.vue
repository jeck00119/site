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

export default {
    props: ['graphics', 'imageSourceId', 'width', 'height', 'canvasId'],

    emits: ['closed', 'save'],

    setup(props, context) {
        let socket = null;
        let canvas = null;
        const canvasContainer = ref(null);

        let polyPoints = [];
        let canvasPoints = [];

        const isEditMode = ref(false);

        const color = ref("#000000");

        const graphicsRect = toRef(props, 'graphics');
        const imageSourceId = toRef(props, 'imageSourceId');

        watch(graphicsRect, (current) => {
            if(current)
            {
                if(socket)
                {
                    let loadFromImageSource = false;
                    if(imageSourceId.value)
                    {
                        loadFromImageSource = true;
                    }

                    socket.send(JSON.stringify({
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
                canvas.backgroundImage = null;
                canvas.renderAll();
            }
        });

        watch(imageSourceId, (current) => {
            if(socket)
            {
                socket.send(JSON.stringify({
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

                canvas.add(polygon);
            }
        }

        function connectToCropROISocket()
        {
            let ws_uid = uuid.v4();
            let url = `ws://${ipAddress}:${port}/mask/${ws_uid}/crop_roi/ws`;
            socket = new WebSocket(url);

            socket.addEventListener('open', onSocketOpen);
            socket.addEventListener('message', roiReceived);
        }

        function disconnectFromCropROISocket()
        {
            if(socket)
            {
                socket.send(JSON.stringify({command: "disconnect"}));

                socket.removeEventListener('open', onSocketOpen);
                socket.removeEventListener('message', roiReceived);

                socket.close();
                socket = null;
            }

            removePoints();
            removePolygons();
        }

        function onSocketOpen() {
            if(socket)
            {
                socket.send(JSON.stringify({
                    command: 'set',
                    image_source_uid: imageSourceId.value,
                    graphics: graphicsRect.value
                }));
            }
        }

        function roiReceived(event) {
            let recvData = JSON.parse(event.data);
            // Fabric.js v6: Use direct property assignment instead of setBackgroundImage
            canvas.backgroundImage = 'data:image/png;base64,' + recvData.roi;
            canvas.renderAll();
        }

        function addPolyPoint(mouseEvent) {
            let pointer = canvas.getPointer(mouseEvent);

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
            canvas.add(c);
        }

        function removePointsFromCanvas() {
            for(let point of canvasPoints)
            {
                canvas.remove(point);
            }

            canvasPoints = [];
        }

        function removePoints() {
            removePointsFromCanvas();
            polyPoints = [];
        }

        function removePolygons() {
            const objects = canvas.getObjects();

            objects.forEach(function(object){
                if(object.type === 'polygon')
                {
                    canvas.remove(object);
                }
            });
        }

        function deleteSelected() {
            const activeObject = canvas.getActiveObject();
            canvas.remove(activeObject);
        }

        function toggleEditMode() {
            isEditMode.value = !isEditMode.value;
        }

        function save() {
            const polygons = [];
            const objects = canvas.getObjects();

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
            canvas = new fabric.Canvas(props.canvasId);

            canvas.setHeight(canvasContainer.value.clientHeight);
            canvas.setWidth(canvasContainer.value.clientWidth);

            canvas.on('mouse:down', function(opt) {
                let evt = opt.e;
                if (evt.altKey === true) {
                    this.isDragging = true;
                    this.selection = false;
                    this.lastPosX = evt.clientX;
                    this.lastPosY = evt.clientY;
                }
            });

            canvas.on('mouse:move', function(opt) {
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

            canvas.on('mouse:up', function(options) {
                this.setViewportTransform(this.viewportTransform);
                this.isDragging = false;
                this.selection = true;

                if(isEditMode.value)
                {
                    addPolyPoint(options.e)
                }
            });

            canvas.on("mouse:wheel", (opt) => {
                let delta = opt.e.deltaY;
                let zoom = canvas.getZoom();
                zoom *= 0.999 ** delta;
                if (zoom > 20) zoom = 20;
                if (zoom < 0.01) zoom = 0.01;
                canvas.zoomToPoint({
                    x: opt.e.offsetX,
                    y: opt.e.offsetY
                },
                zoom
                );
                opt.e.preventDefault();
                opt.e.stopPropagation();
            });

            canvas.on('mouse:dblclick', function() {
                if(isEditMode.value)
                {
                    removePointsFromCanvas();

                    // last two elements have the same value since mouse:up is fired twice during dblclick event
                    polyPoints.pop();

                    let polygon = new fabric.Polygon(polyPoints, {
                        fill: color.value
                    });

                    canvas.add(polygon);

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