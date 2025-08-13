<template>
    <div class="flex-container" :style="{width: width, height: height}">
        <div class="action-container">
                <base-tabs-wrapper @tab-changed="tabChanged">
                    <base-tab :title="tabs[0]">
                        <div class="tab-wrapper">
                            <div class="action-wrapper">
                                <div class="action">
                                    <base-button-rectangle
                                        width="100%"
                                        @state-changed="singleRunReference"
                                        :disabled="disableActions || currentReferenceName === null"
                                    >
                                        <div class="button-container">
                                            <div class="button-icon">
                                                <v-icon name="md-repeatone-outlined" scale="1.5"/>
                                            </div>
                                            <div class="button-text">Single proc.</div>
                                        </div>
                                    </base-button-rectangle>
                                </div>
                                <div class="action">
                                    <base-button-rectangle
                                        width="100%"
                                        @state-changed="liveProcessReference"
                                        :disabled="disableActions || currentReferenceName === null"
                                    >
                                        <div class="button-container">
                                            <div class="button-icon">
                                                <v-icon name="si-kdenlive" scale="1.5"/>
                                            </div>
                                            <div class="button-text">Live proc.</div>
                                        </div>
                                    </base-button-rectangle>
                                </div>
                            </div>
                            <div class="algorithm-list">
                                <vue-multiselect
                                    v-model="currentReferenceName"
                                    :options="referenceAlgorithms"
                                    placeholder="Select Reference Algorithm"
                                    :searchable="true"
                                ></vue-multiselect>
                            </div>
                            <div class="algorithm-parameters" v-if="currentReferenceName">
                                <algorithm-parameters
                                        type="reference"
                                        :algorithm-attributes="referenceAlgorithmAttributes ? referenceAlgorithmAttributes : []"
                                        :parameters="referenceParameters ? referenceParameters : []"
                                        height="95%"
                                    ></algorithm-parameters>
                            </div>
                            <div class="action-wrapper">
                                <div class="action">
                                    <base-button-rectangle
                                        width="100%" 
                                        @state-changed="$refs.importAlgorithm.click()"
                                    >
                                        <div class="button-container">
                                            <div class="button-icon">
                                                <v-icon name="fa-file-upload" scale="1.5"/>
                                            </div>
                                            <div class="button-text">Load</div>
                                        </div>
                                    </base-button-rectangle>
                                    <input
                                        type="file"
                                        ref="importAlgorithm"
                                        style="display:none"
                                        name="file-import-algorithm"
                                        id="fileImportAlgorithm"
                                        accept=".json"
                                        :disabled="false"
                                        @change="onFileSelected"
                                    />
                                </div>
                                <div class="action">
                                    <base-button-rectangle
                                        width="100%"
                                        @state-changed="downloadCurrentAlgorithm"
                                    >
                                        <div class="button-container">
                                            <div class="button-icon">
                                                <v-icon name="fa-file-download" scale="1.5"/>
                                            </div>
                                            <div class="button-text">Save</div>
                                        </div>
                                    </base-button-rectangle>
                                </div>
                            </div>
                        </div>
                    </base-tab>

                    <base-tab :title="tabs[1]">
                        <div class="tab-wrapper">
                            <div class="action-wrapper">
                                <div class="action">
                                    <base-button-rectangle
                                        width="100%"
                                        @state-changed="singleRun"
                                        :disabled="disableActions || currentAlgorithmName === null"
                                    >
                                        <div class="button-container">
                                            <div class="button-icon">
                                                <v-icon name="md-repeatone-outlined" scale="1.5"/>
                                            </div>
                                            <div class="button-text">Single proc.</div>
                                        </div>
                                    </base-button-rectangle>
                                </div>
                                <div class="action">
                                    <base-button-rectangle
                                        width="100%"
                                        @state-changed="liveProcess"
                                        :active="false"
                                        :disabled="disableActions || currentAlgorithmName === null"
                                    >
                                        <div class="button-container">
                                            <div class="button-icon">
                                                <v-icon name="si-kdenlive" scale="1.5"/>
                                            </div>
                                            <div class="button-text">Live proc.</div>
                                        </div>
                                    </base-button-rectangle>
                                </div>
                            </div>
                            <div class="algorithm-list">
                                <vue-multiselect
                                    v-model="currentAlgorithmName"
                                    :options="Array.isArray(algorithms) ? algorithms.map(alg => alg && alg.type ? alg.type : String(alg)).filter(Boolean) : []"
                                    placeholder="Select Algorithm"
                                    :searchable="true"
                                    :close-on-select="true"
                                    :clear-on-select="false"
                                ></vue-multiselect>
                            </div>
                            <div class="algorithm-parameters" v-if="currentAlgorithmName">
                                <algorithm-parameters
                                    type="component"
                                    :algorithm-attributes="algorithmAttributes ? algorithmAttributes : []"
                                    :parameters="parameters ? parameters : []"
                                    height="95%"
                                ></algorithm-parameters>
                            </div>
                            <div class="action-wrapper">
                                <div class="action">
                                    <base-button-rectangle
                                        width="100%"
                                        @state-changed="$refs.importAlgorithm.click()"
                                    >
                                        <div class="button-container">
                                            <div class="button-icon">
                                                <v-icon name="fa-file-upload" scale="1.5"/>
                                            </div>
                                            <div class="button-text">Load</div>
                                        </div>
                                    </base-button-rectangle>
                                    <input
                                        type="file"
                                        ref="importAlgorithm"
                                        style="display:none"
                                        name="file-import-algorithm"
                                        id="fileImportAlgorithm"
                                        accept=".json"
                                        :disabled="false"
                                        @change="onFileSelected"
                                    />
                                </div>
                                <div class="action">
                                    <base-button-rectangle
                                        width="100%"
                                        @state-changed="downloadCurrentAlgorithm"
                                    >
                                        <div class="button-container">
                                            <div class="button-icon">
                                                <v-icon name="fa-file-download" scale="1.5"/>
                                            </div>
                                            <div class="button-text">Save</div>
                                        </div>
                                    </base-button-rectangle>
                                </div>
                            </div>
                        </div>
                    </base-tab>
                </base-tabs-wrapper>
        </div>
    </div>
</template>

<script>
import { ref, watch } from 'vue';

import VueMultiselect from 'vue-multiselect';

import AlgorithmParameters from './AlgorithmParameters.vue';

export default {
    components: {
        VueMultiselect,
        AlgorithmParameters
    },

    emits: ['reference-changed', 'algorithm-changed', 'import-path-changed', 'download-algorithm', 'single-run', 'live-process', 'single-run-reference', 'live-process-reference', 'tab-changed'],

    props: {
        algorithms: { 
            type: Array, 
            default: () => [] 
        },
        referenceAlgorithms: { 
            type: Array, 
            default: () => [] 
        },
        currentAlgorithm: { 
            type: Object, 
            default: () => null 
        },
        algorithmAttributes: { 
            type: Array, 
            default: () => [] 
        },
        parameters: { 
            type: Array, 
            default: () => [] 
        },
        currentReferenceAlgorithm: { 
            type: Object, 
            default: () => null 
        },
        referenceAlgorithmAttributes: { 
            type: Array, 
            default: () => [] 
        },
        referenceParameters: { 
            type: Array, 
            default: () => [] 
        },
        width: { 
            type: String, 
            default: '100%' 
        },
        height: { 
            type: String, 
            default: '100%' 
        },
        disableActions: { 
            type: Boolean, 
            default: false 
        }
    },

    setup(_, context){
        const tabs = ref(['References', 'Detections']);
        const currentTab = ref(tabs.value[0]);

        function tabChanged(value) {
            currentTab.value = value;
            context.emit('tab-changed',value);
        }

        const currentReferenceName = ref(null);
        const currentAlgorithmName = ref(null);

        watch(currentReferenceName, (newValue) => {
            context.emit('reference-changed', newValue);
        });

        watch(currentAlgorithmName, (newValue) => {
            console.log('AlgorithmDebugControl: currentAlgorithmName changed to:', newValue);
            context.emit('algorithm-changed', newValue);
        });

        function onFileSelected(event) {
            context.emit('import-path-changed', event.target.files[0]);
        }

        function singleRun(){
            context.emit("single-run");
        }

        function liveProcess(state) {
            context.emit("live-process", state);
        }

        function singleRunReference() {
            context.emit("single-run-reference");
        }

        function liveProcessReference(state) {
            context.emit("live-process-reference", state);
        }

        function downloadCurrentAlgorithm() {
            context.emit('download-algorithm');
        }

        return {
            currentReferenceName,
            currentAlgorithmName,
            tabs,
            singleRun,
            liveProcess,
            singleRunReference,
            liveProcessReference,
            onFileSelected,
            tabChanged,
            downloadCurrentAlgorithm
        }

    }
}
</script>

<style scoped>
.flex-container {
    background-color: rgb(73, 69, 69);
    width: 100%;
    height: 100%;
}

.list-container {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 100%;
}

.action-container {
    display: flex;
    justify-content: flex-start;
    align-items: flex-start;
    width: 100%;
    height: 100%;
}

.tabs-wrapper {
    width: 100%;
    height: 100%;
}

.tab-wrapper {
    display: flex;
    flex-direction: column;
    height: 100%;
}

.reference-tab {
    display: flex;
    flex-direction: column;
}

.action-wrapper {
    display: flex;
    flex-direction: row;
    height: 10%;
    margin-top: 1%;
}

.action {
    width: 50%;
    height: 100%;
    margin-right: 5px;
}

.button-container {
    display: flex;
    width: 100%;
    height: 100%;
    padding: 4px;
    justify-content: center;
    align-items: center;
}

.button-icon {
    height: 100%;
    display: flex;
    align-items: center;
}

.button-text {
    height: 100%;
    display: flex;
    align-items: center;
    font-size: medium;
}

.algorithm-list {
    width: 100%;
    margin-bottom: 1%;
    margin-top: 2%;
    height: 10%;
}

.algorithm-parameters {
    height: 55%;
}
</style>