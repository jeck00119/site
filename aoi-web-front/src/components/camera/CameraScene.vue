<template>
    <div id="canvas-container" :style="{width: width, height: height}" ref="canvasContainer">
        <canvas :id="canvasId" :style="{width: '100%', height: '100%'}" ref="canvasElement"></canvas>
    </div>
</template>

<script>
import * as fabric from 'fabric';
import { ref, watch, onMounted, toRef, onUnmounted, onBeforeUnmount } from 'vue';

import { useStore } from 'vuex';

export default {
    props: ['width', 'height', 'show', 'feedLocation', 'cameraFeed', 'staticImages', 'id', 'canvasId', 'graphics', 'imageFileName', 'overlay'],

    emits: ['graphics-changed', 'graphic-selected', 'graphic-cleared', 'graphic-modified'],

    setup(props, context) {
        let socket = null;
        let canvas = null;
        const imageSource = ref(null);
        const canvasContainer = ref(null);
        const canvasElement = ref(null);

        const graphics = toRef(props, 'graphics');
        const feedLocation = toRef(props, 'feedLocation');
        const show = toRef(props, 'show');
        const staticImages = toRef(props, 'staticImages');
        const overlay = toRef(props, 'overlay');
        const imageFileName = toRef(props, 'imageFileName');

        let staticImagesOffset = 0;
        const staticImagesMargin = 20;

        let ws_uid = null;

        const store = useStore();

        function connectToCamera() {
            ws_uid = crypto.randomUUID();
            socket = new WebSocket(props.feedLocation + `/${ws_uid}`);

            socket.addEventListener('open', onSocketOpen);
            socket.addEventListener('message', imageReceived);
        };

        function disconnectFromCamera() {
            if(socket){
                // socket.send('disct');

                store.dispatch("imageSources/closeImageSourceSocket", {
                    uid: ws_uid
                });

                socket.removeEventListener('open', onSocketOpen);
                socket.removeEventListener('message', imageReceived);

                socket.close();

                socket = null;
                ws_uid = null;
            }
        };

        function onSocketOpen() {
            if(socket && socket.connected)
                socket.send('eses');
        }

        function imageReceived(event) {
            let reader = new FileReader();
            reader.readAsBinaryString(event.data);
            reader.onloadend = function () {
                let base64data = reader.result;
                imageSource.value = 'data:image/png;base64,' + base64data;
                // if(socket)
                //     socket.send('eses');
            };
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
            for(const graphicData of graphics)
            {
                const graphic = createFabricObject(graphicData);
                if (graphic) {
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

                    canvas.add(graphic);
                    canvas.setActiveObject(graphic);

                    canvas.bringObjectToFront(graphic);
                    canvas.renderAll();
                }
            }
        }

        function removeRectangles() {
            if (!canvas) return;
            
            const objects = canvas.getObjects();

            objects.forEach(function(item, _) {
                if(item.type === 'rect')
                {
                    canvas.remove(item);
                }
            });
        }

        function removeCircles() {
            if (!canvas) return;
            
            const objects = canvas.getObjects();

            objects.forEach(function(item, _) {
                if(item.type === 'circle')
                {
                    canvas.remove(item);
                }
            });
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
            }
        });

        watch(feedLocation, (newValue) => {
            if(newValue)
            {
                disconnectFromCamera();
                connectToCamera();
            }
            else
            {
                disconnectFromCamera();
            }
        });

        watch(show, (newValue) => {
            if(!newValue)
            {
                socket.removeEventListener('message', imageReceived);
                removeImages();
            }

            if(newValue && props.cameraFeed)
            {
                removeImages();
                socket.addEventListener('message', imageReceived);
            }
        });

        watch(staticImages, (newValue) => {
            if(!show.value)
            {
                staticImagesOffset = 0;
                removeImages();
                for(const img of newValue)
                {
                    addStaticImage(img);
                }
            }
        });

        watch(overlay, (newValue) => {
            if(newValue)
            {
                removeImages();
                // Fabric.js v6: Use direct property assignment instead of setOverlayImage
                canvas.overlayImage = newValue;
                canvas.renderAll();
            }
        });

        watch(imageFileName, (newValue) => {
            if(newValue && canvas.backgroundImage)
            {
                let link = document.createElement('a');
                link.href = canvas.backgroundImage.getSrc().replace(/^data:image\/[^;]/, 'data:application/octet-stream');
                link.download = newValue.split('.')[0] + '.jpeg';
                link.click();
            }
        });

        watch(imageSource, (newValue) => {
            if(show.value && canvas)
            {
                // Fabric.js v6: Use async/await with FabricImage.fromURL
                fabric.FabricImage.fromURL(newValue).then(img => {
                    canvas.backgroundImage = img;
                    canvas.renderAll();
                }).catch(err => {
                    console.error('Error loading background image:', err);
                });
            }
        });

        function addStaticImage(url) {
            // Fabric.js v6: Use async/await with FabricImage.fromURL
            fabric.FabricImage.fromURL(url).then(img => {
                img.set({top: 0, left: staticImagesOffset, selectable: false});
                staticImagesOffset += img.width + staticImagesMargin;
                canvas.add(img);
                canvas.sendObjectToBack(img);
            }).catch(err => {
                console.error('Error loading static image:', err);
            });
        }

        function removeImages() {
            if (!canvas) return;
            
            const objects = canvas.getObjects();

            objects.forEach(function(object, _) {
                if(object.type === 'image')
                {
                    canvas.remove(object);
                }
            });

            // Fabric.js v6: Use direct property assignment instead of setBackgroundImage
            canvas.backgroundImage = null;
            canvas.renderAll();
        }

        function selectionChanged(obj)
        {
            context.emit('graphic-selected', obj.selected[0]);
        }

        function selectionCleared() {
            context.emit('graphic-cleared');
        }

        onMounted(() => {
            canvas = new fabric.Canvas(props.canvasId);

            canvas.setHeight(canvasContainer.value.clientHeight);
            canvas.setWidth(canvasContainer.value.clientWidth);

            const resizeObserver = new ResizeObserver(() => {
                if(canvasContainer.value)
                {
                    canvas.setHeight(canvasContainer.value.clientHeight);
                    canvas.setWidth(canvasContainer.value.clientWidth);
                }
            });

            resizeObserver.observe(canvasContainer.value);

            if(!props.cameraFeed)
            {
                staticImagesOffset = 0;
                removeImages();
                for(const img of props.staticImages)
                {
                    addStaticImage(img);
                }
            }

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

            canvas.on('mouse:up', function() {
                this.setViewportTransform(this.viewportTransform);
                this.isDragging = false;
                this.selection = true;
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

            canvas.on({
                'selection:updated': selectionChanged,
                'selection:created': selectionChanged
            });

            canvas.on({
                'selection:cleared': selectionCleared
            });

            if(props.cameraFeed)
                store.dispatch("graphics/setCanvas", canvas);

            addRectangles(props.graphics);

            if(overlay.value)
            {
                // Fabric.js v6: Use direct property assignment instead of setOverlayImage
                canvas.overlayImage = overlay.value;
                canvas.renderAll();
            }
        });

        onBeforeUnmount(() => {
            removeImages();
            removeRectangles();
            removeCircles();
        });

        onUnmounted(() => {
            try {
                disconnectFromCamera();
            } catch (error) {
                console.warn('Error during CameraScene component unmounting:', error);
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