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
import { useStore } from 'vuex';

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

        const store = useStore();

        const currentRobot = ref(null);
        const selectedComponents = ref([]);
        const currentPosition = ref(null);

        const currentImageSource = ref(null);

        const feedLocation = ref('');
        const showCamera = ref(false);

        let socket = null;
        let wsUid = null;

        const currentConfiguration = computed(function() {
            return store.getters["configurations/getCurrentConfiguration"];
        });

        const robotList = computed(function () {
            return store.getters["robots/getRobots"];
        });

        const components = computed(function () {
            return store.getters["components/getAllComponents"];
        });

        const currentAngles = computed(function () {
            return store.getters["robots/getCurrentAngles"];
        });

        watch(currentAngles, (newVal, _) => {
            if (newVal) {
                jointAngles.value[0] = newVal[0];
                jointAngles.value[1] = newVal[1];
                jointAngles.value[2] = newVal[2];
            }
        });

        watch(currentRobot, (newVal, _) => {
            if (newVal) {
                store.dispatch("robots/loadCurrentRobotPositions", {
                    uid: newVal.uid
                });
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

                store.dispatch("robots/moveRobotToPosition", {
                    robotUid: currentRobot.value.uid,
                    positionUid: newVal.uid
                });
            }
        });

        const robotPositions = computed(function () {
            return store.getters["robots/getCurrentRobotPositions"];
        });

        const imageSources = computed(() => {
            return store.getters['imageSources/getImageSources'];
        });

        watch(currentImageSource, (newValue) => {
            if(newValue)
            {
                feedLocation.value = `ws://${ipAddress}:${port}/image_source/${newValue.uid}/ws`;
                showCamera.value = true;
            }
            else
            {
                showCamera.value = false;
            }
        });

        function refreshAngles(){
            store.dispatch("robots/loadCurrentAngles", {
                uid: currentRobot.value.uid
            });
        }

        function moveRobotHome() {
            store.dispatch("robots/moveRobotHome", {
                uid: currentRobot.value.uid
            });
        }

        function releaseServos() {
            store.dispatch("robots/releaseServos", {
                uid: currentRobot.value.uid
            });
        }

        function powerServos() {
            store.dispatch("robots/powerServos", {
                uid: currentRobot.value.uid
            });
        }

        function saveCurrentPosition() {
            if(currentPosition.value)
            {
                store.dispatch("robots/updateCurrentPosition", {
                    positionUid: currentPosition.value.uid,
                    robotUid: currentRobot.value.uid,
                    speed: speed.value,
                    components: selectedComponents.value.map(component => component.uid),
                    name: positionName.value
                });
            }
            else
            {
                store.dispatch("robots/saveCurrentPosition", {
                    uid: currentRobot.value.uid,
                    speed: speed.value,
                    components: selectedComponents.value.map(component => component.uid),
                    name: positionName.value
                });
            }
        }

        function jointBtnPressed(jointNumber, increase) {
            jointAngles.value[jointNumber - 1] = jointAngles.value[jointNumber - 1] + (increase ? step.value : -step.value);
            setRobotJointAngle(jointNumber, jointAngles.value[jointNumber - 1], speed.value);
        }

        function setRobotJointAngle(jointNumber, angle, speed) {
            store.dispatch("robots/setRobotJointAngle", {
                uid: currentRobot.value.uid,
                jointNumber: jointNumber,
                angle: angle,
                speed: speed,
                name: positionName.value
            });
        }

        function deleteCurrentPosition() {
            if (currentPosition.value) {
                store.dispatch("robots/deleteRobotPosition", {
                    uid: currentPosition.value.uid
                }).then(() => {
                    currentPosition.value = null;
                    selectedComponents.value = [];
                }).catch();
            }
        }

        onMounted(()=>{
            if(currentConfiguration.value)
            {
                store.dispatch("robots/loadRobots");
                store.dispatch("components/loadComponents", {
                    type: 'component'
                });

                store.dispatch("components/loadComponents", {
                    type: 'reference'
                });
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
