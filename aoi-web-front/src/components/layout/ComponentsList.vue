<template>
    <div class="list-container" :style="{width: width, height: height}">
        <div class="select-container">
            <vue-multiselect
                v-model="currentComponent"
                :options="components"
                track-by="uid"
                label="name"
                placeholder="Select Component"
                :searchable="true"
            ></vue-multiselect>
        </div>
        
        <!-- <div class="list-item-container">
            <div class="list-item" v-for="component in components" :key="component.uid" @mouseover="setCurrentId(component.uid)" @mouseleave="setCurrentId(null)">
                <div class="component-name">
                    <p>{{ component.name }}</p>
                </div>
                <div class="action-control" v-show="currentId === component.uid">
                    <base-action-button @state-changed="removeComponent">
                        <div class="button-container">
                            <div class="button-icon">
                                &#128465;
                            </div>
                        </div>
                    </base-action-button>
                    <base-action-button @state-changed="openComponent">
                        <div class="button-container">
                            <div class="button-icon">
                                &#10551;
                            </div>
                        </div>
                    </base-action-button>
                </div>
            </div>
        </div> -->
        <div class="action-wrapper">
            <!-- <base-button width="3vw" mode="flat" font-size="1.1rem" @click="openCreateDialog" :disabled="disable">
                <div class="button-container">
                    <div class="button-icon">
                        <v-icon name="io-add-circle-sharp" scale="1"/>
                    </div>
                </div>
            </base-button> -->
            <button class="action-button" @click="openCreateDialog" :disabled="disable">
                <div class="button-container">
                    <div class="button-icon">
                        <v-icon name="io-add-circle-sharp" scale="1"/>
                    </div>
                </div>
            </button>
            <button class="action-button" @click="removeComponent" :disabled="!currentComponent">
                <div class="button-container">
                    <div class="button-icon">
                        <v-icon name="fa-trash" scale="1"/>
                    </div>
                </div>
            </button>
        </div>
        <!-- <div v-if="retrieving" class="loading-spinner">
            <base-spinner :spinnerStyle='{borderColor: "#ffffff"}'></base-spinner>
        </div> -->
        <base-dialog title="Create a new component:" :show="showNewComponentDialog" @close="closeCreateDialog">
            <template #default>
                <div class="form-control">
                    <label for="component-name">Component Name:</label>
                    <input type="text" name="component-name" id="component-name" v-model.trim="newComponentName">
                </div>
                <transition name="error">
                    <div class="error" v-if="invalidName">
                        <p>Component name should not be an empty string.</p>
                    </div>
                </transition>
            </template>
            <template #actions>
                <div class="action-control">
                    <base-button width="7vw" @click="closeCreateDialog">Cancel</base-button>
                    <base-button width="7vw" mode="flat" @click="saveComponent">Ok</base-button>
                </div>
            </template>
        </base-dialog>
    </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue';

import VueMultiselect from 'vue-multiselect';

export default {
    props: ['width', 'height', 'components', 'retrieving', 'disable'],

    emits: ['load-component', 'remove-component', 'save-component'],

    components: {
        VueMultiselect
    },

    setup(_, context) {
        const currentId = ref(null);
        const currentComponent = ref(null);
        const showNewComponentDialog = ref(false);
        const invalidName = ref(false);
        const error = ref('');

        const newComponentName = ref('');

        watch(currentComponent, (newValue, _) => {
            if(newValue)
            {
                context.emit('load-component', newValue.uid);
            }
            else
            {
                context.emit('load-component', null);
            }
        });

        function setCurrentId(id) {
            currentId.value = id;
        }

        function removeComponent() {
            context.emit('remove-component', currentComponent.value.uid);
        }

        async function openComponent() {
            context.emit('load-component', currentComponent.value.uid);
        }

        function openCreateDialog() {
            showNewComponentDialog.value = true;
        }

        function closeCreateDialog() {
            newComponentName.value = '';
            invalidName.value = false;
            showNewComponentDialog.value = false;
        }

        function saveComponent() {
            invalidName.value = false;

            if(newComponentName.value === '')
            {
                invalidName.value = true;
                return;
            }
            else
            {
                context.emit('save-component', newComponentName.value);
                closeCreateDialog();
            }
        }

        return {
            currentComponent,
            currentId,
            showNewComponentDialog,
            newComponentName,
            invalidName,
            setCurrentId,
            removeComponent,
            openComponent,
            openCreateDialog,
            closeCreateDialog,
            saveComponent
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
    /* justify-content: space-between;
    align-items: flex-end; */
    /* background-color: rgb(0, 255, 26); */
    /* overflow-y: auto; */
}

.select-container {
    width: 90%;
    height: 100%;
}

.list-item-container {
    width: 100%;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
}

.list-item {
    width: 100%;
    height: 5vh;
    margin-bottom: 5px;
    background-color: gray;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    font-weight: 600;
    font-size: 0.7vw;
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

.component-name {
    width: 50%;
    height: 100%;
    display: flex;
    justify-content: flex-start;
    align-items: center;
}

p {
    margin: auto 0;
}

.action-control{
    width: 50%;
    height: 95%;
    margin: 0;
    display: flex;
    justify-content: space-evenly;
    align-items: center;
    margin: auto;
}

.form-control {
    background-color: inherit;
    border: none;
    color: white;
    display: flex;
    justify-content: space-between;
}

.error {
    color: red;
}

input {
    width: 60%;
    background-color: rgb(56, 54, 54);
    border: none;
    color: white;
}

button:disabled,
button[disabled] {
    border: 1px solid #999999;
    background-color: #cccccc;
    color: #666666;
    cursor: not-allowed;
}

.error-enter-from,
.error-leave-to {
    opacity: 0;
    transform: scale(0.8);
}

.error-enter-to,
.error-leave-from {
    opacity: 1;
    transform: scale(1);
}

.error-enter-active {
    transition: all 0.3s ease-out;
}

.error-leave-active {
    transition: all 0.3s ease-in;
}

.loading-spinner {
    align-self: center;
    margin: auto;
}
</style>