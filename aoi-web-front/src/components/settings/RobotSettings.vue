<template>
    <div class="list-wrapper">
        <div class="robot-config-wrapper" v-for="robot in robots" :key="robot.uid">
            <p class="robot-name">{{robot.name}}</p>
            <div class="close">
                <button @click="removeRobot(robot.uid)">&#10006;</button>
            </div>
            <div v-if="robot.type === 'ultraArm'" class="port-wrapper">
                <label for="robot-port">Port:</label>
                <base-dropdown
                    width="100%"
                    :current="robot.port"
                    :values="robotPorts"
                    @update-value="(name, value) => updateConnectionID(robot.uid, value)"
                ></base-dropdown>
            </div>
            <div v-else class="ip-wrapper">
                <label for="robot-ip">IP:</label>
                <div class="robot-ip">
                    <base-text-input
                        :current="robot.ip"
                        width="100%"
                        pattern="^((\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.){3}(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$"
                        @update-value="(_, value) => updateConnectionID(robot.uid, value)"
                    ></base-text-input>
                </div>
            </div>
            <div class="type-wrapper">
                <label for="robot-type">Type:</label>
                <base-dropdown
                    width="100%"
                    :current="robot.type"
                    :values="robotTypes"
                    @update-value="(_, value) => updateType(robot.uid, value)"
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
        <base-button-rectangle width="10vw" @state-changed="saveRobots" :disabled="disable">
            <div class="button-container">
                <div class="button-icon">
                    <v-icon name="ri-save-3-fill" scale="1.5"/>
                </div>
                <div class="button-text">SAVE</div>
            </div>
        </base-button-rectangle>
    </div>

    <base-dialog title="Create a new Robot:" :show="showDialog" height="20vh" @close="close">
            <template #default>
                <div class="form-control">
                    <label class="dialog-label" for="robot-name">Robot Name:</label>
                    <input type="text" name="robot-name" id="robot-name" v-model.trim="newRobotName">
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
                    <base-button width="7vw" mode="flat" @click="addRobot">Ok</base-button>
                </div>
            </template>
        </base-dialog>
</template>

<script>
import { ref } from 'vue';

export default {
    props: ['robots', 'robotPorts', 'robotTypes', 'disable'],

    emits: ['remove-robot', 'add-robot', 'save-robots', 'update-connection-id', 'update-type'],

    setup(_, context) {
        const showDialog = ref(false);
        const newRobotName = ref('');
        const invalidName = ref(false);

        function removeRobot(uid)
        {
            context.emit('remove-robot', uid);
        }

        function addRobot() {
            invalidName.value = false;

            if(newRobotName.value === '')
            {
                invalidName.value = true;
                return;
            }
            else
            {
                context.emit('add-robot', newRobotName.value);
                close();
            }
        }

        function saveRobots() {
            context.emit('save-robots');
        }

        function updateConnectionID(uid, value) {
            context.emit('update-connection-id', uid, value);
        }

        function updateType(uid, value) {
            context.emit('update-type', uid, value);
        }

        function show() {
            showDialog.value = true;
        }

        function close() {
            newRobotName.value = '';
            invalidName.value = false;
            showDialog.value = false;
        }

        return {
            showDialog,
            newRobotName,
            invalidName,
            removeRobot,
            addRobot,
            saveRobots,
            updateConnectionID,
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

.robot-config-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin: 1%;
    width: 80%;
    height: 15vh;
    background-color: rgb(90, 90, 90);
    border-radius: 12px;
    padding: 15px;
    position: relative;
}

.port-wrapper {
    margin-top: 0.5vh;
    width: 60%;
    display: flex;
}

.ip-wrapper {
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

.robot-name {
    font-weight: bold;
}

.robot-name:hover {
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

.robot-ip {
    width: 100%;
}

.robot-config-wrapper .close {
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