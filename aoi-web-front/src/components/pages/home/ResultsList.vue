<template>
    <div class="flex-container">
        <div class="top-group">
            <div class="action-control">
                <button class="action-button" @click="toggleRunState" :disabled="runButtonStatus">
                    <div class="button-container" :class='{ "pass-text": processRunning }'>
                        <div class="button-icon">
                            <v-icon :name="runButtonIcon" scale="1.5" />
                        </div>
                        <div class="button-text">
                            {{ runButtonMessage }}
                        </div>
                    </div>
                </button>
                <button class="action-button" @click="toggleRunOfflineState" :disabled="runOfflineButtonStatus">
                    <div class="button-container" :class='{"pass-text": processRunningOffline}'>
                        <div class="button-icon">
                            <v-icon :name="runOfflineButtonIcon" scale="1.5" />
                        </div>
                        <div class="button-text">
                            {{ runOfflineButtonMessage }}
                        </div>
                    </div>
                </button>
                <!-- <button class="action-button" @click="capabilityClick" :disabled="true"
                    :class="{ 'action-button-green': capabilityState }">
                    <div class="button-container">
                        <div class="button-icon">
                            <v-icon name="si-speedtest" scale="1.5" />
                        </div>
                        <div class="button-text">
                            CAPABILITY
                        </div>
                        <div v-if="excelBlobPath">
                            <a v-bind:href="excelBlobPath" download="Book.xlsx">Here Baws</a>
                        </div>
                    </div>
                </button> -->
                <!-- <button class="action-button" @click="offsetClick" :disabled="true"
                    :class="{ 'action-button-green': offsetState }">
                    <div class="button-container">
                        <div class="button-icon">
                            <v-icon name="oi-diff-renamed" scale="1.5" />
                        </div>
                        <div class="button-text">
                            OFFSET
                        </div>
                    </div>
                </button> -->
                <!-- <button class="action-button" @click="itacClick" :disabled="true"
                    :class="{ 'action-button-green': itacState }">
                    <div class="button-container">
                        <div class="button-icon">
                            <v-icon name="io-server-sharp" scale="1.5" />
                        </div>
                        <div class="button-text">
                            ITAC
                        </div>
                    </div>
                </button> -->
                <button class="action-button" @click="toggleSaveFailImgsFlag" :class="{ 'action-button-green': saveFailImgsFlag }" :disabled="currentUser?.level !== 'admin'">
                    <div class="button-container">
                        <div class="button-icon">
                            <v-icon name="ri-save-3-fill" scale="1.5" />
                        </div>
                        <div class="button-text">
                            SAVE FAIL IMGS
                        </div>
                    </div>
                </button>
            </div>
            <div class="info-container">
                <div class="process-state" :class='{ "process-running": processStatus !== "IDLE" }'>
                    State: {{ processStatus }}
                </div>
                <div class="hella-logo">
                    <img src="../../../assets/icons/hella-logo-white.png" alt="Hella Logo">
                </div>
            </div>
        </div>
        <div class="results-container">
            <div class="card-wrapper">
                <base-card width="100%" height="100%">
                    <div class="main-container" v-if="currentInspectionResult">
                        <div class="main-result-image">
                            <img :src='resultImage' alt="Result Image">
                        </div>
                        <div class="main-details">
                            <div class="name">
                                <h2>PART NAME: {{ currentInspectionResult.name }} {{ currentConfiguration.part_number }}</h2>
                            </div>
                            <div class="main-status">
                                <div class="status-text" :class='{ "pass": currentInspectionResult.status === "Pass", "fail": currentInspectionResult.status === "Fail" }'>
                                    <h2>STATUS:</h2>
                                </div>
                                <div class="status-info">
                                    <div class="status-value" :class='{ "pass-text": currentInspectionResult.status === "Pass", "fail-text": currentInspectionResult.status === "Fail" }'>
                                        {{ currentInspectionResult.status }}
                                    </div>
                                    <div class="status-icon" :class='{ "pass-text": currentInspectionResult.status === "Pass", "fail-text": currentInspectionResult.status === "Fail" }'>
                                        <v-icon :name="statusIcon" scale="10" />
                                    </div>
                                </div>
                            </div>
                            <div class="data-wrapper">
                                <div v-if="currentInspectionResult.name === 'PINS'">
                                    <div v-for="pinsData in currentInspectionResult.data">
                                        <h5>CONNECTOR {{ idx + 1 }}</h5>
                                        <pins-result-table :dimensions="2" :data="pinsData"></pins-result-table>
                                    </div>
                                </div>
                                <div v-else class="table-wrapper">
                                    <table class="result-table">
                                        <thead>
                                            <tr>
                                                <th>Name</th>
                                                <th>Detected</th>
                                                <th>Expected</th>
                                            </tr>
                                        </thead>
                                        <tr v-for="value, key in currentInspectionResult.data" :key="key"
                                            :class='{ "failed-inspection": value.pass === false, "table-data-pass": value.pass === true }'>
                                            <td>{{ value.inspection_name }}</td>
                                            <td>{{ value.value }}</td>
                                            <td>{{ value.expected }}</td>
                                        </tr>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </base-card>
            </div>
        </div>
        <div class="carousel">
            <carousel :items-to-show="6" snap-align="start" style="height: 100%;">
                <template #slides>
                    <slide v-for="result, idx in inspectionResults" :key="result.name">
                        <base-card @click="setCurrentInspectionIdx(idx)">
                            <div class="thumbnail-container"
                                :class='{ "pass": result.status === "Pass", "fail": result.status === "Fail" }'>
                                <div class="result-image">
                                    <img :src="getResultImage(result)" alt="Result Image">
                                </div>
                                <div class="status">
                                    <div class="status-visual">
                                        <p>{{ result.name }}</p>
                                    </div>
                                </div>
                            </div>
                        </base-card>
                    </slide>
                </template>

                <template #addons="{ slidesCount }">
                    <navigation />
                    <pagination />
                </template>
            </carousel>
        </div>
        <div class="status-footer">
            <div class="run-status">
                <div class="run">
                    <v-icon name="md-restartalt" scale="1.5"/>
                    <p>Running</p>
                    <div class="lightbulb off" :class='{ "on": processRunning || processRunningOffline}'></div>
                </div>
                <div class="itac">
                    <v-icon name="fa-server" scale="1.5"/>
                    <p>ITAC</p>
                    <div class="lightbulb off" :class='{ "on": processRunning }'></div>
                </div>
                <div class="cognex">
                    <v-icon name="co-matrix" scale="1.5"/>
                    <p>Cognex</p>
                    <div class="lightbulb off" :class='{ "on": cognexConnected }'></div>
                </div>
                <div class="camera">
                    <v-icon name="bi-camera-video-fill" scale="1.5"/>
                    <p>Camera</p>
                    <div class="lightbulb off" :class='{ "on": cameraConnected }'></div>
                </div>
            </div>
            <div class="left-side-container">
                <div class="dmc">
                    <v-icon name="md-viewarray-round" scale="1.5"/>
                    <div class="text">DMC: {{ currentDMC ? currentDMC : 'N/A' }}</div>
                </div>
                <div class="help">
                    <router-link :to="'/help'" style="width: 100%; height: auto; padding: 0; margin: 0;">
                        <button class="help-button">
                            <div class="button-container help-button-container">
                                <div class="button-icon-help">
                                    <v-icon name="hi-solid-question-mark-circle" scale="1.5"/>
                                </div>
                            </div>
                        </button>
                    </router-link>
                </div>
            </div>
        </div>
        <base-notification :show="showNotification" :timeout="notificationTimeout" height="15vh" color="#CCA152" @close="clearNotification">
            <div class="message-wrapper">
                <div class="icon-wrapper">
                    <v-icon :name="notificationIcon" scale="2.5" animation="float" />
                </div>
                <div class="text-wrapper">
                    {{ notificationMessage }}
                </div>
            </div>
        </base-notification>
        <base-notification :show="showItacNotification" :timeout="itacNotificationTimeout" height="15vh" :color="itacStatusColor" top="77%" left="78%" @close="clearNotificationItac">
            <div class="message-wrapper">
                <div class="icon-wrapper">
                    <v-icon :name="itacStatusIcon" scale="2.5" animation="pulse" />
                </div>
                <div class="text-wrapper">
                    {{ itacStatusMessage }}
                </div>
            </div>
        </base-notification>
    </div>
</template>

<script>

import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useStore } from 'vuex';
import { uuid } from "vue3-uuid";

import useNotification from '../../../hooks/notifications.js';

import 'vue3-carousel/dist/carousel.css';
import { Carousel, Slide, Pagination, Navigation } from 'vue3-carousel';

import PinsResultTable from '../../layout/PinsResultTable.vue';
import { ipAddress, port } from '../../../url';



export default {
    components: {
        Carousel,
        Slide,
        Pagination,
        Navigation,
        PinsResultTable
    },

    setup() {
        const store = useStore();
        const processRunning = ref(false);
        const processRunningOffline = ref(false);
        let wsProcess = null;
        let processId = null;

        let cognexStateSocket = null;
        let cognexStateSocketId = null;

        const cognexConnected = ref(false);

        let cameraStateSocket = null;
        let cameraStateSocketId = null;

        const cameraConnected = ref(false);

        const firstRun = ref(false);

        const currentInspectionIdx = ref(-1);
        const saveFailImgsFlag = ref(false);

        const disableRunButton = ref(false);
        const disableRunOfflineButton = ref(false);

        const {showNotification, notificationMessage, notificationIcon, notificationTimeout, 
            setNotification, clearNotification} = useNotification();

        const {showNotification: showItacNotification, notificationMessage: itacStatusMessage, notificationIcon: itacStatusIcon, notificationTimeout: itacNotificationTimeout, 
            setNotification: setNotificationItac, clearNotification: clearNotificationItac} = useNotification();

        const itacStatusColor = ref('');

        onMounted(() => {
            processId = uuid.v4();
            cognexStateSocketId = uuid.v4();
            cameraStateSocketId = uuid.v4();

            store.dispatch("process/getCapabilityState");
            store.dispatch("process/getOffsetState");

            connectToStateSocket();
            connectToCognexStateSocket();
            connectToCameraStateSocket();
        });

        onUnmounted(async () => {
            try {
                store.dispatch("process/stopProcessing");

                clearNotification();

                store.commit("process/setProcessStatus", 'IDLE');

                await closeSocket();
                await closeCognexSocket();
                await closeCameraSocket();

                if (wsProcess) {
                    wsProcess.close();
                    wsProcess = null;
                }

                if (cognexStateSocket) {
                    cognexStateSocket.close();
                    cognexStateSocket = null;
                }

                if(cameraStateSocket) {
                    cameraStateSocket.close();
                    cameraStateSocket = null;
                }
            } catch (error) {
                console.warn('Error during ResultsList component unmounting:', error);
            }
        });

        async function closeSocket() {
            await store.dispatch("process/closeProcessStateSocket", {
                uid: processId
            });
            wsProcess.removeEventListener("open", onStateSocketOpen);
            wsProcess.removeEventListener("message", onStateSocketMsgRecv);
        }

        async function closeCognexSocket() {
            await store.dispatch("peripherals/closeDeviceStateSocket", {
                uid: cognexStateSocketId
            });
            cognexStateSocket.removeEventListener("message", onCognexStateSocketMsgRecv);
        }

        async function closeCameraSocket() {
            await store.dispatch("peripherals/closeDeviceStateSocket", {
                uid: cameraStateSocketId
            });
            cameraStateSocket.removeEventListener("message", onCameraStateSocketMsgRecv);
        }

        function connectToStateSocket() {
            wsProcess = new WebSocket(`ws://${ipAddress}:${port}/processing/${processId}/process`);

            wsProcess.addEventListener("open", onStateSocketOpen);
            wsProcess.addEventListener("message", onStateSocketMsgRecv);
        }

        function connectToCognexStateSocket() {
            cognexStateSocket = new WebSocket(`ws://${ipAddress}:${port}/peripheral/${cognexStateSocketId}/cognex_status/ws`);
            cognexStateSocket.addEventListener("message", onCognexStateSocketMsgRecv);
        }

        function connectToCameraStateSocket() {
            cameraStateSocket = new WebSocket(`ws://${ipAddress}:${port}/peripheral/${cameraStateSocketId}/camera_status/ws`);
            cameraStateSocket.addEventListener("message", onCameraStateSocketMsgRecv);
        }

        function onStateSocketOpen() {
            if (wsProcess) wsProcess.send("eses");
        }

        function onStateSocketMsgRecv(event) {
            const data = JSON.parse(event.data);
            wsProcess.send("pong");

            if(processRunning.value || processRunningOffline.value)
            {
                switch(data.event) {
                    case 'done_results':
                        if (showNotification.value) {
                            showNotification.value = false;
                        }

                        firstRun.value = false;

                        store.dispatch("process/resetInspectionResultsStatus");

                        store.commit("process/setInspectionResults", data.data);
                        
                        if(data.data.length !== 0)
                        {
                            setCurrentInspectionIdx(0);
                        }
                        break;
                    case 'dmc':
                        store.commit("process/setDMC", data.data);
                        break;
                    case 'done_capability':
                        store.dispatch("process/getCapabilityReport");
                        break;
                    case 'process_status':
                        // if (data.data === "Waiting for DMC") {
                        //     setNotification(null, 'Waiting for DMC.', 'co-matrix');
                        // }
                        if (data.data === "Inspecting Cable" && firstRun.value) {
                            setNotification(null, 'Detection model is being loaded. Please wait.', 'io-rocket-sharp');
                        }
                        else {
                            clearNotification();
                        }
                        store.commit("process/setProcessStatus", data.data);
                        break;
                    case 'ITAC Status':
                        if(data.data.includes('NACK'))
                        {
                            itacStatusColor.value = '#733131'
                            setNotificationItac(4000, data.data, 'fc-cancel');
                        }
                        else
                        {
                            itacStatusColor.value = '#317343'
                            setNotificationItac(4000, data.data, 'fc-ok');
                        }
                        break;
                }
            }
        }

        function onCognexStateSocketMsgRecv(event) {
            const data = JSON.parse(event.data);

            if (data.status === true)
            {
                cognexConnected.value = true;
            }
            else
            {
                cognexConnected.value = false;
            }
        }

        function onCameraStateSocketMsgRecv(event) {
            const data = JSON.parse(event.data);

            if (data.status === true)
            {
                cameraConnected.value = true;
            }
            else
            {
                cameraConnected.value = false;
            }
        }

        function toggleRunState() {
            processRunning.value = !processRunning.value;

            if (processRunning.value) {
                store.dispatch("process/startProcessing", {
                    offline: false
                }).then(function() {
                    disableRunButton.value = false;
                    disableRunOfflineButton.value = false;
                }).catch((e) => {
                    processRunning.value = false;

                    disableRunButton.value = false;
                    disableRunOfflineButton.value = false;

                    clearNotification();

                    store.commit("process/setProcessStatus", 'IDLE');

                    store.dispatch("errors/addError", {
                        id: uuid.v4(),
                        title: "Error on running",
                        description: e.message
                    });
                });
                
                firstRun.value = true;
                disableRunOfflineButton.value = true;
            }
            else {
                disableRunButton.value = true;
                store.dispatch("process/stopProcessing");

                clearNotification();

                store.commit("process/setProcessStatus", 'IDLE');
            }
        }

        function toggleRunOfflineState() {
            processRunningOffline.value = !processRunningOffline.value;

            if (processRunningOffline.value) {
                store.dispatch("process/startProcessing", {
                    offline: true
                }).then(function() {
                    disableRunOfflineButton.value = false;
                    disableRunButton.value = false;
                }).catch((e) => {
                    processRunningOffline.value = false;

                    disableRunOfflineButton.value = false;
                    disableRunButton.value = false;

                    clearNotification();

                    store.commit("process/setProcessStatus", 'IDLE');

                    store.dispatch("errors/addError", {
                        id: uuid.v4(),
                        title: "Error on running",
                        description: e.message
                    });
                });
                
                firstRun.value = true;
                disableRunButton.value = true;
            }
            else {
                disableRunOfflineButton.value = true;
                store.dispatch("process/stopProcessing");

                clearNotification();

                store.commit("process/setProcessStatus", 'IDLE');
            }
        }

        const currentUser = computed(function () {
            return store.getters["auth/getCurrentUser"];
        });

        const currentConfiguration = computed(function() {
            return store.getters["configurations/getCurrentConfiguration"];
        });

        const runButtonIcon = computed(function () {
            return processRunning.value ? "bi-stop-fill" : "bi-play-circle-fill";
        });

        const runOfflineButtonIcon = computed(function () {
            return processRunningOffline.value ? "bi-stop-fill" : "bi-play-circle-fill";
        });

        const runButtonMessage = computed(function () {
            return processRunning.value ? "STOP" : "RUN";
        });

        const runOfflineButtonMessage = computed(function () {
            return processRunningOffline.value ? "STOP OFFLINE" : "RUN OFFLINE";
        });

        const currentInspectionResult = computed(function () {
            return store.getters['process/getInspectionResultByIdx'](currentInspectionIdx.value);
        });

        const currentDMC = computed(function () {
            return store.getters['process/getDMC'];
        });

        const filteredInspectionResult = computed(function () {
            let result = {};

            let expected_head = {};
            let found_head = {};

            for (const [key, value] of Object.entries(currentInspectionResult.value.data)) {
                if (value.inspection_name === "clip_count") {
                    result[key] = value;
                    result[key].inspection_name = "Clips Count"
                }
                else
                {
                    if (value.expected === 1)
                    {
                        expected_head[key] = value;
                    }

                    if (value.value === 1) {
                        found_head[key] = value;
                    }
                }
            }

            let expected_keys = Object.keys(expected_head);
            let found_keys = Object.keys(found_head);

            if (found_keys.length > 0 && expected_keys.length > 0) {
                result[found_keys[0]] = {
                    value: found_head[found_keys[0]].inspection_name.split('_')[1],
                    expected: expected_head[expected_keys[0]].inspection_name.split('_')[1],
                    pass: found_head[found_keys[0]].inspection_name.split('_')[1] === expected_head[expected_keys[0]].inspection_name.split('_')[1],
                    inspection_name: "Head"
                };
            }

            return result;
        });

        const resultImage = computed(function () {
            return 'data:image/png;base64,' + currentInspectionResult.value.image;
        });

        const statusIcon = computed(function () {
            return currentInspectionResult.value.status === 'Pass' ? 'fa-regular-smile' : 'hi-emoji-sad';
        });

        const runButtonStatus = computed(function() {
            return disableRunButton.value;
        });

        const runOfflineButtonStatus = computed(function() {
            return disableRunOfflineButton.value || !currentConfiguration.value;
        });

        function getResultImage(result) {
            if (result.image) {
                return 'data:image/png;base64,' + result.image;
            }

            return null;
        }

        function setCurrentResult(name) {
            store.commit('process/setCurrentInspectionResult', name);
        }

        function setCurrentInspectionIdx(idx) {
            currentInspectionIdx.value = idx;
        }

        function resetInspectionResults() {
            store.commit("process/setInspectionResults", []);
        }

        async function capabilityClick() {
            await store.dispatch("process/postCapabilityState");
            store.dispatch("process/getCapabilityState");
        }

        async function offsetClick() {
            await store.dispatch("process/postOffsetState");
            store.dispatch("process/getOffsetState");
        }

        async function itacClick() {
            await store.dispatch("process/postItacState");
            store.dispatch("process/getItacState");
        }

        function toggleSaveFailImgsFlag() {
            saveFailImgsFlag.value = !saveFailImgsFlag.value;
            store.dispatch("process/setSaveFailImgsFlag", saveFailImgsFlag.value);
        }

        return {
            processRunning,
            processRunningOffline,
            runButtonIcon,
            runButtonMessage,
            runOfflineButtonIcon,
            runOfflineButtonMessage,
            resultImage,
            showNotification,
            statusIcon,
            notificationIcon,
            notificationMessage,
            notificationTimeout,
            showItacNotification,
            itacStatusMessage,
            itacStatusIcon,
            itacNotificationTimeout,
            itacStatusColor,
            saveFailImgsFlag,
            runButtonStatus,
            runOfflineButtonStatus,
            currentUser,
            cognexConnected,
            cameraConnected,
            setCurrentResult,
            toggleRunState,
            toggleRunOfflineState,
            capabilityClick,
            offsetClick,
            itacClick,
            getResultImage,
            setCurrentInspectionIdx,
            toggleSaveFailImgsFlag,
            clearNotification,
            clearNotificationItac,
            currentConfiguration,
            inspectionResults: computed(() => store.getters['process/getInspectionResults']),
            currentInspectionResult,
            currentDMC,
            filteredInspectionResult,
            excelBlobPath: computed(() => store.getters['process/getExcelBlobPath']),
            excelBlob: computed(() => store.getters['process/getExcelBlob']),
            offsetState: computed(() => store.getters['process/getOffsetState']),
            itacState: computed(() => store.getters['process/getItacState']),
            capabilityState: computed(() => store.getters['process/getCapabilityState']),
            processStatus: computed(() => store.getters['process/getProcessStatus'])
        }
    }
}
</script>

<style scoped>
.process-state {
    display: flex;
    align-items: center;
    font-size: 1vw;
    white-space: normal;
    line-height: 1.2;
    font-weight: bolder;
    height: 100%;
    padding-left: 2%;
    padding-right: 2%;
}

.top-group {
    display: flex;
    align-items: center;
    background-color: #1a1a1a;
    margin-top: 1%;
    height: 9%;
}

.flex-container {
    display: flex;
    justify-content: flex-start;
    /* align-items: flex-start; */
    width: 100%;
    color: white;
    height: 92vh;
    /* margin-top: 1vh; */
    flex-direction: column;
}

.action-control {
    display: flex;
    margin: 1vh 0;
    justify-content: start;
    align-items: flex-end;
    width: 45%;
    padding-left: 30px;
}

.action-button {
    width: 25%;
    height: 4vh;
    margin-right: 10px;
}

.action-button-green {
    background-color: rgba(0, 128, 0, 0.66);
    color: white;
}

.button-container {
    display: flex;
    width: 100%;
    height: 100%;
    max-width: 100%;
    justify-content: center;
    align-items: center;
    color: #000033;
    font-weight: bolder;
}

.button-icon {
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
}

.button-icon-help {
    height: auto;
}

.button-text {
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 70%;
    white-space: normal;
    line-height: 1.2;
    font-size: 0.8vw;
}

button:disabled,
button[disabled] {
    border: 1px solid #999999;
    background-color: #cccccc;
    color: #666666;
    cursor: not-allowed;
}

button:hover:not(:disabled) {
    border: none;
    background-color: gray;
}

.info-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 55%;
    height: 100%;
}

.results-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 59%;
    width: 100%;
    margin-top: 1%;
}

img {
    max-width: 100%;
    max-height: 100%;
}

.status-footer {
    display: flex;
    justify-content: space-between;
    width: 100%;
    height: 8%;
    background-color: #1a1a1a;
    margin-top: 1%;
}

.run-status {
    display: flex;
    justify-content: flex-start;
    align-items: center;
    width: 50%;
    height: 100%;
    flex-direction: row;
    padding: 1%;
}

.run {
    display: flex;
    flex-direction: row;
    justify-content: flex-start;
    align-items: center;
    width: 20%;
    height: 80%;
}

.itac {
    display: flex;
    flex-direction: row;
    justify-content: flex-start;
    align-items: center;
    width: 20%;
    height: 80%;
    margin-left: 2%;
}

.cognex {
    display: flex;
    flex-direction: row;
    justify-content: flex-start;
    align-items: center;
    width: 20%;
    height: 80%;
    margin-left: 2%;
}

.camera {
    display: flex;
    flex-direction: row;
    justify-content: flex-start;
    align-items: center;
    width: 20%;
    height: 80%;
    margin-left: 2%;
}

.lightbulb {
  width: 20%;
  padding-top: 20%;
  border-radius: 50%;
  margin-left: 1%;
  background: radial-gradient(circle at 30% 30%, #ff0, rgb(61, 155, 61));
  
}

p {
    align-self: center;
    margin: 0;
    width: 50%;
    font-size: 1vw;
    font-weight: bold;
    white-space: normal;
    line-height: 1.2;
}

.off {
  background: #ccc;
}

.on {
  background: rgb(18, 94, 35);
  box-shadow: 0 0 20px rgb(61, 155, 61);
}

.left-side-container {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    width: 50%;
    height: 100%;
    flex-direction: row;
}

.dmc {
    font-size: 1vw;
    font-weight: bold;
    width: 50%;
    display: flex;
    justify-content: flex-start;
    align-items: center;
}

.carousel {
    width: 100%;
    background-color: rgb(56, 51, 51);
    display: flex;
    flex-direction: column;
    margin-left: 0;
    margin-right: 0;
    justify-content: flex-start;
    height: 29%;
    margin-top: 1%;
    /* align-items: start; */
}

.thumbnail-container {
    display: flex;
    flex-direction: column;
    justify-content: space-evenly;
    width: 12vw;
    height: 100%;
    align-items: center;
    /* margin-right: 1vw;
    margin-left: 1vw; */
    border-radius: 12px;
    padding: 5px;
    transition: all 0.3s ease-in;
}

.thumbnail-container:hover {
    cursor: pointer;
    transform: scale(1.1);
}

.pass {
    background-color: rgba(0, 128, 0, 0.66);
}

.fail {
    background-color: rgba(255, 0, 0, 0.658);
}

.fail-text {
    color: rgba(255, 0, 0, 0.658); 
}

.pass-text {
    color: rgba(0, 128, 0, 0.66);
}

.process-running {
    background-color: rgb(204, 161, 82);
    animation-name: process-running-anim;
    animation-duration: 1s;
    animation-iteration-count: infinite;
    animation-direction: alternate;

}

.failed-inspection {
    background-color: rgba(255, 0, 0, 0.658);
    animation-name: failed-inspection-anim;
    animation-duration: 1s;
    animation-iteration-count: infinite;
    animation-direction: alternate;
}

.status {
    width: 100%;
    display: flex;
    height: 20%;
    min-height: 20%;
    margin-left: 3px;
    justify-content: center;
    align-items: center;
    /* background-color: blue; */
}

.status-visual {
    display: flex;
    height: 20%;
    width: 100%;
    flex-direction: row;
    justify-content: center;
    align-items: center;
    font-weight: bold;
    /* background-color: rgb(46, 53, 53); */
}

.result-image {
    /* width: 5vw; */
    display: flex;
    justify-content: center;
    align-items: center;
    height: 80%;
    /* height: 18vh; */
    /* width: 50%; */
    /* background-color: brown;
    color: black; */
}

.hella-logo {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 10%;
    height: 100%;
    margin-right: 1%;
}

.main-container {
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: flex-start;
}

.main-result-image {
    height: 93%;
    width: 62%;
    /* background-color: red; */
    display: flex;
    justify-content: center;
    align-items: center;
    margin-right: 2%;
}

.main-details {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    height: auto;
    width: 35%;
}

.card-wrapper {
    width: 100%;
    height: 100%;
    padding: 0;
}

.name {
    width: 100%;
    background-color: black;
    border-radius: 10px;
    margin-bottom: 1vh;
}

.main-status {
    width: 100%;
    border-radius: 10px;
    display: flex;
    justify-content: center;
    flex-direction: column;
    margin-bottom: 2%;
    background-color: rgb(43, 41, 41);
}

.status-text {
    border-radius: 10px 10px 0px 0px;
}

.status-info {
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-direction: row;
}

.status-value {
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 450%;
    font-weight: bold;
}

.status-icon {
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
}

.data-wrapper {
    height: 45vh;
    margin-top: 2vh;
    overflow-y: auto;
}

table {
    border-collapse: collapse;
    width: 100%;
}

.table-wrapper {
    /* height: 10vh; */
    overflow-y: auto;
    width: 100%;
    margin-top: 1vh;
}

.table-wrapper::-webkit-scrollbar {
    display: none;
}

.table-wrapper thead th {
    background-color: black;
    position: sticky;
    top: 0;
    z-index: 1;
}

.result-table {
    background-color: rgb(0, 0, 0);
    color: rgb(255, 255, 255);
    width: 100%;
    border-collapse: collapse;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.26);
    margin: 0;
    border-collapse: separate;
    border-spacing: 0;
    overflow: hidden;
    border-radius: 10px;
}

.result-table tr {
    border-bottom: 1px solid #696464;
    height: 8vh;
    font-size: 1.5rem;
    font-weight: bold;
    background-color: #524d4d;
    color: white;
}

.result-table tr.pass-text {
    color: rgb(105, 192, 105);
}

.result-table td {
    padding: 5px;
}

.table-data-pass {
    background-color: #524d4d;
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

.help {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 10%;
    height: 100%;
    margin-right: 2%;
    margin-left: 2%;
}

.help-button {
    width: 100%;
    height: auto;
    background-color: rgb(0, 0, 0);
    border: none;
    padding: 5% 35%;
    /* border-radius: 10px; */
}

.help-button-container {
    color: rgb(204, 161, 82);
}

@keyframes process-running-anim {
    from {
        background-color: #1a1a1a;
    }

    to {
        background-color: rgb(204, 161, 82);
    }
}

@keyframes failed-inspection-anim {
    from {
        color: white;
    }

    to {
        color: rgba(255, 0, 0, 0.658);
    }
}
</style>