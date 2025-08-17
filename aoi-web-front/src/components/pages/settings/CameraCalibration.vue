<template>
    <div class="flex-container">
        <div class="calibration-settings-panel">
            <div class="image-source-selector">
                <label id="image-source-label" for="image-source">Image Source</label>
                <vue-multiselect
                    v-model="currentImageSource"
                    :options="imageSources ? imageSourcesNames : []"
                    placeholder="Select Image Source"
                    :searchable="true"
                ></vue-multiselect>
            </div>
            <div class="checkerboard-settings">
                <div class="title">Checkerboard</div>
                <div class="rows-container">
                    <label for="checkerboard-rows">Rows</label>
                    <input type="number" id="checkerboard-rows" name="checkerboard-rows" min="1" max="100" v-model="checkerboardRows">
                </div>
                <div class="cols-container">
                    <label for="checkerboard-cols">Columns</label>
                    <input type="number" id="checkerboard-cols" name="checkerboard-cols" min="1" max="100" v-model="checkerboardCols">
                </div>
                <div class="square-size-container">
                    <label for="checkerboard-square-size">Square Size</label>
                    <input type="number" id="checkerboard-square-size" name="checkerboard-square-size" min="1" max="100" v-model="checkerboardSquareSize">
                </div>
            </div>
            <div class="other-settings">
                <div class="title">Other</div>
                <div class="calibration-frames-container">
                    <label for="calibration-frames">Calibration Frames</label>
                    <input type="number" id="calibration-frames" name="calibration-frames" min="1" max="100" v-model="calibrationFrames">
                </div>
                <div class="cooldown-container">
                    <label for="cooldown">Cooldown</label>
                    <input type="number" id="cooldown" name="cooldown" min="1" max="100" v-model="cooldown">
                </div>
            </div>
            <div class="calibration-action-container">
                <button @click="startCalibration" :disabled="currentImageSource === null || calibrationRunning === true">Start Calibration</button>
            </div>
            <div class="calibration-info">
                <div class="frames-wrap">
                    Frames Acquired: {{ framesAcquired }}
                </div>
                <div class="clock-wrap">
                    <div class="clock">
                        <span class="count">{{ timeRemaining ? timeRemaining : 0 }}</span>
                    </div>
                </div>
            </div>
        </div>
        <div class="camera-scene-container">
            <camera-scene width="100%" height="100%" :show="showCamera" :camera-feed="true"
                        :feed-location="feedLocation" :static-images="[]" :id="1" canvas-id="camera-calibration-canvas"
                        :graphics="[]"></camera-scene>
        </div>
        <div v-if="showFrames" @click="tryClose" class="backdrop"></div>
        <div v-if="showFrames" class="frame-view-container">
                <div class="frame-view">
                    <img class="calib-frame-img" :src="currentCalibFrameSrc" style="width:100%">
                    <a class="prev" @click="changeImage(-1)">&#10094;</a>
                    <a class="next" @click="changeImage(1)">&#10095;</a>
                </div>
                <div class="side-panel">
                    <div class="calibration-frames-info">
                        <h2>Calibration Frames</h2>
                        <p>Visually check that the detected points are correct. If the detected points are poor, repeat the calibration process. If your code does not detect the checkerboard pattern points, ensure that your calibration patterns are well lit, and all of the pattern can be seen by the camera. Ensure that the checkerboard rows and checkerboard columns values file is correctly set. These are NOT the number of boxes in your checkerboard pattern. A good calibration should result in less then 0.3 RMSE. You should aim to obtain about .15 to 0.25 RMSE.</p>
                        <div class="rmse">RMSE: {{currentRMSE}}</div>
                    </div>
                    <div class="calibration-actions-container">
                        <button class="discard-btn" @click="tryClose">Discard</button>
                        <button class="apply-btn" @click="saveCalibration">Apply</button>
                    </div>
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
import VueMultiselect from 'vue-multiselect';

import useNotification, { NotificationType } from '../../../hooks/notifications';
import { CameraMessages, GeneralMessages } from '@/constants/notifications';
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import { useCameraCalibrationStore, useImageSourcesStore } from '@/composables/useStore';
import { logger } from '@/utils/logger';
import { v4 as uuidv4 } from "uuid";

import CameraScene from '../../camera/CameraScene.vue';
import { ipAddress, port } from '../../../url';
import { useWebSocket } from '@/composables/useStore';
import { DEFAULT_IMAGE_DATA_URI_PREFIX, ImageDataUtils } from '../../../utils/imageConstants';

export default {
    components :{
        CameraScene,
        VueMultiselect
    },

    setup() {
        const currentImageSource = ref(null);

        const checkerboardRows = ref(4);
        const checkerboardCols = ref(7);
        const checkerboardSquareSize = ref(3.5);

        const calibrationFrames = ref(10);
        const cooldown = ref(5);

        const feedLocation = ref('');
        const showCamera = ref(false);

        const framesAcquired = ref(0);
        const timeRemaining = ref(null);

        const showFrames = ref(false);
        const currentImageIdx = ref(-1);
        const currentCalibFrameSrc = ref('');
        const currentRMSE = ref(null);

        const calibrationRunning = ref(false);

        const cameraCalibrationStore = useCameraCalibrationStore();
        const imageSourcesStore = useImageSourcesStore();

        // WebSocket state
        let wsUid = null;
        let webSocketInstance = null;

        const {showNotification, notificationMessage, notificationIcon, notificationTimeout, notificationType,
            setTypedNotification, clearNotification} = useNotification();

        // These are already computed refs from the composables


        const imageSources = imageSourcesStore.imageSources;

        const imageSourcesNames = computed(() => 
            (imageSourcesStore.imageSources.value || []).map(imageSource => imageSource.name)
        );

        watch(currentImageSource, (newValue) => {
            const imageSource = imageSources.value.find(imageSource => imageSource.name === newValue);

            if(imageSource)
            {
                // Include FPS parameter for proper frame rate control
                const fps = imageSource.fps || 1; // Default to 1 FPS if not specified
                let wsUrl;
                
                if (imageSource.image_source_type === "static") {
                    wsUrl = `ws://${ipAddress}:${port}/image_source/${imageSource.uid}/${imageSource.image_generator_uid}/${fps}/ws`;
                } else if (imageSource.image_source_type === "dynamic") {
                    wsUrl = `ws://${ipAddress}:${port}/image_source/${imageSource.uid}/${imageSource.camera_uid}/${fps}/ws`;
                } else {
                    // Fallback to old format if type is unknown
                    wsUrl = `ws://${ipAddress}:${port}/image_source/${imageSource.uid}/ws`;
                }
                
                feedLocation.value = wsUrl;
                showCamera.value = true;
                logger.debug('CameraCalibration - WebSocket URL with FPS:', wsUrl, 'FPS:', fps);
            }
            else
            {
                showCamera.value = false;
            }
        });

        watch(currentImageIdx, (newValue) => {
            if(newValue >= 0)
            {
                webSocketInstance.send(JSON.stringify({
                    "command": "retrieve",
                    "idx": currentImageIdx.value
                }));
            }
        });

        // Watch for FPS changes in the current image source to trigger WebSocket reconnection
        watch(() => {
            const imageSource = imageSources.value.find(imageSource => imageSource.name === currentImageSource.value);
            return imageSource?.fps;
        }, (newFps, oldFps) => {
            if (newFps !== oldFps && newFps != null && currentImageSource.value) {
                logger.debug('CameraCalibration - FPS changed, updating WebSocket URL', { newFps, oldFps });
                // Trigger the currentImageSource watcher to update the WebSocket URL
                const imageSource = imageSources.value.find(imageSource => imageSource.name === currentImageSource.value);
                if (imageSource) {
                    const fps = newFps;
                    let wsUrl;
                    
                    if (imageSource.image_source_type === "static") {
                        wsUrl = `ws://${ipAddress}:${port}/image_source/${imageSource.uid}/${imageSource.image_generator_uid}/${fps}/ws`;
                    } else if (imageSource.image_source_type === "dynamic") {
                        wsUrl = `ws://${ipAddress}:${port}/image_source/${imageSource.uid}/${imageSource.camera_uid}/${fps}/ws`;
                    } else {
                        wsUrl = `ws://${ipAddress}:${port}/image_source/${imageSource.uid}/ws`;
                    }
                    
                    feedLocation.value = wsUrl;
                    logger.debug('CameraCalibration - Updated WebSocket URL for FPS change:', wsUrl);
                }
            }
        });

        function startCalibration() {
            calibrationRunning.value = true;

            connectToWs();

            cameraCalibrationStore.setCalibrationParameters(
                checkerboardRows.value,
                checkerboardCols.value,
                checkerboardSquareSize.value
            );

            timeRemaining.value = cooldown.value;

            var timer = setInterval(() => {
                if(timeRemaining.value > 0)
                {
                    timeRemaining.value -= 1;
                }
                else
                {
                    webSocketInstance.send(JSON.stringify({
                        command: "capture"
                    }));
                    framesAcquired.value += 1;
                    if(framesAcquired.value < calibrationFrames.value)
                    {
                        timeRemaining.value = cooldown.value;
                    }
                    else
                    {
                        webSocketInstance.send(JSON.stringify({
                            command: "calibrate"
                        }));
                        setTypedNotification(
                            CameraMessages.CALIBRATING,
                            NotificationType.LOADING
                        );
                        clearInterval(timer);
                    }
                }
            }, 1000);
        }

        function connectToWs() 
        {
            wsUid = uuidv4();
            const imageSource = imageSources.value.find(imageSource => imageSource.name === currentImageSource.value);
            const wsUrl = `ws://${ipAddress}:${port}/camera_calibration/${imageSource.uid}/ws/${wsUid}`;
            
            webSocketInstance = useWebSocket(wsUrl, {
                autoConnect: true,
                onMessage: onCalibrationSocketMsgRecv
            });
        }

        async function disconnectFromWs() 
        {
            const imageSource = imageSources.value.find(imageSource => imageSource.name === currentImageSource.value);
            await cameraCalibrationStore.closeCalibrationSocket(imageSource.uid);

            if(webSocketInstance)
            {
                webSocketInstance.disconnect();
                webSocketInstance = null;
            }
        }

        function onCalibrationSocketMsgRecv(event)
        {
            const data = JSON.parse(event.data);

            if(data.details === "calibDone")
            {
                clearNotification();
                showFrames.value = true;

                currentImageIdx.value = 0;
                currentRMSE.value = data.data;

                calibrationRunning.value = false;
            }
            else if(data.details === "calibFrame")
            {
                currentCalibFrameSrc.value = ImageDataUtils.createJpegDataURI(data.data);
            }
            else if(data.details === "calibError")
            {
                clearNotification();
                setTypedNotification(
                    CameraMessages.CALIBRATION_FAILED,
                    NotificationType.ERROR,
                    3000
                );
                showFrames.value = true;
                currentImageIdx.value = 0;

                calibrationRunning.value = false;
            }
        }

        function tryClose() 
        {
            showFrames.value = false;
        }

        function changeImage(step)
        {
            if(step > 0 && currentImageIdx.value < calibrationFrames.value - 1)
            {
                currentImageIdx.value += step;
            }
            else if(step < 0 && currentImageIdx.value > 0)
            {
                currentImageIdx.value += step;
            }
        }

        function saveCalibration()
        {
            webSocketInstance.send(JSON.stringify({
                "command": "save",
                "uid": uuidv4()
            }));
            webSocketInstance.send(JSON.stringify({
                "command": "stop",
            }));
            showFrames.value = false;

            if(webSocketInstance)
            {
                webSocketInstance.disconnect();
                webSocketInstance = null;
            }
        }

        onMounted(() => {
            
        });

        onUnmounted(() => {
            if(webSocketInstance)
                disconnectFromWs();
        });

        return {
            currentImageSource,
            imageSources,
            imageSourcesNames,
            type: 'camera-calibration',
            checkerboardRows,
            checkerboardCols,
            checkerboardSquareSize,
            calibrationFrames,
            cooldown,
            showCamera,
            feedLocation,
            framesAcquired,
            timeRemaining,
            showNotification,
            notificationMessage,
            notificationIcon,
            notificationTimeout,
            notificationType,
            showFrames,
            currentCalibFrameSrc,
            currentRMSE,
            calibrationRunning,
            clearNotification,
            startCalibration,
            tryClose,
            changeImage,
            saveCalibration
        }
    }
}
</script>

<style scoped>
.flex-container {
    display: flex;
    justify-content: center;
    align-items: flex-start;
    width: 100%;
    height: 90%;
    color: white;
    margin: 5vh auto;
    background-color: rgb(11, 15, 25);
}

.calibration-settings-panel {
    height: 100%;
    width: 30%;
    background-color: rgb(11, 15, 25);
}

.image-source-selector {
    /* background-color: blue; */
    padding-top: 1.5%;
    padding-bottom: 1.5%;
    padding-left: 3%;
    padding-right: 3%;
    background-color: rgb(31, 41, 55);
    border-radius: 5px;
    margin: 0.5% auto;
    width: 98%
}

#image-source-label {
    color: white;
    /* background-color: white; */
    margin-bottom: 1%;
    width: 100%;
    text-align: start;
}

.checkerboard-settings {
    padding-top: 1.5%;
    padding-bottom: 1.5%;
    padding-left: 3%;
    padding-right: 3%;
    background-color: rgb(31, 41, 55);
    border-radius: 5px;
    margin: 1% auto;
    width: 98%;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: start;
}

.title {
    font-weight: bold;
}

.rows-container {
    margin-top: 1%;
    margin-bottom: 1%;
    width: 100%;
    display: flex;
    justify-content: space-between;
}

.cols-container {
    margin-top: 1%;
    margin-bottom: 1%;
    width: 100%;
    display: flex;
    justify-content: space-between;
}

.square-size-container {
    margin-top: 1%;
    margin-bottom: 1%;
    width: 100%;
    display: flex;
    justify-content: space-between;
}

.other-settings {
    padding-top: 1.5%;
    padding-bottom: 1.5%;
    padding-left: 3%;
    padding-right: 3%;
    background-color: rgb(31, 41, 55);
    border-radius: 5px;
    margin: 1% auto;
    width: 98%;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: start;
}

.calibration-frames-container {
    margin-top: 1%;
    margin-bottom: 1%;
    width: 100%;
    display: flex;
    justify-content: space-between;
}

.cooldown-container {
    margin-top: 1%;
    margin-bottom: 1%;
    width: 100%;
    display: flex;
    justify-content: space-between;
}

input {
    width: 60%;
    border: 1px groove rgb(47, 59, 77);
    border-radius: 5px;
    background-color: inherit;
    color: white;
    text-align: center;
}

.calibration-action-container {
    width: 100%;
}

.calibration-info {
    width: 100%;
    height: 35%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.frames-wrap{
    width: 100%;
    height: 40%;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 300%;
    font-weight: bolder;
    color: rgb(47, 59, 77);
}

.clock-wrap{
    background-color: white;
    width: 30%;
    height: 60%;
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center
}
.clock{
    background-color: rgb(31, 41, 55);
    width: 75%;
    height: 75%;
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 400%;
}

button {
    width: 98%;
    color: white;
    background-color: rgb(59, 119, 241);
}

button:disabled,
button[disabled]{
  border: 1px solid #999999;
  background-color: #cccccc;
  color: #666666;
  cursor: not-allowed;
}

.camera-scene-container {
    height: 100%;
    width: 70%;
}


.backdrop {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    width: 100%;
    background-color: rgba(0, 0, 0, 0.75);
    z-index: 10;
}

.frame-view-container {
    position: fixed;
    top: 2vh;
    left: 5vw;
    height: 90vh;
    width: 90vw;
    background-color: rgb(11, 15, 25);
    border-radius: 5px;
    display: flex;
    z-index: 11;
}

.frame-view {
    height: 100;
    width: 75%;
    background-color: black;
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center
}

.prev, .next {
  cursor: pointer;
  position: absolute;
  top: 50%;
  width: auto;
  margin-top: -22px;
  padding: 16px;
  color: white;
  font-weight: bold;
  font-size: 18px;
  transition: 0.6s ease;
  border-radius: 0 3px 3px 0;
  user-select: none;
}

.next {
  right: 0;
  border-radius: 3px 0 0 3px;
}

.prev {
    left: 0;
}

.prev:hover, .next:hover {
  background-color: rgba(0,0,0,0.8);
}

.side-panel {
    display: flex;
    height: 100%;
    width: 25%;
    flex-direction: column;
    justify-content: space-between;
}

.calibration-frames-info {
    display: flex;
    flex-direction: column;
    height: 80%;
    padding: 2%;
}

h2 {
    text-align: left;
    width: 100%;
}

p {
    text-align: justify;
}

.rmse {
    font-weight: bolder;
}

.calibration-actions-container {
    display: flex;
    flex-direction: row;
    justify-content: space-around;
}

.discard-btn {
    width: 45%;
    margin-bottom: 1%;
    background-color: darkgray;
}

.apply-btn {
    width: 45%;
    margin-bottom: 1%;
}

.discard-btn:hover {
    background-color: rgb(128, 128, 128);
    border: none;
}

.apply-btn:hover {
    background-color: rgb(23, 33, 85);
    border: none;
}
</style>
