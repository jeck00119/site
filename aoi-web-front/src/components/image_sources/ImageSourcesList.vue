<template>
    <div class="list-container" :style="{width: '100%', height: '100%'}">
        <div class="select-container">
            <vue-multiselect
                v-model="currentImageSource"
                :options="sources"
                track-by="uid"
                label="name"
                placeholder="Select Image Source"
                :searchable="true"
            ></vue-multiselect>
        </div>
        <div class="action-wrapper">
            <button class="action-button" @click="showAddDialog">
                <div class="button-container">
                    <div class="button-icon">
                        <v-icon name="io-add-circle-sharp" scale="1"/>
                    </div>
                </div>
            </button>
            <button class="action-button" @click="showDeleteDialog(currentImageSource)" :disabled="!currentImageSource">
                <div class="button-container">
                    <div class="button-icon">
                        <v-icon name="fa-trash" scale="1"/>
                    </div>
                </div>
            </button>
        </div>
        <base-dialog :show="addDialogShown" :title="'Add Source'" @close="closeAddDialog">
            <div class="dialog-input-container">
                <div class="type-container">
                    <label>Type:</label>
                    <div class="dialog-type-buttons-container">
                        <button class="dialog-button" :class="{ 'type-button-selected': newSourceType === 'dynamic' }"
                            @click="selectType('dynamic')">
                            <font-awesome-icon icon="video-camera" size="xl" />
                        </button>
                        <button class="dialog-button" :class="{ 'type-button-selected': newSourceType === 'static' }"
                            @click="selectType('static')">
                            <font-awesome-icon icon="images" size="xl" />
                        </button>
                    </div>
                </div>
                <div class="name-container">
                    <label>Name:</label>
                    <div id="input-wrapper">
                        <input type="text" v-model="newSourceName" />
                    </div>
                </div>
            </div>
            <div class="dialog-ctrl-buttons-container">
                <base-button :width="'25%'" @click="closeAddDialog">
                    <font-awesome-icon icon="fa-x" />
                    Cancel
                </base-button>
                <base-button :width="'25%'" class="dialog-add-button" @click="addSource">
                    <font-awesome-icon icon="fa-plus" />
                    Add
                </base-button>
            </div>
        </base-dialog>
        <base-dialog :show="deleteDialogShown" :title="'Are you sure?'" @close="closeDeleteDialog">
            <div class="dialog-ctrl-buttons-container">
                <base-button :width="'25%'" @click="closeDeleteDialog">
                    <font-awesome-icon icon="fa-x" />
                    Cancel
                </base-button>
                <base-button :width="'25%'" class="dialog-add-button" @click="deleteSource(sourceToDelete)">
                    <font-awesome-icon icon="fa-check" />
                    Delete
                </base-button>
            </div>
        </base-dialog>
    </div>
</template>
<script>
import { ref, watch } from 'vue';
import { useStore } from 'vuex';

import VueMultiselect from 'vue-multiselect';

export default {
    components: {
        VueMultiselect
    },

    props: ['sources'],
    emits: ['load-current-image-source', 'delete-source'],

    setup(_, context) {
        const store = useStore();
        const sourceIsLoaded = ref(false);
        const loadedSource = ref(null);
        const sourceToDelete = ref(null);

        const newSourceName = ref(null);
        const newSourceType = ref(null);

        const currentId = ref(null);
        const currentImageSource = ref(null);

        const addDialogShown = ref(false);
        const deleteDialogShown = ref(false);

        watch(currentImageSource, (newValue, _) => {
            if(newValue)
            {
                context.emit('load-current-image-source', newValue.uid);
            }
            else
            {
                context.emit('load-current-image-source', null);
            }
        });

        function setCurrentId(id) {
            currentId.value = id;
        }

        async function loadSource() {
            context.emit('load-current-image-source', currentId.value);
        }

        function showAddDialog() {
            addDialogShown.value = true;
        }

        function showDeleteDialog(source) {
            deleteDialogShown.value = true;
            sourceToDelete.value = source;
        }

        function selectType(type) {
            newSourceType.value = type;
        }

        function closeAddDialog() {
            addDialogShown.value = false;
            newSourceName.value = null;
            newSourceType.value = null;
            selectType.value = null;
        }

        function closeDeleteDialog() {
            deleteDialogShown.value = false;
        }

        function addSource() {
            const newSource = {
                name: newSourceName.value,
                type: newSourceType.value
            }
            store.dispatch("imageSources/addImageSource", newSource);
            closeAddDialog();
        }

        function deleteSource(source) {
            context.emit("delete-source", source);
            closeDeleteDialog();
        }

        return {
            currentId,
            currentImageSource,
            addDialogShown,
            newSourceName,
            newSourceType,
            deleteDialogShown,
            sourceToDelete,
            sourceIsLoaded,
            loadedSource,
            loadSource,
            setCurrentId,
            addSource,
            showAddDialog,
            closeAddDialog,
            selectType,
            deleteSource,
            showDeleteDialog,
            closeDeleteDialog
        }
    }
}
</script>

<style scoped>
.list-container {
    display: flex;
    flex-direction: row;
    background-color: inherit;
    width: 100%;
    height: 100%;
    margin: 0;
}

.select-container {
    width: 90%;
    height: 100%;
}

.action-wrapper {
    margin-bottom: 1vh;
    display: flex;
    width: 8%;
    margin-left: 2%;
    justify-content: end;
}

.action-button {
    width: 50%;
    height: 100%;
    background-color: rgb(0, 0, 0);
    border: none;
    /* padding: 5% 35%; */
    /* border-radius: 10px; */
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

ul {
    color: rgba(204, 161, 82);
    list-style: none;
    padding-left: 0pt;
    background-color: rgb(0, 0, 0);
    overflow-y: auto;
    width: 100%;
}

li {
    display: flex;
    justify-content: space-between;
    align-items: center;
    /* margin:3px; */
    /* user-select:none; */
    color: rgba(204, 161, 82);
    height: 7%;
    background-color: rgb(37, 36, 36);
}

li:hover {
    background-color: rgb(61, 61, 62);
}

.li-text {
    padding: 10px;
}

.li-button {
    cursor: pointer;
}

.add-button-container {
    display: flex;
    justify-content: start;
}

.add-button {
    width: 100%;
    color: rgba(204, 161, 82);
}

.type-button-selected {
    background-color: rgba(204, 161, 82);
    color: white;
}

#input-wrapper {
    width: 80%;
}

input {
    outline: none;
    border: none;
    width: 23.8vw;
}

label {
    margin-right: 10%;
    color: white;
    width: 10%;
}

.dialog-input-container {
    display: flexbox;
    margin: 2%;
}

.type-container {
    width: 100%;
}

.name-container {
    width: 100%;
    display: flex;
    align-items: center;
}

.dialog-type-buttons-container {
    display: inline-flex;
    width: 80%;
}

.dialog-button {
    outline: none;
    border: none;
    width: 11.4vw;
    height: 11.4vw;
    margin-bottom: 2%;
    margin-right: 1vh;
}

.dialog-button:hover {
    background-color: rgba(204, 161, 82);
}

.dialog-ctrl-buttons-container {
    display: flex;
    justify-content: end;
    margin: 5%;
}

.dialog-add-button {
    background-color: rgba(204, 161, 82);
    color: white;
}

.add-button {
    border: none;
    color: rgba(204, 161, 82);
}

.add-button:hover {
    background-color: rgba(204, 161, 82);
    color: white;
}

button:disabled,
button[disabled] {
    border: 1px solid #999999;
    background-color: #cccccc;
    color: #666666;
    cursor: not-allowed;
}

::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-track {
    background: rgb(0, 0, 0);
}

::-webkit-scrollbar-thumb {
    background: #888;
}

::-webkit-scrollbar-thumb:hover {
    background: #555;
}
</style>