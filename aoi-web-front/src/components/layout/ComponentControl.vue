<template>
    <div class="control-wrapper">
        <div class="actions-control">
            <div class="action">
                <base-button-rectangle
                    width="5.5vw"
                    :active="cameraActive"
                    @state-changed="toggleCamera"
                    :disabled="!currentComponent || imageSourceUid === ''"
                >
                    <div class="button-container">
                        <div class="button-icon">
                            <v-icon name="bi-camera-video-fill" scale="1.5"/>
                        </div>
                        <div class="button-text">Camera</div>
                    </div>
                </base-button-rectangle>
            </div>
            <div class="action">
                <base-button-rectangle
                    width="5.5vw"
                    @state-changed="singleRun"
                    :disabled="!currentComponent || imageSourceUid === ''"
                >
                    <div class="button-container">
                        <div class="button-icon">
                            <v-icon name="md-repeatone-outlined" scale="1.5"/>
                        </div>
                        <div class="button-text">Single</div>
                    </div>
                </base-button-rectangle>
            </div>
            <div class="action">
                <base-button-rectangle
                    width="5.5vw"
                    @state-changed="liveProcess"
                    :disabled="!currentComponent || imageSourceUid === ''"
                >
                    <div class="button-container">
                        <div class="button-icon">
                            <v-icon name="si-kdenlive" scale="1.5"/>
                        </div>
                        <div class="button-text">{{ liveRunningBtnText }}</div>
                    </div>
                </base-button-rectangle>
            </div>
            <div class="action">
                <base-button-rectangle
                    width="5.5vw"
                    @state-changed="saveComponent"
                    :disabled="!currentComponent"
                >
                    <div class="button-container">
                        <div class="button-icon">
                            <v-icon name="ri-save-3-fill" scale="1.5"/>
                        </div>
                        <div class="button-text">Save</div>
                    </div>
                </base-button-rectangle>
            </div>
            <div class="action">
                <base-button-rectangle
                    @state-changed="$refs.importAlgorithm.click()"
                    width="5.5vw"
                    :disabled="!currentComponent"
                >
                    <div class="button-container">
                        <div class="button-icon">
                            <v-icon name="fa-file-import" scale="1.5"/>
                        </div>
                        <div class="button-text">Import</div>
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
                    @state-changed="downloadCurrentAlgorithm"
                    width="5.5vw"
                    :disabled="!currentComponent"
                >
                    <div class="button-container">
                        <div class="button-icon">
                            <v-icon name="fa-file-export" scale="1.5"/>
                        </div>
                        <div class="button-text">Export</div>
                    </div>
                </base-button-rectangle>
            </div>
        </div>
        <div class="drop-below" @click="updateSelectedSection('General')">
            General
        </div>
        <div class="general" v-show="selectedSection === 'General'">
            <div class="form-control" v-if="currentComponent">
                <label for="component">Name:</label>
                <input type="text" name="component" id="component" v-model.trim.lazy="componentName">
            </div>
            <div class="form-control" v-if="currentComponent">
                <label for="image-source">Image Source:</label>
                <select v-model="imageSourceUid" style="border: none;">
                    <option v-for="imageSource in imageSources"
                        :key="imageSource.uid"
                        :value="imageSource.uid">
                    {{ imageSource.name }}
                    </option>
                </select>
            </div>
            <div class="form-control" v-if="currentComponent">
                <label for="component">Algorithm:</label>
                <select v-model="algorithmTypeUid" style="border: none;">
                    <option v-for="algorithm in availableAlgorithms"
                    :key="algorithm.uid"
                    :value="algorithm.uid">
                        {{ algorithm.type }}
                    </option>
                </select>
            </div>
            <div class="form-control" v-if="currentComponent && (type === 'component' || type === 'identification')">
                <label for="component">Reference:</label>
                <select v-model="currentReferenceUid" style="border: none;">
                    <option
                        v-for="(reference, index) in (references || [])"
                        :key="reference?.uid || `ref-${index}`"
                        :value="reference?.uid"
                    >{{ reference?.name || 'Unnamed Reference' }}</option>
                </select>
            </div>
        </div>
        <div class="drop-below" @click="updateSelectedSection('Parameters')">
            Parameters
        </div>
        <div v-show="selectedSection === 'Parameters'">
            <div class="parameters" v-if="currentComponent">
                <algorithm-parameters
                        :type="type"
                        :algorithm-idx="algorithmTypeUid"
                        :algorithm-attributes="algorithmAttributes ? algorithmAttributes : []"
                        :parameters="algorithmParameters ? algorithmParameters : []"
                        height="55vh"
                    ></algorithm-parameters>
                    <div v-if="showSaveRef" class="save-ref">
                        <div class="form-control">
                            <label for="save-reference">Save Reference Point:</label>
                            <base-checkbox 
                            :current="false"
                            name="saveRef"
                            @update-value="saveRefChanged"
                            ></base-checkbox>
                        </div>
                    </div>
            </div>
        </div>
        <div v-if="componentLoading" class="loading-spinner">
            <base-spinner></base-spinner>
        </div>
    </div>
</template>

<script>
import { ref, computed, watch, toRef } from 'vue';
import { useImageSourcesStore } from '@/composables/useStore';

import AlgorithmParameters from '../layout/AlgorithmParameters.vue';

export default {
    components: {
        AlgorithmParameters
    },

    props: ['type', 'currentComponent', 'availableAlgorithms', 'algorithmAttributes', 'algorithmParameters', 'algorithmId', 'references', 'componentLoading'],

    emits: ['show-camera', 'single-run', 'live-process', 'update-image-source', 'update-reference', 'algorithm-changed', 'import-path-changed', 'save-component', 'download-algorithm', 'save-ref-changed'],

    setup(props, context) {
        // Use centralized composables instead of direct store access
        const { imageSources } = useImageSourcesStore();

        // Debug: Log availableAlgorithms prop changes
        watch(() => props.availableAlgorithms, (newValue) => {
            console.log('ComponentControl - availableAlgorithms changed:', {
                length: newValue?.length || 0,
                algorithms: newValue
            });
        }, { immediate: true });

        const selectedSection = ref(null);

        const componentName = ref(props.currentComponent ? props.currentComponent.name : "");
        const imageSourceUid = ref(props.currentComponent ? props.currentComponent.imageSourceUid : "");

        const algorithmId = toRef(props, 'algorithmId');
        const algorithmTypeUid = ref(algorithmId.value);

        const currentReferenceUid = ref(props.currentComponent ? props.currentComponent.referenceUid : "");

        const importFilePath = ref("");

        const currentComponent = toRef(props, 'currentComponent');

        const showSaveRef = computed(function() {
            return props.type === 'reference';
        });

        watch(algorithmId, (newValue) => {
            algorithmTypeUid.value = newValue;
        });

        watch(currentComponent, (newValue) => {
            componentName.value = newValue.name;
            imageSourceUid.value = newValue.imageSourceUid;
            currentReferenceUid.value = newValue.referenceUid;
        });

        const cameraActive = ref(false);

        const liveRunningBtnText = ref('Live');

        function toggleCamera(value) {
            cameraActive.value = value
            context.emit('show-camera', cameraActive.value);
        }

        function singleRun() {
            context.emit('single-run', imageSourceUid.value);
        }

        function liveProcess(state) {
            if(state) {
                liveRunningBtnText.value = 'Stop';
            } else {
                liveRunningBtnText.value = 'Live';
            }

            context.emit('live-process', state);
        }

        function saveComponent() {
            context.emit('save-component', {
                name: componentName.value,
                imageSourceUid: imageSourceUid.value
            });
        }

        watch(imageSourceUid, () => {
            context.emit('update-image-source', imageSourceUid.value);
        });

        watch(currentReferenceUid, () => {
            context.emit('update-reference', currentReferenceUid.value);
        });

        watch(algorithmTypeUid, () => {
            context.emit('algorithm-changed', algorithmTypeUid.value);
        });

        function onFileSelected(event) {
            importFilePath.value = event.target.files[0];
        }

        watch(importFilePath, (newValue) => {
            context.emit('import-path-changed', newValue);
        });

        function downloadCurrentAlgorithm() {
            context.emit('download-algorithm');
        }

        function saveRefChanged(_, value)
        {
            context.emit('save-ref-changed', value);
        }

        function updateSelectedSection(value) {
            if(selectedSection.value === value) 
            {
                selectedSection.value = null;
            }
            else
            {
                selectedSection.value = value;
            }
        }
        
        return {
            componentName,
            imageSourceUid,
            currentReferenceUid,
            algorithmTypeUid,
            cameraActive,
            liveRunningBtnText,
            imageSources,
            showSaveRef,
            selectedSection,
            toggleCamera,
            singleRun,
            liveProcess,
            saveComponent,
            onFileSelected,
            downloadCurrentAlgorithm,
            saveRefChanged,
            updateSelectedSection
        };
    }
}
</script>

<style scoped>
.control-wrapper {
    display: flex;
    flex-direction: column;;
    background-color: rgb(34, 31, 31);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.26);
    width: 18vw;
    height: 90vh;
}

.actions-control {
    display: flex;
    flex-wrap: wrap;
    height: 15%;
    margin-bottom: 1%;
    margin-top: 1%;
    align-self: center;
    justify-content: center;
    /* margin-right: auto; */
}

.action {
    margin: 2px;
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
    width: 30%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
}

.button-text {
    width: 70%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 80%;
}

.form-control {
    margin-top: 5px;
    background-color: inherit;
    border: none;
    color: inherit;
    display: flex;
    justify-content: space-between;
}

.drop-below {
    background-color: #ffffff;
    margin-bottom: 3px;
    height: 5vh;
    display: flex;
    justify-content: center;
    align-items: center;
    border-radius: 5px;
    color: rgb(204, 161, 82);
    font-weight: bold;
}

.drop-below:hover {
    cursor: pointer;
}

.parameters {
    margin-top: 10px;
}

label {
    font-size: 80%;
}

select {
    width: 10vw;
    background-color: rgb(204, 161, 82);
    padding-left: 0.2vw;
    padding-right: 0.2vw;
    margin: 0;
}

input {
    width: 10vw;
    background-color: inherit;
    border: none;
}

.loading-spinner {
    align-self: center;
    margin: auto;
}

</style>