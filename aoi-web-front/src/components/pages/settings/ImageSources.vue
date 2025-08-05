<template>
    <div class="flex-container">
        <div class="list-wrapper">
            <image-sources-list
                :sources="sources"
                @load-current-image-source="loadCurrentImageSource"
                @delete-source="deleteSource"
            ></image-sources-list>
        </div>
        <div class="camera-view">
            <div class="results-vis">
                <div class="camera-wrapper">
                    <a href="#" id="downloader" @click="download()">Download!</a>
                    <div class="camera-scene-item">
                        <camera-scene
                            width="100%"
                            height="100%"
                            :show="showCamera"
                            :camera-feed="cameraFeed"
                            :feed-location="feedLocation"
                            :static-images="[]"
                            :id="1"
                            canvas-id="canvas"
                            :graphics="[]"
                            :image-file-name="imageFileName"
                        ></camera-scene>
                    </div>
                </div>
            </div>
            <div class="settings-container">
                <image-source-settings
                    :type="currentSourceType"
                    :current-image-source="currentImageSource"
                    :current-image-generator="currentImageGenerator"
                    @generator-updated="imageGeneratorChanged"
                    @camera-updated="cameraChanged"
                    @camera-settings-updated="cameraSettingsChanged"
                    @fps-updated="fpsChanged"
                    @save-photo="savePhoto"
                    @show-camera="changeCameraStatus"
                    @save-src-status="onSaveSrcStatus"
                    @save-settings-status="onSaveSettingsStatus"
                ></image-source-settings>
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
                    <v-icon :name="notificationIcon" scale="2.5" animation="pulse"/>
                </div>
                <div class="text-wrapper">
                    {{ notificationMessage }}
                </div>
            </div>
        </base-notification>
    </div>
</template>

<script>
import { computed, onMounted, onUnmounted, ref, toRef, watch } from 'vue';
import { useStore } from 'vuex';
import { ipAddress, port } from '../../../url.js';
import useNotification from '../../../hooks/notifications.js';

import ImageSourcesList from '../../image_sources/ImageSourcesList.vue';
import ImageSourceSettings from '../../image_sources/ImageSourceSettings.vue';
import CameraScene from '../../camera/CameraScene.vue';


export default{
    components: {
        ImageSourcesList,
        ImageSourceSettings,
        CameraScene
    },
    setup(){
        const currentSourceId = ref('');
        const currentSourceType = ref('');

        const error = ref('');

        const store = useStore();

        const {showNotification, notificationMessage, notificationIcon, notificationTimeout, 
            setNotification, clearNotification} = useNotification();

        const feedLocation = ref('');

        const showCamera = ref(false);
        const cameraFeed = ref(true);

        const imageFileName = ref(null);

        const currentConfiguration = computed(function() {
            return store.getters["configurations/getCurrentConfiguration"];
        });

        const currentImageSource = computed(function() {
            return store.getters["imageSources/getCurrentImageSource"];
        });

        const currentImageGenerator = computed(function() {
            return store.getters["imageSources/getCurrentImageGenerator"];
        });

        const imageGeneratorsList = computed(function() {
            return store.getters["imageSources/getImageGenerators"];
        });

        const sources = computed(function() {
            const s = store.getters["imageSources/getImageSources"];
            return s;
        });

        function fpsChanged(newFps){
            store.dispatch("imageSources/setCurrentImageSourceProp", {
                key: "fps",
                value: newFps
            });

            if(newFps != null && newFps != 0){
                if( currentImageSource.value.imageSourceType === "static"){
                    feedLocation.value = `ws://${ipAddress}:${port}/image_source/` + currentImageSource.value.uid + '/' +  currentImageSource.value.imageGeneratorUid + '/' + String(newFps) + `/ws`;
                }else if( currentImageSource.value.imageSourceType === "dynamic"){
                    feedLocation.value = `ws://${ipAddress}:${port}/image_source/` + currentImageSource.value.uid + '/' +  currentImageSource.value.cameraUid + '/' + String(newFps) + `/ws`;
                }
            }
        }
        
        function savePhoto(){
            document.getElementById('downloader').click();
        }

        function download(){
            const currentDate = new Date();

            const imageName = currentDate.getDate() + "_" + (currentDate.getMonth() + 1) + "_"
                + currentDate.getFullYear() + "_" + currentDate.getHours() + "_"
                + currentDate.getMinutes() + "_" + currentDate.getSeconds() + ".png";
            // const imageName = currentImageSource.value.name + "screenshot.png";
            // document.getElementById("downloader").download = imageName;
            // document.getElementById("downloader").href = document.getElementById("canvas").toDataURL("image/png").replace(/^data:image\/[^;]/, 'data:application/octet-stream');
            imageFileName.value = imageName;
        }

        async function loadCurrentImageSource(id) {
            try{
                if(id)
                {
                    await store.dispatch("imageSources/loadCurrentImageSource", {
                        uid: id
                    });

                    const gen = store.getters["imageSources/getImageGeneratorById"](currentImageSource.value.imageGeneratorUid);
                    store.dispatch("imageSources/setCurrentImageGenerator", gen);

                    currentSourceId.value = currentImageSource.value.uid;
                    currentSourceType.value = currentImageSource.value.imageSourceType;

                    if(currentImageSource.value.imageSourceType === "static"){
                        feedLocation.value = `ws://${ipAddress}:${port}/image_source/` + currentSourceId.value + '/' +  currentImageSource.value.imageGeneratorUid + '/' + currentImageSource.value.fps + `/ws`;
                    }else if( currentImageSource.value.imageSourceType === "dynamic"){
                        feedLocation.value = `ws://${ipAddress}:${port}/image_source/` + currentSourceId.value + '/' +  currentImageSource.value.cameraUid + '/' + currentImageSource.value.fps + `/ws`;
                    }
                }
                else
                {
                    showCamera.value = false;

                    store.dispatch("imageSources/setCurrentImageSource", null);
                    store.dispatch("imageSources/setCurrentImageGenerator", null);
                }
            }
            catch(err) {
                error.value = err.message || 'Something failed!';
            }
        }

        function deleteSource(source) {
            if(currentImageSource.value.uid === source.uid)
            {
                store.dispatch("imageSources/setCurrentImageSource", null);
            }

            store.dispatch("imageSources/removeImageSource", source);
        }

        function changeCameraStatus(value) {
            showCamera.value = value;
            cameraFeed.value = value;
        }

        function cameraChanged(camera){
            store.dispatch("imageSources/setCurrentImageSourceProp", {
                key: "cameraUid",
                value: camera
            });
            feedLocation.value = `ws://${ipAddress}:${port}/image_source/` + currentImageSource.value.uid + '/' + camera + '/' + currentImageSource.value.fps + `/ws`;
        }

        async function imageGeneratorChanged(uid){
            store.dispatch("imageSources/setCurrentImageSourceProp", {
                key: "imageGeneratorUid",
                value: uid
            });

            feedLocation.value = `ws://${ipAddress}:${port}/image_source/` + currentImageSource.value.uid + `/` + currentImageSource.value.imageGeneratorUid + `/` + currentImageSource.value.fps + `/ws`;
        }

        function cameraSettingsChanged(uid){
            store.dispatch("imageSources/setCurrentImageSourceProp", {
                key: "cameraSettingsUid",
                value: uid
            });
        }

        function onSaveSrcStatus(status){
            if(status){
                setNotification(3000, "Source saved successfully!", 'fc-ok');
            }else{
                setNotification(3000, "Failed to save source!", 'bi-exclamation-circle-fill');
            }
        }

        function onSaveSettingsStatus(status){
            if(status){
                setNotification(3000, "Settings saved successfully!", 'fc-ok');
            }else{
                setNotification(3000, "Failed to save settings!", 'bi-exclamation-circle-fill');
            }
        }

        onUnmounted(() => {
            try {
                showCamera.value = false;

                store.dispatch("imageSources/setCurrentImageSource", null);
                store.dispatch("imageSources/setCurrentImageGenerator", null);
            } catch (error) {
                console.warn('Error during ImageSources component unmounting:', error);
            }
        });
        
        return{
            currentImageSource,
            currentSourceId,
            currentSourceType,
            currentImageGenerator,
            error,
            sources,
            feedLocation,
            showCamera,
            currentConfiguration,
            cameraFeed,
            imageGeneratorsList,
            imageFileName,
            showNotification,
            notificationMessage,
            notificationIcon,
            notificationTimeout,
            changeCameraStatus,
            loadCurrentImageSource,
            deleteSource,
            imageGeneratorChanged,
            cameraChanged,
            cameraSettingsChanged,
            savePhoto,
            download,
            fpsChanged,
            clearNotification,
            onSaveSrcStatus,
            onSaveSettingsStatus
        }
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

h1{
    color:white;
}

.main-container{
    width:100%;
    height:100%;
    display:flex;
    position:relative;
}

.list-container {
    width: 15%;
    height: 97%;
}

.camera-view{
    background-color: inherit;
    width:100%;
    height:100%;
    border-radius:20px;
    display:flex;
    align-items: center;
}

.settings-container {
    width: 39%;
    height: 80vh;
    margin-right: 1%;
}

p{
    background-color: rgb(37, 36, 36);
    color:rgba(204, 161, 82);
    border-top-right-radius:20px;
    border-top-left-radius:20px;
}

.results-vis{
    display: flex;
    flex-direction: column;
    width: 60%;
    height: 100%;
    /* background-color: red; */
}

.camera-wrapper{
    display: flex;
    width: 100%;
    height: 100%;
    justify-content: center;

}

.camera-scene-item {
    margin-right: 1%;
    height: 100%;
    width: 98%;
}

#downloader{
    position:absolute;
    visibility:hidden;
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