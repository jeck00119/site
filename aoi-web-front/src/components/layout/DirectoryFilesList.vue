<template>
    <div class="flex-container" :style="{width: width, height: height}">
        <base-tabs-wrapper @tab-changed="sourceOfImageChanged">
            <base-tab title="Image Source">
                <div class="image-source-list-wrapper">
                    <div class="image-source-list">
                        <vue-multiselect v-model="currentImageSource" :options="imageSourcesNames" placeholder="Select Image Source"></vue-multiselect>
                    </div>
                    <div class="actions">
                        <div class="action-wrapper">
                            <base-button-rectangle
                                @state-changed="startCamera"
                                width="100%" :active="!disableStart"
                                :disabled="disableStart"
                            >
                                <div class="button-container">
                                    <div class="button-icon">
                                        <v-icon name="bi-play-circle-fill" scale="1.5"/>
                                    </div>
                                    <div class="button-text">Start</div>
                                </div>
                            </base-button-rectangle>
                        </div>
                        <div class="action-wrapper">
                            <base-button-rectangle
                                @state-changed="stopCamera"
                                width="100%" :active="!disableStop"
                                :disabled="disableStop"
                            >
                                <div class="button-container">
                                    <div class="button-icon">
                                        <v-icon name="bi-stop-fill" scale="1.5"/>
                                    </div>
                                    <div class="button-text">Stop</div>
                                </div>
                            </base-button-rectangle>
                        </div>
                    </div>
                </div>
            </base-tab>
            <base-tab title="Load Image">
                <div class="list-container" :class="{'list-container-active': fileDropperActive}">
                    <div class="file-drop-container">
                        <file-dropper @state-changed="changeState" @files-dropped="fileChanged">
                            <div class="file-drop-content">
                                <div class="icon-wrapper">
                                    <font-awesome-icon icon="image" size="8x" shake/>
                                </div>
                                <h2>{{ message }}</h2>
                            </div>
                        </file-dropper>
                    </div>
                </div>
            </base-tab>
        </base-tabs-wrapper>
    </div>
</template>

<script>
import { ref, computed, watch } from 'vue';
import { useStore } from 'vuex';

import VueMultiselect from 'vue-multiselect';

import FileDropper from './FileDropper.vue';

export default {
    components: {
        VueMultiselect,
        FileDropper
    },

    props: ['width', 'height'],

    emits: ['files-dropped', 'image-source-changed', 'start-camera', 'stop-camera', 'reset-camera-scene'],

    setup(_, context){
        const store = useStore();

        const fileDropperActive = ref(false);
        const message = ref('Drag Image Here');
        const disableStart = ref(true);
        const disableStop = ref(true);

        const currentImageSource = ref(null);

        const imageSources = computed(function() {
            return store.getters["imageSources/getImageSources"];
        });

        const imageSourcesNames = computed(function() {
            return store.getters["imageSources/getImageSources"].map(imageSource => imageSource.name);
        });

        watch(currentImageSource, (newValue) => {
            const imageSource = imageSources.value.find(imageSource => imageSource.name === newValue);

            if(newValue)
            {
                disableStart.value = false;
            }
            else
            {
                disableStart.value = true;
            }

            context.emit('image-source-changed', imageSource? imageSource.uid : null);
        });

        function changeState(state) {
            fileDropperActive.value = state;
        }

        function fileChanged(files) {
            context.emit('files-dropped', files);
        }

        function startCamera(value) {
            context.emit('start-camera');
            disableStart.value = !value;
            disableStop.value = value;
        }

        function stopCamera(value) {
            context.emit('stop-camera');
            disableStop.value = !value;
            disableStart.value = value;
        }

        function sourceOfImageChanged(value) {
            context.emit('reset-camera-scene', value);
        }

        watch(fileDropperActive, (newValue) => {
            message.value = newValue ? 'Drop It' : 'Drag Image Here'
        });

        return{
            fileDropperActive,
            message,
            currentImageSource,
            imageSources,
            imageSourcesNames,
            disableStart,
            disableStop,
            changeState,
            fileChanged,
            startCamera,
            stopCamera,
            sourceOfImageChanged
        }
    }
}
</script>

<style scoped>
.flex-container {
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: rgb(73, 69, 69);
}

.list-container {
    background-color: black;
    width: 98%;
    height: 96%;
}

.list-container-active {
    background-color: rgb(204, 161, 82);
}

.file-drop-container {
    width: 100%;
    height: 100%;
}

.file-drop-content {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 100%;
}
.icon-wrapper {
    height: 50%;
    width: 50%;
    font-size: large;
    color:rgb(73, 69, 69);
    display: flex;
    justify-content: center;
    align-items: center;
}

h2 {
    color:rgb(73, 69, 69);
}

.actions {
    display: flex;
    width: 100%;
}

.action-wrapper {
    width: 50%;
    margin-bottom: 10px;
    margin-right: 5px;
    margin-top: 10px;
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

.button-text {
    height: 100%;
    display: flex;
    align-items: center;
    font-size: medium;
}
</style>