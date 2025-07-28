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
            height="15vh"
            color="#CCA152"
            @close="clearNotification"
        >
            <div class="message-wrapper">
                <div class="icon-wrapper">
                    <v-icon :name="notificationIcon" scale="2.5" animation="spin"/>
                </div>
                <div class="text-wrapper">
                    {{ notificationMessage }}
                </div>
            </div>
        </base-notification>
    </div>
</template>

<script>
import VueMultiselect from 'vue-multiselect';

import useNotification from '../../../hooks/notifications';
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import { useStore } from 'vuex';
import { uuid } from 'vue3-uuid';

import CameraScene from '../../camera/CameraScene.vue';
import { ipAddress, port } from '../../../url';

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

        let socket = null;
        let wsUid = null;

        const store = useStore();

        const {showNotification, notificationMessage, notificationIcon, notificationTimeout, 
            setNotification, clearNotification} = useNotification();

        const imageSources = computed(() => {
            return store.getters['imageSources/getImageSources'];
        });

        const imageSourcesNames = computed(function() {
            return store.getters["imageSources/getImageSources"].map(imageSource => imageSource.name);
        });

        watch(currentImageSource, (newValue) => {
            const imageSource = imageSources.value.find(imageSource => imageSource.name === newValue);

            if(imageSource)
            {
                feedLocation.value = `ws://${ipAddress}:${port}/image_source/${imageSource.uid}/ws`;
                showCamera.value = true;
            }
            else
            {
                showCamera.value = false;
            }
        });

        watch(currentImageIdx, (newValue) => {
            if(newValue >= 0)
            {
                socket.send(JSON.stringify({
                    "command": "retrieve",
                    "idx": currentImageIdx.value
                }));
            }
        });

        function startCalibration() {
            calibrationRunning.value = true;

            connectToWs();

            store.dispatch('cameraCalibration/setCalibrationParameters', {
                rows: checkerboardRows.value,
                cols: checkerboardCols.value,
                square_size: checkerboardSquareSize.value
            });

            timeRemaining.value = cooldown.value;

            var timer = setInterval(() => {
                if(timeRemaining.value > 0)
                {
                    timeRemaining.value -= 1;
                }
                else
                {
                    socket.send(JSON.stringify({
                        command: "capture"
                    }));
                    framesAcquired.value += 1;
                    if(framesAcquired.value < calibrationFrames.value)
                    {
                        timeRemaining.value = cooldown.value;
                    }
                    else
                    {
                        socket.send(JSON.stringify({
                            command: "calibrate"
                        }));
                        setNotification(null, 'Calibrating...', 'fa-cog');
                        clearInterval(timer);
                    }
                }
            }, 1000);
        }

        function connectToWs() 
        {
            wsUid = uuid.v4();
            const imageSource = imageSources.value.find(imageSource => imageSource.name === currentImageSource.value);
            socket = new WebSocket(`ws://${ipAddress}:${port}/camera_calibration/${imageSource.uid}/ws/${wsUid}`);

            socket.addEventListener("message", onCalibrationSocketMsgRecv);
        }

        async function disconnectFromWs() 
        {
            const imageSource = imageSources.value.find(imageSource => imageSource.name === currentImageSource.value);
            await store.dispatch("cameraCalibration/closeCalibrationSocket", {
                uid: imageSource.uid
            });
            socket.removeEventListener("message", onCalibrationSocketMsgRecv);

            if(socket)
            {
                socket.close();
                socket = null;
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
                currentCalibFrameSrc.value = 'data:image/png;base64,' + data.data;
            }
            else if(data.details === "calibError")
            {
                clearNotification();
                setNotification(3000, "Calibration failed. Please try again.", 'bi-exclamation-circle-fill');
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
            socket.send(JSON.stringify({
                "command": "save",
                "uid": uuid.v4()
            }));
            socket.send(JSON.stringify({
                "command": "stop",
            }));
            showFrames.value = false;

            socket.removeEventListener("message", onCalibrationSocketMsgRecv);

            if(socket)
            {
                socket.close();
                socket = null;
            }
        }

        onMounted(() => {
            
        });

        onUnmounted(() => {
            if(socket)
                disconnectFromWs();
        });

        return {
            currentImageSource,
            imageSources,
            imageSourcesNames,
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
