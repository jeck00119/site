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
                    :type="debugCurrentSourceType"
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
import { computed, nextTick, onMounted, onUnmounted, ref, toRef, watch } from 'vue';
import { useImageSourcesStore, useConfigurationsStore } from '@/composables/useStore';
import { ipAddress, port } from '../../../url.js';
import useNotification, { NotificationType } from '../../../hooks/notifications';
import { GeneralMessages } from '@/constants/notifications';
import { logger } from '@/utils/logger';

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

        const imageSourcesStore = useImageSourcesStore();
        const configurationsStore = useConfigurationsStore();

        const {showNotification, notificationMessage, notificationIcon, notificationTimeout, notificationType,
            setTypedNotification, clearNotification} = useNotification();

        const feedLocation = ref('');

        const showCamera = ref(false);
        const cameraFeed = ref(true);

        const imageFileName = ref(null);

        // These are already computed refs from the composables


        const currentConfiguration = configurationsStore.currentConfiguration;

        const currentImageSource = imageSourcesStore.currentImageSource;

        const currentImageGenerator = imageSourcesStore.currentImageGenerator;

        const imageGeneratorsList = imageSourcesStore.imageGenerators;

        const sources = computed(() => {
            const result = imageSourcesStore.imageSources.value || [];
            logger.debug('ImageSources - sources computed', { result });
            return result;
        });

        // Debug reactive updates - moved after variable declarations
        watch(currentSourceType, (newValue, oldValue) => {
            logger.debug('ImageSources - currentSourceType watcher fired', { oldValue, newValue });
        }, { immediate: true });

        // Also watch currentImageSource for debugging
        watch(currentImageSource, (newValue, oldValue) => {
            logger.debug('ImageSources - currentImageSource watcher fired');
            logger.debug('ImageSources - currentImageSource changed', { oldValue });
            logger.debug('ImageSources - currentImageSource changed to', { newValue });
            if (newValue && newValue.image_source_type) {
                logger.debug('ImageSources - newValue.image_source_type:', newValue.image_source_type);
            }
        }, { immediate: true });

        // Debug computed to trace template binding
        const debugCurrentSourceType = computed(() => {
            logger.debug('ImageSources - debugCurrentSourceType computed - currentSourceType.value:', currentSourceType.value);
            return currentSourceType.value;
        });

        function fpsChanged(newFps){
            logger.debug('ImageSources - fpsChanged called with:', newFps);
            imageSourcesStore.setCurrentImageSourceProp("fps", newFps);

            if(newFps != null && newFps != 0){
                let newFeedLocation;
                if( currentImageSource.value.image_source_type === "static"){
                    newFeedLocation = `ws://${ipAddress}:${port}/image_source/` + currentImageSource.value.uid + '/' +  currentImageSource.value.image_generator_uid + '/' + String(newFps) + `/ws`;
                }else if( currentImageSource.value.image_source_type === "dynamic"){
                    newFeedLocation = `ws://${ipAddress}:${port}/image_source/` + currentImageSource.value.uid + '/' +  currentImageSource.value.camera_uid + '/' + String(newFps) + `/ws`;
                }
                
                logger.debug('ImageSources - updating feedLocation from:', feedLocation.value);
                logger.debug('ImageSources - updating feedLocation to:', newFeedLocation);
                feedLocation.value = newFeedLocation;
                logger.debug('ImageSources - feedLocation.value is now:', feedLocation.value);
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
            logger.debug('loadCurrentImageSource called with id:', id);
            try{
                if(id)
                {
                    logger.debug('Loading image source:', id);
                    await imageSourcesStore.loadCurrentImageSource(id);
                    logger.debug('Image source loaded, currentImageSource:', currentImageSource.value);
                    
                    // TEST: Add a simple log to see if we reach this point
                    logger.debug('CHECKPOINT 1: Before getImageGeneratorById');
                    logger.debug('ImageSources - image_generator_uid:', currentImageSource.value.image_generator_uid);
                    
                    // Only try to get image generator if UID is not empty
                    let gen = null;
                    if (currentImageSource.value.image_generator_uid && currentImageSource.value.image_generator_uid !== '') {
                        try {
                            gen = imageSourcesStore.getImageGeneratorById(currentImageSource.value.image_generator_uid);
                            logger.debug('ImageSources - found image generator:', gen);
                        } catch (error) {
                            logger.error('ImageSources - error getting image generator:', error);
                            gen = null;
                        }
                    } else {
                        logger.debug('ImageSources - image_generator_uid is empty, skipping');
                    }
                    imageSourcesStore.setCurrentImageGenerator(gen);

                    logger.debug('CHECKPOINT 2: Before currentSourceType assignment');
                    logger.debug('ImageSources - currentImageSource.value.image_source_type:', currentImageSource.value.image_source_type);
                    logger.debug('ImageSources - currentSourceType.value before:', currentSourceType.value);
                    
                    currentSourceId.value = currentImageSource.value.uid;
                    logger.debug('CHECKPOINT 3: After currentSourceId assignment');
                    
                    currentSourceType.value = currentImageSource.value.image_source_type;
                    logger.debug('CHECKPOINT 4: After currentSourceType assignment');
                    logger.debug('ImageSources - currentSourceType.value after:', currentSourceType.value);
                    
                    // Ensure Vue's reactivity system processes the change
                    await nextTick();
                    logger.debug('CHECKPOINT 5: After nextTick, currentSourceType.value:', currentSourceType.value);

                    if(currentImageSource.value.image_source_type === "static"){
                        feedLocation.value = `ws://${ipAddress}:${port}/image_source/` + currentSourceId.value + '/' +  currentImageSource.value.image_generator_uid + '/' + currentImageSource.value.fps + `/ws`;
                    }else if( currentImageSource.value.image_source_type === "dynamic"){
                        feedLocation.value = `ws://${ipAddress}:${port}/image_source/` + currentSourceId.value + '/' +  currentImageSource.value.camera_uid + '/' + currentImageSource.value.fps + `/ws`;
                    }
                }
                else
                {
                    showCamera.value = false;

                    imageSourcesStore.setCurrentImageSource(null);
                    imageSourcesStore.setCurrentImageGenerator(null);
                }
            }
            catch(err) {
                error.value = err.message || 'Something failed!';
            }
        }

        function deleteSource(source) {
            if(currentImageSource.value && currentImageSource.value.uid === source.uid)
            {
                imageSourcesStore.setCurrentImageSource(null);
            }
            imageSourcesStore.removeImageSource(source);
        }

        function changeCameraStatus(value) {
            showCamera.value = value;
            cameraFeed.value = value;
        }

        function cameraChanged(camera){
            imageSourcesStore.setCurrentImageSourceProp("camera_uid", camera);
            feedLocation.value = `ws://${ipAddress}:${port}/image_source/` + currentImageSource.value.uid + '/' + camera + '/' + currentImageSource.value.fps + `/ws`;
        }

        async function imageGeneratorChanged(uid){
            imageSourcesStore.setCurrentImageSourceProp("image_generator_uid", uid);

            feedLocation.value = `ws://${ipAddress}:${port}/image_source/` + currentImageSource.value.uid + `/` + currentImageSource.value.image_generator_uid + `/` + currentImageSource.value.fps + `/ws`;
        }

        function cameraSettingsChanged(uid){
            imageSourcesStore.setCurrentImageSourceProp("camera_settings_uid", uid);
        }

        function onSaveSrcStatus(status){
            if(status){
                setTypedNotification(
                    'Source saved successfully!',
                    NotificationType.SUCCESS,
                    3000
                );
            }else{
                setTypedNotification(
                    'Failed to save source!',
                    NotificationType.ERROR,
                    3000
                );
            }
        }

        function onSaveSettingsStatus(status){
            if(status){
                setTypedNotification(
                    'Settings saved successfully!',
                    NotificationType.SUCCESS,
                    3000
                );
            }else{
                setTypedNotification(
                    'Failed to save settings!',
                    NotificationType.ERROR,
                    3000
                );
            }
        }

        onMounted(async () => {
            logger.debug('ImageSources - component mounted, loading image sources');
            try {
                await imageSourcesStore.loadImageSources();
                logger.debug('ImageSources - image sources loaded');
            } catch (error) {
                logger.error('ImageSources - error loading image sources:', error);
            }
        });

        onUnmounted(() => {
            try {
                showCamera.value = false;

                imageSourcesStore.setCurrentImageSource(null);
                imageSourcesStore.setCurrentImageGenerator(null);
            } catch (error) {
                logger.warn('Error during ImageSources component unmounting:', error);
            }
        });
        
        return{
            currentImageSource,
            currentSourceId,
            currentSourceType,
            debugCurrentSourceType,
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
            notificationType,
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


</style>