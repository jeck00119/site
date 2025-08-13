<template>
    <div class="flex-container">
        <div class="folder-upload" @dragover.prevent @drop="handleDrop">
            <v-icon name="oi-file-directory-open-fill" scale="5" animation="ring"></v-icon>
            <p>Upload Images Directory</p>
        </div>
        <div class="images-control">
            <div class="frame-view">
                <camera-scene width="100%" height="100%" :show="false" :camera-feed="true"
                        :feed-location="''" :static-images="[currentFrame]" :id="7" canvas-id="annotation-images-canvas"
                        :graphics="[]">
                </camera-scene>
                <a class="prev" @click="prevImage()">&#10094;</a>
                <a class="next" @click="nextImage()">&#10095;</a>
            </div>
            <div class="action-control">
                <div class="images-info">
                    {{currentIdx + 1}}/{{ imageFiles?.length }}
                </div>
                <div class="image-name">
                    {{ imageFiles[currentIdx]?.fileName }}
                </div>
                <button @click="removeImage()">Remove</button>
            </div>
        </div>
        <div class="model-control">
            <div class="model-list">
                <label style="width: 100%; text-align: left; font-size: large; margin-bottom: 2%;">Model:</label>
                <vue-multiselect
                    v-model="currentModel"
                    :options="modelOptions"
                    :searchable="true"
                ></vue-multiselect>
            </div>
            <div class="model-task">
                <label style="width: 100%; text-align: left; font-size: large; margin-bottom: 2%;">Task:</label>
                <vue-multiselect
                    v-model="currentTask"
                    :options="['Detection', 'Segmentation', 'OBB']"
                    :searchable="true"
                ></vue-multiselect>
            </div>
            <div class="model-drop" @dragover.prevent @drop.prevent="handleModelDrop">
                <v-icon name="fa-file-upload" scale="5"></v-icon>
                <p>{{ uploadModelMsg }}</p>
            </div>
            <div class="action-control">
                <div v-if="showSpinner" class="fulfilling-bouncing-circle-spinner">
                    <div class="circle"></div>
                    <div class="orbit"></div>
                </div>
                <button class="annotate-btn" @click="annotateImages" :disabled="disableAnnotateButton">Auto Annotate</button>
            </div>
        </div>
    </div>
</template>
  
<script>
import { ref, watch, computed, onMounted } from 'vue';
// import { useAnnotationStore } from '../../../hooks/annotation.js';

import CameraScene from '../../camera/CameraScene.vue';
import VueMultiselect from 'vue-multiselect';

import { ipAddress, port } from '../../../url';
  
export default {
    components: {
        VueMultiselect,
        CameraScene
    },

    setup(props, context) {
        const currentModel = ref(null);
        const currentTask = ref(null);
        const imageFiles = ref([]);
        const currentIdx = ref(-1);
        const currentFrame = ref(null);
        const filenames = ref([]);
        const showSpinner = ref(false);
        const uploadModelMsg = ref("Upload Model");

        const annotationStore = useAnnotationStore();

        // These are already computed refs from the composables


        const modelOptions = annotationStore.models;

        const disableAnnotateButton = computed(() => {
            return showSpinner.value || currentModel.value === null || currentTask.value === null || imageFiles.value.length === 0;
        });

        const handleDrop = (event) => {
            event.preventDefault();

            frames.value = [];

            const items = event.dataTransfer.items;
            if (items.length === 0) return;

            const promises = [];

            // Handle directory
            for (let item of items) {
                if (item.webkitGetAsEntry && item.webkitGetAsEntry().isDirectory) {
                    const directoryEntry = item.webkitGetAsEntry();
                    promises.push(readDirectory(directoryEntry));
                }
            }

            Promise.all(promises).then(() => {
                currentIdx.value = 0; // Set currentIdx to 0 only when all files are processed
            });
        };

        function handleModelDrop(event) {
            event.preventDefault();

            const file = event.dataTransfer.files[0];

            const formData = new FormData();
            formData.append('file', file);

            uploadModelMsg.value = "Uploading Model..."

            annotationStore.uploadModel(formData).then(() => {
                uploadModelMsg.value = "Model Uploaded!";

                annotationStore.addModel(file.name);

                setTimeout(() => {
                    uploadModelMsg.value = "Upload Model";
                }, 3000);
            }).catch(() => {
                uploadModelMsg.value = "Error on Upload!";

                setTimeout(() => {
                    uploadModelMsg.value = "Upload Model";
                }, 3000);
            });
        }

        async function readDirectory(directoryEntry) {
            const reader = directoryEntry.createReader();

            return new Promise((resolve) => {
                readAllEntries(reader).then(() => resolve());
            });
        }

        async function readAllEntries(reader) {
            return new Promise(async (resolve) => { // Make the promise executor async
                const subPromises = [];
                reader.readEntries(async (entries) => { // Make the callback async
                    if (entries.length > 0) {
                        for (let entry of entries) {
                            if (entry.isFile) {
                                subPromises.push(readFile(entry));
                            } else if (entry.isDirectory) {
                                // Recursive call for sub-directories
                                subPromises.push(readDirectory(entry));
                            }
                        }
        
                        // Read more entries if there are any
                        await readAllEntries(reader);
        
                        Promise.all(subPromises).then(() => {
                            resolve(); // Resolve once all files and subdirectories are processed
                        });
                    }
                    else {
                        resolve();
                    }
                });
            });
        }

        async function readFile(fileEntry) {
            return new Promise((resolve) => {
                fileEntry.file((file) => {
                    if (file.type.startsWith("image/")) {
                        console.log("Image file dropped:", file.name);
                        // filenames.value.push(file.name);
                        imageFiles.value.push({data: fileEntry, fileName: file.name});
                        resolve();
                        // readImage(file).then(() => resolve()); // Call the method to read the image and resolve
                    } else {
                        console.log("Not an image");
                        resolve(); // Resolve immediately if it's not an image
                    }
                });
            });
        }

        function readImage(fileEntry) {
            console.log("aaaaa");
            if (currentFrame.value !== null) {
                URL.revokeObjectURL(currentFrame.value);
                currentFrame.value = null;
            }

            fileEntry.file((file) => {
                const objectURL = URL.createObjectURL(file);
                currentFrame.value = objectURL;
            });
                
                // const reader = new FileReader();
                // reader.onload = (event) => {
                //     const imageUrl = event.target.result;
                //     currentFrame.value = imageUrl;
                //     // frames.value.push(imageUrl);
                //     resolve(); // Resolve once the image is read
                // };
                // reader.readAsDataURL(file); // Read the image file as a data URL (base64 encoded)
        }

        watch(currentIdx, (newValue, _) => {
            console.log("ssssss");
            console.log(newValue);
            if (newValue < 0 || newValue >= imageFiles.value.length) {
                currentFrame.value = null;
            } else {
                readImage(imageFiles.value[newValue].data);
            }
        });

        function prevImage() {
            if (currentIdx.value > 0) {
                currentIdx.value -= 1;
            }
        }

        function nextImage() {
            if (currentIdx.value < imageFiles.value.length - 1) {
                currentIdx.value += 1;
            }
        }

        function removeImage() {
            if (currentIdx.value >= 0) {
                imageFiles.value.splice(currentIdx.value, 1);

                let oldValue = currentIdx.value;

                currentIdx.value = Math.min(currentIdx.value, imageFiles.value.length - 1);

                if(currentIdx.value === oldValue)
                {
                    readImage(imageFiles.value[currentIdx.value].data);
                }
            }
        }

        async function annotateImages() {
            const formData = new FormData();

            for(let i = 0; i < imageFiles.value.length; i++) {
                await new Promise((resolve) => {
                    imageFiles.value[i].data.file((file) => {
                        formData.append('files', file, imageFiles.value[i].fileName);
                        resolve();
                    });
                });
                // formData.append('images', imageFiles.value[i].data);
            }

            formData.append('model', currentModel.value);
            formData.append('mode', currentTask.value)
            // let result = filenames.value.reduce((o, k, i) => ({...o, [k]: frames.value[i]}), {});

            // console.log(result);

            // let payload = {
            //     model: currentModel.value,
            //     images: result
            // };

            console.log(formData);

            showSpinner.value = true;
            
            annotationStore.annotate(formData).then(() => {
                console.log("returned");
                showSpinner.value = false;
            }).catch((err) => {
                console.log(err);
                showSpinner.value = false;
            });
        }

        onMounted(() => {
            annotationStore.loadAvailableModels();
        });

        return {
            currentModel,
            currentTask,
            modelOptions,
            currentFrame,
            currentIdx,
            imageFiles,
            // frames,
            filenames,
            showSpinner,
            disableAnnotateButton,
            uploadModelMsg,
            handleDrop,
            prevImage,
            nextImage,
            removeImage,
            annotateImages,
            handleModelDrop
        };
    },
};
</script>

<style scoped>
.flex-container {
    display: flex;
    flex-direction: row;
    width: 100%;
    height: 100%;
    color: white;
    margin: 0;
    /* background-color: red; */
}

.folder-upload {
    background-color: black;
    width: 25%;
    height: 90%;
    margin: auto;
    border-radius: 10px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

p {
    font-size: xx-large;
    font-weight: bold;
}

.images-control {
    /* background-color: blue; */
    width: 50%;
    height: 90%;
    margin: auto;
    border-radius: 10px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.frame-view {
    width: 100%;
    height: 90%;
    position: relative;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: center
}

.prev, .next {
  background-color: white;
  cursor: pointer;
  position: absolute;
  top: 50%;
  width: auto;
  margin-top: -22px;
  padding: 16px;
  color: black;
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
  color: white;
}

.action-control {
    width: 98%;
    height: 10%;
    display: flex;
    justify-content: flex-end;
    align-items: center;
    /* background-color: red; */
}

.images-info {
    margin-right: auto;
    background-color: black;
    width: 15%;
    height: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    border-radius: 10px;
    font-size: large;
}

.image-name {
    margin-right: 1%;
    color: white;
    width: 50%;
    height: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    font-style: italic;
}

button {
    /* margin-top: auto; */
    /* margin-left: 1%; */
    background-color: red;
    color: white;
    border: none;
    width: 50%;
    height: 50%;
    font-size: 1vw;
    display: flex;
    justify-content: center;
    align-items: center;
}

button:disabled,
button[disabled] {
    border: 1px solid #999999;
    background-color: #cccccc;
    color: #666666;
    cursor: not-allowed;
}

button:hover {
    background-color: rgb(255, 96, 96);
}

.model-control {
    background-color: rgba(0, 0, 0, 0.386);
    width: 20%;
    height: 90%;
    margin: auto;
    border-radius: 10px;
    display: flex;
    flex-direction: column;
}

.model-list {
    width: 98%;
    height: 10%;
    margin-top: 5%;
    margin-left: 1%;
}

.model-task {
    width: 98%;
    height: 10%;
    margin-top: 5%;
    margin-left: 1%;
}

.model-drop {
    width: 98%;
    height: 50%;
    margin-top: 10%;
    margin-left: 1%;
    border-radius: 10px;
    background-color: black;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.annotate-btn {
    background-color: white;
    color: #0024D3;
}

.annotate-btn:hover {
    background-color: rgb(192, 192, 192);
}

.fulfilling-bouncing-circle-spinner, .fulfilling-bouncing-circle-spinner * {
    box-sizing: border-box;
}

.fulfilling-bouncing-circle-spinner {
    height: 30px;
    width: 30px;
    position: relative;
    animation: fulfilling-bouncing-circle-spinner-animation infinite 4000ms ease;
    margin-right: 5%;
}

.fulfilling-bouncing-circle-spinner .orbit {
    height: 30px;
    width: 30px;
    position: absolute;
    top: 0;
    left: 0;
    border-radius: 50%;
    border: calc(30px * 0.03) solid #ff1d5e;
    animation: fulfilling-bouncing-circle-spinner-orbit-animation infinite 4000ms ease;
}

.fulfilling-bouncing-circle-spinner .circle {
    height: 30px;
    width: 30px;
    color: #ff1d5e;
    display: block;
    border-radius: 50%;
    position: relative;
    border: calc(30px * 0.1) solid #ff1d5e;
    animation: fulfilling-bouncing-circle-spinner-circle-animation infinite 4000ms ease;
    transform: rotate(0deg) scale(1);
}

@keyframes fulfilling-bouncing-circle-spinner-animation {
    0% {
    transform: rotate(0deg);
    }
    100% {
    transform: rotate(360deg);
    }
}

@keyframes fulfilling-bouncing-circle-spinner-orbit-animation {
    0% {
    transform: scale(1);
    }
    50% {
    transform: scale(1);
    }
    62.5% {
    transform: scale(0.8);
    }
    75% {
    transform: scale(1);
    }
    87.5% {
    transform: scale(0.8);
    }
    100% {
    transform: scale(1);
    }
}

@keyframes fulfilling-bouncing-circle-spinner-circle-animation {
    0% {
    transform: scale(1);
    border-color: transparent;
    border-top-color: inherit;
    }
    16.7% {
    border-color: transparent;
    border-top-color: initial;
    border-right-color: initial;
    }
    33.4% {
    border-color: transparent;
    border-top-color: inherit;
    border-right-color: inherit;
    border-bottom-color: inherit;
    }
    50% {
    border-color: inherit;
    transform: scale(1);
    }
    62.5% {
    border-color: inherit;
    transform: scale(1.4);
    }
    75% {
    border-color: inherit;
    transform: scale(1);
    opacity: 1;
    }
    87.5% {
    border-color: inherit;
    transform: scale(1.4);
    }
    100% {
    border-color: transparent;
    border-top-color: inherit;
    transform: scale(1);
    }
}
</style>

