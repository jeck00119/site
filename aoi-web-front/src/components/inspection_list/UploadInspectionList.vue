<template>
    <div class="upload-container" v-if="show">
        <div class="action">
            <button @click="$refs.importInspectionList.click()">Browse</button>
            <input
                    type="file"
                    ref="importInspectionList"
                    style="display:none"
                    name="file-import-inspection"
                    id="fileImportInsplection"
                    accept=".xlsx, .ods"
                    :disabled="false"
                    @change="onFileSelected"
                />
        </div>
        <div class="dropper-wrapper">
            <file-dropper @state-changed="changeDropperState" @files-dropped="onFileDropped">
                <div class="drop-container">
                    {{ dropText }}
                </div>
            </file-dropper>
        </div>
    </div>
</template>

<script>
import { ref } from 'vue';

import FileDropper from '../layout/FileDropper.vue';

export default {
    components: {
        FileDropper
    },
    
    props: ['show'],

    emits: ['file-changed'],

    setup(_, context) {
        const dropText = ref('Drag File Here');

        function changeDropperState(state) {
            dropText.value = state ? 'Drop File' : 'Drag File Here';
        }

        function onFileSelected(event) {
            context.emit('file-changed', event.target.files[0]);
        }

        function onFileDropped(files) {
            context.emit('file-changed', files[0]);
        }

        return {
            dropText,
            changeDropperState,
            onFileSelected,
            onFileDropped
        }
    }
}
</script>

<style scoped>
.upload-container {
    position: absolute;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background-color: #1D6F42;
    width: 30%;
    height: 25vh;
    border-radius: 10px;
    z-index: 10;
}

.action {
    height: 18%;
    width: 100%;
    margin-bottom: 1%;
    margin-top: 1%;
}

button {
    height: 100%;
    color: #1D6F42;
}

button:hover {
    border: #114227;
}

.dropper-wrapper {
    display: flex;
    width: 100%;
    height: 80%;
}

.drop-container{
    display: flex;
    justify-content: center;
    align-items: center;
    width: 90%;
    height: 90%;
    margin: auto;
    border: 2px dashed white;
    font-weight: bold;
}
</style>