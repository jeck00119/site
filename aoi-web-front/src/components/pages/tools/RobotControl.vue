<template>
    <div class="flex-container">
        <div class="content-wrapper">
            <div class="robot-list">
                <vue-multiselect
                    v-model="currentRobot"
                    :options="robotList"
                    track-by="uid"
                    label="name"
                    placeholder="Select Robot"
                    :searchable="true"
                ></vue-multiselect>
            </div>
            <div class="main-container">
                <div class="robot-control">
                    <div class="upper-ctn">
                        <div class="joints-control">
                            <div class="refresh-container">
                                <button class="refresh-btn" @click="refreshAngles" :disabled="!currentRobot">
                                    <v-icon name="md-restartalt" scale="1"/>
                                </button>
                            </div>
                            <div class="first">
                                <label class="joint-label">Joint 1</label>
                                <div class="input-container">
                                    <button id="decrease" class="btn" @click="jointBtnPressed(1, false)" :disabled="!currentRobot">-</button>
                                    <input type="text" id="inputBox" min="-150" max="170" v-model="jointAngles[0]">
                                    <button id="increase" class="btn" @click="jointBtnPressed(1, true)" :disabled="!currentRobot">+</button>
                                </div>
                            </div>
                            <div class="second">
                                <label class="joint-label">Joint 2</label>
                                <div class="input-container">
                                    <button id="decrease" class="btn" @click="jointBtnPressed(2, false)" :disabled="!currentRobot">-</button>
                                    <input type="text" id="inputBox" min="-20" max="90" v-model="jointAngles[1]" readonly>
                                    <button id="increase" class="btn" @click="jointBtnPressed(2, true)" :disabled="!currentRobot">+</button>
                                </div>
                            </div>
                            <div class="third">
                                <label class="joint-label">Joint 3</label>
                                <div class="input-container">
                                    <button id="decrease" class="btn" @click="jointBtnPressed(3, false)" :disabled="!currentRobot">-</button>
                                    <input type="text" id="inputBox" min="-5" max="60" v-model="jointAngles[2]" readonly>
                                    <button id="increase" class="btn" @click="jointBtnPressed(3, true)" :disabled="!currentRobot">+</button>
                                </div>
                            </div>
                        </div>
                        <div class="arm-img-container">
                            <div class="robotic-arm-image">
                                <img src="../../../assets/icons/robot-arm.png" alt="Robotic Arm" width="100%" height="100%">
                            </div>
                        </div>
                    </div>
                    <div class="action-button-container">
                        <button class="home-btn" @click="moveRobotHome" :disabled="!currentRobot">Home</button>
                        <button class="release-btn" @click="releaseServos" :disabled="!currentRobot">Release Servos</button>
                        <button class="power-btn" @click="powerServos" :disabled="!currentRobot">Power On Servos</button>
                    </div>
                    <div class="action-button-container save-container">
                        <button class="save-btn" @click="saveCurrentPosition" :disabled="!currentRobot">Save</button>
                    </div>
                </div>
                <div class="right-container">
                    <div class="speed-container">
                        <label for="speed" class="speed-label">Speed:</label>
                        <input type="number" id="speed" min="1" max="200" v-model="speed" :disabled="!currentRobot">
                    </div>
                    <div class="step-container">
                        <label for="step" class="step-label">Step:</label>
                        <input type="number" id="step" v-model="step" :disabled="!currentRobot">
                    </div>
                    <div class="components-container">
                        <vue-multiselect
                            v-model="selectedComponents"
                            :options="components"
                            track-by="uid"
                            label="name"
                            placeholder="Select Components"
                            :searchable="true"
                            :multiple="true"
                            :disabled="!currentRobot"
                        ></vue-multiselect>
                    </div>
                    <div class="position-name-container">
                        <input type="text" id="position-name" placeholder="Position Name" v-model="positionName" :disabled="!currentRobot">
                    </div>
                    <div class="positions-container">
                        <vue-multiselect
                            v-model="currentPosition"
                            :options="robotPositions"
                            track-by="uid"
                            label="name"
                            placeholder="Select Position"
                            :searchable="true"
                            :multiple="false"
                            :disabled="!currentRobot">
                        </vue-multiselect>
                    </div>
                    <div class="positions-action-container">
                        <button class="delete-btn" @click="deleteCurrentPosition" :disabled="!currentPosition">Delete Current Position</button>
                    </div>
                    <div class="right-lower-container">
                        <div class="robotic-arm-image second-img">
                            <img src="../../../assets/icons/robot-arm-2.png" alt="Robotic Arm" width="100%" height="100%">
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="camera-container">
            <div class="image-source-selector">
                <vue-multiselect
                    v-model="currentImageSource"
                    :options="imageSources"
                    track-by="uid"
                    label="name"
                    placeholder="Select Image Source"
                    :searchable="true"
                ></vue-multiselect>
            </div>
            <div class="camera-scene-container">
                <camera-scene width="100%" height="100%" :show="showCamera" :camera-feed="true"
                            :feed-location="feedLocation" :static-images="[]" :id="1" canvas-id="camera-robot-canvas"
                            :graphics="[]"></camera-scene>
            </div>
        </div>
    </div>
</template>
  
<script>
import { ref, watch, computed, onMounted } from 'vue';
import { useRobotsStore, useComponentsStore, useConfigurationsStore, useImageSourcesStore } from '@/composables/useStore';

import CameraScene from '../../camera/CameraScene.vue';
import VueMultiselect from 'vue-multiselect';

import { ipAddress, port } from '../../../url';
  
export default {
    components: {
        CameraScene,
        VueMultiselect
    },

    setup(props, context) {
        const jointAngles = ref([0, 0, 0]);
        const speed = ref(1);
        const step = ref(0.03);
        const positionName = ref("");

        const robotsStore = useRobotsStore();
        const componentsStore = useComponentsStore();
        const configurationsStore = useConfigurationsStore();
        const imageSourcesStore = useImageSourcesStore();

        const currentRobot = ref(null);
        const selectedComponents = ref([]);
        const currentPosition = ref(null);

        const currentImageSource = ref(null);

        const feedLocation = ref('');
        const showCamera = ref(false);

        let socket = null;
        let wsUid = null;

        // These are already computed refs from the composables
        const currentConfiguration = configurationsStore.currentConfiguration;
        const robotList = robotsStore.robots;
        const components = componentsStore.components;
        const currentAngles = robotsStore.currentAngles;

        watch(currentAngles, (newVal, _) => {
            if (newVal) {
                jointAngles.value[0] = newVal[0];
                jointAngles.value[1] = newVal[1];
                jointAngles.value[2] = newVal[2];
            }
        });

        watch(currentRobot, (newVal, _) => {
            if (newVal) {
                robotsStore.loadCurrentRobotPositions(newVal.uid);
            }
        });

        watch(currentPosition, (newVal, _) => {
            if (newVal) {
                speed.value = newVal.speed;

                jointAngles.value[0] = newVal.angles[0];
                jointAngles.value[1] = newVal.angles[1];
                jointAngles.value[2] = newVal.angles[2];

                selectedComponents.value = [];

                for(let component of newVal.components)
                {
                    selectedComponents.value.push(components.value.find(comp => comp.uid === component));
                }

                robotsStore.moveRobotToPosition(currentRobot.value.uid, newVal.uid);
            }
        });

        const robotPositions = robotsStore.currentRobotPositions;

        const imageSources = imageSourcesStore.imageSources;

        watch(currentImageSource, (newValue) => {
            if(newValue)
            {
                // Include FPS parameter for proper frame rate control
                const fps = newValue.fps || 1; // Default to 1 FPS if not specified
                let wsUrl;
                
                if (newValue.image_source_type === "static") {
                    wsUrl = `ws://${ipAddress}:${port}/image_source/${newValue.uid}/${newValue.image_generator_uid}/${fps}/ws`;
                } else if (newValue.image_source_type === "dynamic") {
                    wsUrl = `ws://${ipAddress}:${port}/image_source/${newValue.uid}/${newValue.camera_uid}/${fps}/ws`;
                } else {
                    // Fallback to old format if type is unknown
                    wsUrl = `ws://${ipAddress}:${port}/image_source/${newValue.uid}/ws`;
                }
                
                feedLocation.value = wsUrl;
                showCamera.value = true;
                console.log('RobotControl - WebSocket URL with FPS:', wsUrl, 'FPS:', fps);
            }
            else
            {
                showCamera.value = false;
            }
        });

        // Watch for FPS changes in the current image source to trigger WebSocket reconnection
        watch(() => currentImageSource.value?.fps, (newFps, oldFps) => {
            if (newFps !== oldFps && newFps != null && currentImageSource.value) {
                console.log('RobotControl - FPS changed, updating WebSocket URL', { newFps, oldFps });
                
                const fps = newFps;
                let wsUrl;
                
                if (currentImageSource.value.image_source_type === "static") {
                    wsUrl = `ws://${ipAddress}:${port}/image_source/${currentImageSource.value.uid}/${currentImageSource.value.image_generator_uid}/${fps}/ws`;
                } else if (currentImageSource.value.image_source_type === "dynamic") {
                    wsUrl = `ws://${ipAddress}:${port}/image_source/${currentImageSource.value.uid}/${currentImageSource.value.camera_uid}/${fps}/ws`;
                } else {
                    wsUrl = `ws://${ipAddress}:${port}/image_source/${currentImageSource.value.uid}/ws`;
                }
                
                feedLocation.value = wsUrl;
                console.log('RobotControl - Updated WebSocket URL for FPS change:', wsUrl);
            }
        });

        function refreshAngles(){
            robotsStore.loadCurrentAngles(currentRobot.value.uid);
        }

        function moveRobotHome() {
            robotsStore.moveRobotHome(currentRobot.value.uid);
        }

        function releaseServos() {
            robotsStore.releaseServos(currentRobot.value.uid);
        }

        function powerServos() {
            robotsStore.powerServos(currentRobot.value.uid);
        }

        function saveCurrentPosition() {
            if(currentPosition.value)
            {
                robotsStore.updateCurrentPosition(
                    currentPosition.value.uid,
                    currentRobot.value.uid,
                    speed.value,
                    selectedComponents.value.map(component => component.uid),
                    positionName.value
                );
            }
            else
            {
                robotsStore.saveCurrentPosition(
                    currentRobot.value.uid,
                    speed.value,
                    selectedComponents.value.map(component => component.uid),
                    positionName.value
                );
            }
        }

        function jointBtnPressed(jointNumber, increase) {
            jointAngles.value[jointNumber - 1] = jointAngles.value[jointNumber - 1] + (increase ? step.value : -step.value);
            setRobotJointAngle(jointNumber, jointAngles.value[jointNumber - 1], speed.value);
        }

        function setRobotJointAngle(jointNumber, angle, speed) {
            robotsStore.setRobotJointAngle(
                currentRobot.value.uid,
                jointNumber,
                angle,
                speed,
                positionName.value
            );
        }

        function deleteCurrentPosition() {
            if (currentPosition.value) {
                robotsStore.deleteRobotPosition(currentPosition.value.uid).then(() => {
                    currentPosition.value = null;
                    selectedComponents.value = [];
                }).catch();
            }
        }

        onMounted(()=>{
            if(currentConfiguration.value)
            {
                robotsStore.loadRobots();
                componentsStore.loadComponents({ type: 'component' });
                componentsStore.loadComponents({ type: 'reference' });
            }
        })

        return {
            jointAngles,
            speed,
            step,
            positionName,
            currentRobot,
            robotList,
            selectedComponents,
            components,
            robotPositions,
            currentPosition,
            imageSources,
            currentImageSource,
            showCamera,
            feedLocation,
            refreshAngles,
            moveRobotHome,
            releaseServos,
            powerServos,
            jointBtnPressed,
            saveCurrentPosition,
            deleteCurrentPosition
        };
    },
};
</script>

<style scoped>
.flex-container {
    position: relative;
    display: flex;
    flex-direction: row;
    align-items: start;
    width: 100%;
    height: 93vh;
    overflow-y: auto;
    margin: auto;
    padding: 1%;
    border-radius: 10px;
    z-index: 10;
}

.content-wrapper {
    display: flex;
    flex-direction: column;
    align-items: start;
    width: 50%;
    height: 90%;
    overflow-y: auto;
    margin: auto;
    margin-top: 2%;
    padding: 1%;
    background-color: black;
    border-radius: 10px;
    z-index: 10;
}

.arm-img-container {
    width: 50%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
}

.robotic-arm-image {
    /* position: absolute;
    top: 5%;
    left: 20%; */
    width: 90%;
    height: 80%;
    overflow: hidden;
    z-index: 0;
}

.second-img {
    width: 100%;
    height: 50%;
    display: flex;
    justify-content: center;
}

img {
    width: 100%;
    height: 100%;
    object-fit: contain;
}

.robot-list {
    width: 100%;
    margin-bottom: 0.5%;
    margin-top: 1%;
    height: 10%;
}

.main-container {
    display: flex;
    width: 100%;
    height: 85%;
}

.robot-control {
    width: 50%;
    height: 100%;
    /* background-color: #ddd; */
}

.upper-ctn {
    display: flex;
    width: 100%;
    height: 50%;
}

.joints-control {
    width: 50%;
    height: 100%;
}

.refresh-container {
    height: 10%;
    width: 100%;
}

.refresh-btn {
    background-color: rgb(0, 0, 0);
    color: white;
    border: none;
    cursor: pointer;
    height: 100%;
    width: 15%;
    display: flex;
    justify-content: center;
    align-items: center;
}

.first {
    margin-top: 1%;
    display: flex;
    height: 25%;
}

.second {
    margin-top: 1%;
    display: flex;
    height: 25%;
}

.third {
    margin-top: 1%;
    display: flex;
    height: 25%;
}

.joint-label {
    color: white;
    text-align: center;
    display: flex;
    justify-content: center;
    align-items: center;
    margin-right: 0.3vw;
    width: 35%;
    font-size: 1vmax;
}

.input-container {
    display: flex;
    align-items: center;
    width: 65%;
}

.btn {
    width: 30%;
    height: 60%;
    background-color: #007bff;
    color: white;
    border: none;
    cursor: pointer;
    font-size: 1rem;
    border-radius: 0 5px 5px 0;
    display: flex;
    justify-content: center;
    align-items: center;
}

#decrease {
    border-radius: 5px 0 0 5px;
}

#inputBox[type="text"] {
    width: 30%;
    height: 60%;
    font-size: 90%;
    border: none;
    background-color: #f9f9f9;
    pointer-events: none;
    padding-left: 0;
    padding-right: 0;
    margin: 0;
    text-align: center;
}

.btn:focus {
    outline: none;
}

/* #inputBox[readonly] {
    background-color: #f1f1f1;
    background-color: red;
    
    z-index: 99;
} */

.right-container {
    display: flex;
    flex-direction: column;
    width: 50%;
    height: 100%;
    margin-left: 1%;
}

.speed-container {
    display: flex;
    flex-direction: row;
    height: 5%;
}

.speed-label {
    color: white;
    display: flex;
    align-items: center;
    width: 20%;
    font-size: 1vmax;
}

#speed {
    width: 80%;
}

.step-container {
    display: flex;
    flex-direction: row;
    height: 5%;
}

.step-label {
    color: white;
    display: flex;
    align-items: center;
    width: 20%;
    font-size: 1vmax;
}

#step {
    width: 80%;
}

.components-container {
    margin-top: 1%;
    height: 7%;
    font-size: 1vmax;
}

.action-button-container {
    margin-top: 2%;
    width: 100%;
    height: 35%;
    display: flex;
    align-items: start;
    flex-direction: column;
}

.save-container {
    height: 10%;
}

.home-btn {
    width: 100%;
    height: 30%;
    border: none;
    cursor: pointer;
    font-size: 1vmax;
}

.release-btn {
    width: 100%;
    height: 30%;
    border: none;
    cursor: pointer;
    font-size: 1vmax;
    margin-top: 1%;
}

.power-btn {
    width: 100%;
    height: 30%;
    border: none;
    cursor: pointer;
    font-size: 1vmax;
    margin-top: 1%;
}

.save-btn {
    width: 100%;
    height: 100%;
    background-color: #007bff;
    color: white;
    border: none;
    cursor: pointer;
    font-size: 1vmax;
}

input {
    text-align: center;
}

.position-name-container {
    width: 100%;
    height: 7%;
    margin-top: 5%;
    display: flex;
    align-items: start;
}

#position-name {
    width: 100%;
    height: 100%;
}

.positions-container {
    width: 100%;
    height: 7%;
    margin-top: 2%;
    display: flex;
    align-items: start;
}

.positions-container .multiselect {
    width: 100%;
    height: 100%;
}

.positions-action-container {
    width: 100%;
    height: 7%;
    margin-top: 2%;
    display: flex;
    align-items: start;
}

.delete-btn {
    width: 100%;
    height: 100%;
    border: none;
    cursor: pointer;
    font-size: 1vmax;
    margin-top: 1%;
    display: flex;
    justify-content: center;
    align-items: center;
}

.right-lower-container {
    width: 100%;
    height: 45%;
    display: flex;
    justify-content: center;
    align-items: end;
}

button:disabled,
button[disabled] {
    border: 1px solid #999999;
    background-color: #cccccc;
    color: #666666;
    cursor: not-allowed;
}

.camera-container {
    width: 49%;
    height: 90%;
    margin-left: 1%;
    display: flex;
    flex-direction: column;
    align-items: start;
    margin-top: 2%;
    padding: 1%;
    background-color: black;
    border-radius: 10px;
    background-color: rgb(31, 41, 55);
}

.image-source-selector {
    /* background-color: blue; */
    padding-top: 1%;
    padding-bottom: 1%;
    border-radius: 5px;
    width: 100%
}

.camera-scene-container {
    height: 90%;
    width: 100%;
}

.multiselect {
    width: 100%;
    height: 100%;
}


</style>


<!-- <style>
.multiselect {
    width: 100%;
    max-height: 50%;
    background-color: red;
    padding: 0;
}

.multiselect__tags {
    /* background-color: #007bff; */
    max-height: 100% !important;
}

.multiselect__content-wrapper {
  max-height: 100% !important;
  overflow-y: auto;
  width: 100%;
  background-color: red;
  margin: 0;
}
</style> -->
