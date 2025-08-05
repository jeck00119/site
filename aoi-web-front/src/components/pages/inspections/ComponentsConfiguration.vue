<template>
    <div class="flex-container">
        <div class="list-wrapper">
            <components-list width="100%" height="100%" :components="components" :retrieving="componentsRetrieving"
                :disable="!currentConfiguration" @load-component="loadComponent" @remove-component="remove"
                @save-component="addComponent"></components-list>
        </div>
        <div class="control-camera-container">
            <div class="results-vis">
                <div class="camera-wrapper">
                    <div class="camera-scene-item">
                        <camera-scene width="100%" height="100%" :show="showCamera" :camera-feed="true"
                            :feed-location="feedLocation" :static-images="[]" :id="1" canvas-id="camera-scene-canvas"
                            :graphics="currentGraphics" @graphics-changed="updateGraphics" @graphic-selected="selectionChanged"
                            @graphic-cleared="selectionCleared" @graphic-modified="selectionModified"></camera-scene>
                    </div>
                    <div class="camera-scene-item">
                        <camera-scene width="100%" height="100%" :camera-feed="false" :static-images="outputImages" :id="2"
                            canvas-id="result-canvas" :graphics="[]"></camera-scene>
                    </div>
                </div>
            </div>
            <div class="control">
                <component-control :type="moduleName" :current-component="currentComponent"
                    :algorithm-attributes="algorithmAttributes" :algorithm-parameters="parameters"
                    :availableAlgorithms="algorithms" :algorithm-id="algorithmTypeId" :references="references"
                    :component-loading="componentLoading" @show-camera="changeCameraStatus" @single-run="singleRunAlgorithm"
                    @live-process="liveProcessAlgorithm" @update-image-source="updateImageSource"
                    @update-reference="updateReference" @algorithm-changed="onAlgorithmChanged"
                    @import-path-changed="onImportPathChanged" @save-component="saveComponent"
                    @download-algorithm="downloadAlgorithm"></component-control>
            </div>
        </div>
        <button class="rounded-button" @click="showMasks = true" v-if="!showMasks"
            :disabled="!currentComponent">ROI</button>
        <div class="roi-masks" v-else>
            <mask-scene :graphics="selectedGraphic" :image-source-id="currentImageSourceId" canvas-id="mask-scene"
                width="100%" height="100%" @closed="showMasks = false" @save="saveMasks"></mask-scene>
        </div>
        <div class="results-btn-container" v-if="!showResults">
            <button class="action-button" @click="showResults = true" :disabled="!data">
                <div class="button-container">
                    <div class="button-icon">
                        <v-icon name="vi-file-type-light-json" scale="1"/>
                    </div>
                </div>
            </button>
        </div>
        <div class="results-container" v-else>
            <json-data-container width="auto" height="29vh" :data="data" @closed="showResults = false"></json-data-container>
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
    </div>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue';
import { useStore } from 'vuex';
import { uuid } from "vue3-uuid";

import graphic from '../../../utils/graphics.js';

import ComponentsList from '../../layout/ComponentsList.vue';
import ComponentControl from '../../layout/ComponentControl.vue';
import CameraScene from '../../camera/CameraScene.vue';
import AlgorithmResultTable from '../../layout/AlgorithmResultTable.vue';
import MaskScene from '../../layout/MaskScene.vue';
import JsonDataContainer from '../../layout/JsonDataRenderer.vue';
import { ipAddress, port } from '../../../url';
import useAlgorithms from '../../../hooks/algorithms.js';
import useComponents from '../../../hooks/components.js';
import useGraphics from '../../../hooks/graphics.js';
import useNotification from '../../../hooks/notifications';

export default {
    components: {
        ComponentsList,
        ComponentControl,
        CameraScene,
        AlgorithmResultTable,
        MaskScene,
        JsonDataContainer
    },

    setup() {
        const moduleName = 'component';

        const showMasks = ref(false);
        const showCamera = ref(false);
        const showResults = ref(false);

        const feedLocation = ref('');
        const currentImageSourceId = ref('');
        const currentReferenceId = ref('');

        const {showNotification, notificationMessage, notificationIcon, notificationTimeout, 
            setNotification, clearNotification} = useNotification();

        const store = useStore();

        const { selectedGraphic, graphicsObject, currentGraphics, graphicItems,
            canvas, updateGraphics, selectionChanged, selectionCleared, selectionModified,
            saveMasks } = useGraphics();

        const { currentComponent, componentLoading, componentsRetrieving, components, load,
            remove, update, add } = useComponents(moduleName);

        const algorithmUid = computed(function () {
            return currentComponent.value?.algorithmUid;
        });

        const { algorithmTypeId, algorithms, currentAlgorithm, algorithmAttributes, parameters,
            resultImage, outputImages, data, currentAlgorithmInitial, setAlgorithmConfigured, loadUIandAlgorithm, onAlgorithmChanged,
            onImportPathChanged, download, saveAlgorithm, singleRunAlgorithm,
            liveProcessAlgorithm, _, _2 } = useAlgorithms(algorithmUid, currentReferenceId, currentImageSourceId, moduleName, graphicsObject, ipAddress, port);

        const currentConfiguration = computed(function () {
            return store.getters["configurations/getCurrentConfiguration"];
        });

        const currentUser = computed(function () {
            return store.getters["auth/getCurrentUser"];
        });

        const references = computed(function () {
            return store.getters["components/getReferences"]
        });

        async function loadComponent(id) {
            try {
                if(id)
                {
                    await load(id);

                    currentReferenceId.value = currentComponent.value.referenceUid;

                    if (currentComponent.value.algorithmUid) {
                        setAlgorithmConfigured();
                    }

                    const algorithm = store.getters["algorithms/getAlgorithmByType"](currentComponent.value.algorithmType);

                    if (algorithm) {
                        if (algorithmTypeId.value === algorithm.uid) {
                            loadUIandAlgorithm(algorithm.type, currentComponent.value.algorithmUid);
                        }
                        else {
                            algorithmTypeId.value = algorithm.uid;
                        }
                    }
                    else {
                        algorithmTypeId.value = '';
                    }
                }
                else
                {
                    store.dispatch("algorithms/setCurrentAlgorithm", null);
                    store.dispatch("algorithms/setCurrentAlgorithmAttributes", []);
                    store.dispatch("algorithms/setAlgorithmResult", null);
                    store.dispatch("components/setCurrentComponent", null);
                    store.dispatch("graphics/resetGraphicsItems");

                    showCamera.value = false;
                }
            }catch(err) {
                setNotification(3000, "Error while trying to load component.", 'bi-exclamation-circle-fill');
            }
            
        }

        function addComponent(name) {
            try {
                add(name);

                store.dispatch("log/addEvent", {
                    type: moduleName.toUpperCase(),
                    user: currentUser.value ? currentUser.value.username : "Unknown",
                    title: moduleName.toUpperCase() + ' Added',
                    description: `New ` + moduleName + ` added: ${name}`
                });
            }catch(err) {
                setNotification(3000, err, 'bi-exclamation-circle-fill');
            }
        }

        function changeCameraStatus(value) {
            showCamera.value = value;
        }

        function updateImageSource(imageSourceId) {
            currentImageSourceId.value = imageSourceId;
            feedLocation.value = `ws://${ipAddress}:${port}/image_source/${imageSourceId}/ws`;
        }

        function updateReference(referenceId) {
            currentReferenceId.value = referenceId;
        }

        function downloadAlgorithm() {
            download(currentAlgorithm.value);
        }

        function saveComponent(payload) {
            const data = graphic.getGraphicsProps(graphicItems.value, canvas.value);

            store.dispatch("algorithms/updateCurrentAlgorithmGraphics", data);

            const component = {
                uid: currentComponent.value.uid,
                name: payload.name,
                imageSourceUid: payload.imageSourceUid,
                algorithmUid: currentAlgorithm.value.uid,
                algorithmType: currentAlgorithm.value.type,
                referenceUid: currentReferenceId.value
            };

            update(component).then(
                () => {
                    saveAlgorithm().then(
                        () => {
                            store.dispatch("log/addEvent", {
                                type: moduleName.toUpperCase(),
                                user: currentUser.value ? currentUser.value.username : "Unknown",
                                title: moduleName.toUpperCase() + ' Modified',
                                description: `${currentComponent.value.name} was modified.`,
                                details: [currentComponent.value, component, currentAlgorithmInitial.value, currentAlgorithm.value.parameters]
                            });

                            setNotification(3000, "Configuration saved.", 'fc-ok');
                        }
                    ).catch(err => {
                        setNotification(3000, "Error while trying to save component.", 'bi-exclamation-circle-fill');
                    });
                }
            ).catch(err => {
                setNotification(3000, "Error while trying to save component.", 'bi-exclamation-circle-fill');
            });
        }

        onMounted(() => {
            if (currentConfiguration.value) {
                componentsRetrieving.value = true;

                store.dispatch("components/loadComponents", {
                    type: moduleName
                });

                store.dispatch("components/loadComponents", {
                    type: 'reference'
                });
            }
        });

        onBeforeUnmount(() => {
            store.dispatch("algorithms/setCurrentAlgorithm", null);
            store.dispatch("algorithms/setCurrentAlgorithmAttributes", []);
            store.dispatch("algorithms/setAlgorithmResult", null);
            store.dispatch("components/setComponents", []);
            store.dispatch("components/setReferences", []);
            store.dispatch("components/setCurrentComponent", null);
            store.dispatch("graphics/resetGraphicsItems");
        });

        return {
            moduleName,
            components,
            references,
            algorithms,
            currentImageSourceId,
            currentComponent,
            currentAlgorithm,
            algorithmAttributes,
            parameters,
            currentGraphics,
            showCamera,
            resultImage,
            outputImages,
            feedLocation,
            data,
            componentLoading,
            componentsRetrieving,
            algorithmTypeId,
            currentConfiguration,
            selectedGraphic,
            showMasks,
            showResults,
            showNotification,
            notificationIcon,
            notificationMessage,
            notificationTimeout,
            updateGraphics,
            loadComponent,
            remove,
            addComponent,
            changeCameraStatus,
            singleRunAlgorithm,
            liveProcessAlgorithm,
            updateImageSource,
            updateReference,
            onAlgorithmChanged,
            onImportPathChanged,
            saveComponent,
            downloadAlgorithm,
            selectionChanged,
            selectionCleared,
            selectionModified,
            saveMasks,
            clearNotification
        };
    }
}
</script>

<style scoped>
.flex-container {
    display: flex;
    flex-direction: column;
    width: 100%;
    height: 95%;
    color: white;
    margin: 0;
}

.list-wrapper {
    margin: 1%;
    height: 9%;
}

.control-camera-container {
    display: flex;
    height: 90%;
}

.results-vis {
    display: flex;
    flex-direction: column;
    width: 100%;
    height: 100%;
}

.control {
    display: flex;
    flex-direction: column;
}

.results-table-wrapper {
    width: 98%;
    margin: 0% 1%;
}

.camera-wrapper {
    display: flex;
    height: 100%;
}

.camera-scene-item {
    margin-right: 1%;
    height: 100%;
    width: 98%;
}

.rounded-button {
    border-radius: 0 10px 10px 0;
    background-color: rgb(204, 161, 82);
    border: none;
    color: white;
    padding: 10px 20px;
    position: absolute;
    width: 5vw;
    top: 55%;
    left: 0%;
}

button:disabled,
button[disabled] {
    border: 1px solid #999999;
    background-color: #cccccc;
    color: #666666;
    cursor: not-allowed;
}

.action-button {
    width: 100%;
    height: 100%;
    background-color: rgb(0, 0, 0);
    border: none;
    /* padding: 5% 35%; */
    border-radius: inherit;
    margin-right: 2%;
}

.button-container {
    display: flex;
    width: 100%;
    height: 100%;
    justify-content: center;
    align-items: center;
    color: rgb(204, 161, 82);
}

.button-icon {
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
}

.roi-masks {
    position: absolute;
    top: 55%;
    left: 0;
    width: 30vw;
    height: 35%;
    z-index: 20;
    background-color: rgb(0, 0, 0);
}

.results-btn-container {
    position: absolute;
    top: 88%;
    left: 95%;
    width: 4%;
    height: 4%;
    z-index: 20;
    background-color: rgb(0, 0, 0);
    border-radius: 5px;
}

.results-container {
    position: absolute;
    top: 55%;
    left: 70vw;
    width: 30vw;
    height: 35%;
    z-index: 20;
    background-color: rgb(21, 20, 20);
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

</style>