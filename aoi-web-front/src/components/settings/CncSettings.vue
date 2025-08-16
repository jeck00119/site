<template>
    <div class="list-wrapper">
        <div class="cnc-config-wrapper" v-for="cnc in cncs" :key="cnc.uid">
            <p class="cnc-name">{{cnc.name}}</p>
            <div class="close">
                <button @click="removeCNC(cnc.uid)">&#10006;</button>
            </div>
            <div class="port-wrapper">
                <label for="cnc-port">Port:</label>
                <base-dropdown
                    width="90%"
                    :current="cnc.port"
                    :values="availablePorts"
                    name="port"
                    @update-value="(name, value) => updatePort(cnc.uid, name, value)"
                ></base-dropdown>
            </div>
            <div class="type-wrapper">
                <label for="cnc-type">Type:</label>
                <base-dropdown
                    width="90%"
                    :current="cnc.type"
                    :values="cncTypes"
                    name="type"
                    @update-value="(name, value) => updateType(cnc.uid, name, value)"
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
        <base-button-rectangle width="10vw" @state-changed="saveCNCs" :disabled="disable">
            <div class="button-container">
                <div class="button-icon">
                    <v-icon name="ri-save-3-fill" scale="1.5"/>
                </div>
                <div class="button-text">SAVE</div>
            </div>
        </base-button-rectangle>
    </div>

    <base-dialog title="Create a new CNC:" :show="showDialog" height="20vh" @close="close">
        <template #default>
            <div class="form-control">
                <label class="dialog-label" for="cnc-name">CNC Name:</label>
                <input type="text" name="cnc-name" id="cnc-name" v-model.trim="newCNCName">
            </div>
            <transition name="error">
                <div class="error" v-if="invalidName">
                    <p>CNC name should not be an empty string.</p>
                </div>
            </transition>
        </template>
        <template #actions>
            <div class="action-control">
                <base-button width="7vw" @click="close">Cancel</base-button>
                <base-button width="7vw" mode="flat" @click="addCNC">Ok</base-button>
            </div>
        </template>
    </base-dialog>
</template>

<script>
import { ref, computed } from 'vue';

export default {
    props: ['cncs', 'availablePorts', 'cncTypes', 'disable'],

    emits: ['remove-cnc', 'add-cnc', 'save-cncs', 'update-port', 'update-type'],

    setup(_, context) {
        const showDialog = ref(false);
        const newCNCName = ref('');
        const invalidName = ref(false);

        function removeCNC(uid)
        {
            context.emit('remove-cnc', uid);
        }

        function addCNC() {
            invalidName.value = false;

            if(newCNCName.value === '')
            {
                invalidName.value = true;
                return;
            }
            else
            {
                context.emit('add-cnc', newCNCName.value);
                close();
            }
        }

        function saveCNCs() {
            context.emit('save-cncs');
        }

        function updatePort(uid, _, value) {
            context.emit('update-port', uid, value);
        }

        function updateType(uid, _, value) {
            context.emit('update-type', uid, value);
        }

        function show() {
            showDialog.value = true;
        }

        function close() {
            newCNCName.value = '';
            invalidName.value = false;
            showDialog.value = false;
        }

        return {
            showDialog,
            newCNCName,
            invalidName,
            removeCNC,
            addCNC,
            saveCNCs,
            updatePort,
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
    min-height: 100%;
    /* overflow-y: auto; - moved scrolling to body level */
}

.cnc-config-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin: 1%;
    width: 80%;
    height: 25%;
    background-color: black;
    border-radius: 12px;
    padding: 15px;
    position: relative;
}

.cnc-name {
    font-weight: bold;
}

.cnc-name:hover {
    cursor: pointer;
}

.port-wrapper {
    margin-top: 1%;
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

.cnc-config-wrapper .close {
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

.actions-container {
    height: 10%;
}

p:hover {
    cursor: pointer;
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

input {
    width: 60%;
    background-color: rgb(56, 54, 54);
    border: none;
    color: white;
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