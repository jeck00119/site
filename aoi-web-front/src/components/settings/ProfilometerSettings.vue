<template>
    <div class="list-wrapper">
        <div class="meter-config-wrapper" v-for="prof in profilometers" :key="prof.uid">
            <p class="meter-name">{{prof.name}}</p>
            <div class="close">
                <button @click="removeProfilometer(prof.uid)">&#10006;</button>
            </div>
            <div class="id-wrapper">
                <label for="meter-id">ID:</label>
                <div class="meter-id">
                    <base-text-input
                        :current="prof.id"
                        width="100%"
                        @update-value="(_, value) => updateID(prof.uid, value)"
                    ></base-text-input>
                </div>
            </div>
            <div class="path-wrapper">
                <label for="meter-path">Server:</label>
                <div class="meter-path">
                    <base-text-input
                        :current="prof.path"
                        width="100%"
                        @update-value="(_, value) => updatePath(prof.uid, value)"
                    ></base-text-input>
                </div>
            </div>
            <div class="type-wrapper">
                <label for="meter-type">Type:</label>
                <base-dropdown
                    width="100%"
                    :current="prof.type"
                    :values="profilometerTypes"
                    @update-value="(_, value) => updateType(prof.uid, value)"
                ></base-dropdown>
            </div>
        </div>
    </div>
    <div class="actions-container">
        <base-button-rectangle width="10vw" @state-changed="show" :disabled="disable">
            <div class="button-container">
                <div class="button-icon">
                    <v-icon name="io-add-circle-sharp" scale="1.5"/>
                </div>
                <div class="button-text">ADD</div>
            </div>
        </base-button-rectangle>
        <base-button-rectangle width="10vw" @state-changed="saveProfilometers" :disabled="disable">
            <div class="button-container">
                <div class="button-icon">
                    <v-icon name="ri-save-3-fill" scale="1.5"/>
                </div>
                <div class="button-text">SAVE</div>
            </div>
        </base-button-rectangle>
    </div>

    <base-dialog title="Create a new Profilometer:" :show="showDialog" height="20vh" @close="close">
            <template #default>
                <div class="form-control">
                    <label class="dialog-label" for="meter-name">Profilometer Name:</label>
                    <input type="text" name="meter-name" id="meter-name" v-model.trim="newProfilometerName">
                </div>
                <transition name="error">
                    <div class="error" v-if="invalidName">
                        <p>Robot name should not be an empty string.</p>
                    </div>
                </transition>
            </template>
            <template #actions>
                <div class="action-control">
                    <base-button width="7vw" @click="close">Cancel</base-button>
                    <base-button width="7vw" mode="flat" @click="addProfilometer">Ok</base-button>
                </div>
            </template>
        </base-dialog>
</template>

<script>
import { ref } from 'vue';

export default {
    props: ['profilometers', 'profilometerTypes', 'disable'],

    emits: ['remove-profilometer', 'add-profilometer', 'save-profilometers', 'update-id', 'update-path', 'update-type'],

    setup(_, context) {
        const showDialog = ref(false);
        const newProfilometerName = ref('');
        const invalidName = ref(false);

        function removeProfilometer(uid)
        {
            context.emit('remove-profilometer', uid);
        }

        function addProfilometer() {
            invalidName.value = false;

            if(newProfilometerName.value === '')
            {
                invalidName.value = true;
                return;
            }
            else
            {
                context.emit('add-profilometer', newProfilometerName.value);
                close();
            }
        }

        function saveProfilometers() {
            context.emit('save-profilometers');
        }

        function updateID(uid, value) {
            context.emit('update-id', uid, value);
        }

        function updatePath(uid, value) {
            context.emit('update-path', uid, value);
        }

        function updateType(uid, value) {
            context.emit('update-type', uid, value);
        }

        function show() {
            showDialog.value = true;
        }

        function close() {
            newProfilometerName.value = '';
            invalidName.value = false;
            showDialog.value = false;
        }

        return {
            showDialog,
            newProfilometerName,
            invalidName,
            removeProfilometer,
            addProfilometer,
            saveProfilometers,
            updateID,
            updatePath,
            updateType,
            show,
            close
        }
    }
}
</script>

<style scoped>
.list-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    height: 100%;
    overflow-y: auto;
}

.meter-config-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin: 1%;
    width: 80%;
    height: 20vh;
    background-color: rgb(110, 99, 109);
    border-radius: 12px;
    padding: 15px;
    position: relative;
}

.id-wrapper {
    margin-top: 0.5vh;
    width: 60%;
    display: flex;
}

.path-wrapper {
    margin-top: 0.5vh;
    width: 60%;
    display: flex;
}

.type-wrapper {
    margin-top: 0.5vh;
    width: 60%;
    display: flex;
}

label {
    width: 10%;
}

.actions-container {
    height: 10%;
}

.meter-name {
    font-weight: bold;
}
.action-control{
    width: 50%;
    height: 100%;
    display: flex;
    justify-content: flex-end;
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

.meter-id {
    width: 100%;
}

.meter-path {
    width: 100%;
}

input {
    width: 60%;
    background-color: rgb(56, 54, 54);
    border: none;
    color: white;
}

.meter-config-wrapper .close {
    position: absolute;
    top: 0;
    right: 0;
}

button {
    background-color: inherit;
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

.dialog-label {
    width: 20%;
}
</style>