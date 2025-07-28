<template>
    <div class="wrapper">
        <div class="flex-container-scoped">
            <div class="list-container">
                <div class="ul-container">
                    <transition-group tag="ul" name="listanim">
                        <li v-for="itac in itacList" :key="itac.uid">
                            <div class="list-element" :class="{ selected: isSelected(itac) }" @click="selectItac(itac)">
                                {{ itac.name }}
                            </div>
                        </li>
                    </transition-group>
                </div>

                <div class="button-container">
                    <base-button-rectangle class="button-scoped" @click="deleteItac(selectedItacUid)"
                        :disabled="!selectedItacUid">
                        <font-awesome-icon icon="trash" />
                        Delete
                    </base-button-rectangle>
                    <base-button-rectangle class="button-scoped" @click="saveItac">
                        <font-awesome-icon icon="floppy-disk" />
                        Save
                    </base-button-rectangle>
                </div>
            </div>
            <div class="input-container">
                <div class="input-wrapper">
                    <font-awesome-icon class="icon" icon="signature" />
                    <label>Name</label>
                    <input type="text" v-model="currentItac.name" /><br>
                    <font-awesome-icon class="icon" icon="flag-checkered" />
                    <label>Destination IP</label>
                    <input type="text" v-model="currentItac.destination_ip" /><br>
                    <font-awesome-icon class="icon" icon="network-wired" />
                    <label>Destination Port</label>
                    <input type="text" v-model="currentItac.destination_port" /><br>
                    <font-awesome-icon class="icon" icon="play-circle" />
                    <label>Start Booking Code</label>
                    <input type="text" v-model="currentItac.start_booking_code" /><br>
                    <font-awesome-icon class="icon" icon="check" />
                    <label>Pass Booking Code</label>
                    <input type="text" v-model="currentItac.pass_booking_code" /><br>
                    <font-awesome-icon class="icon" icon="x" />
                    <label>Fail Booking Code</label>
                    <input type="text" v-model="currentItac.fail_booking_code" /><br>
                </div>
            </div>
        </div>
        <base-notification :show="showNotification" :timeout="notificationTimeout" height="15vh" color="#CCA152" @close="clearNotification">
            <div class="message-wrapper">
                <div class="icon-wrapper">
                    <v-icon :name="notificationIcon" scale="2.5" animation="float" />
                </div>
                <div class="text-wrapper">
                    {{ notificationMessage }}
                </div>
            </div>
        </base-notification>
    </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useStore } from 'vuex';
import useNotification from '../../hooks/notifications';
import { uuid } from "vue3-uuid";

import BaseButtonRectangle from '../base/BaseButtonRectangle.vue';


export default {
    components: {
        BaseButtonRectangle
    },

    setup() {
        const store = useStore();

        const {showNotification, notificationMessage, notificationIcon, notificationTimeout, 
            setNotification, clearNotification} = useNotification();

        const currentItac = ref({
            name: '',
            destination_ip: '',
            destination_port: '',
            start_booking_code: '',
            pass_booking_code: '',
            fail_booking_code: '',
            uid: 0
        });

        const selectedItacUid = ref(null);

        const currentUser = computed(function() {
            return store.getters["auth/getCurrentUser"];
        });
        
        const itacList = computed(function() {
            return store.getters["itac/getItacList"];
        });

        async function deleteItac(uid) {
            // try {
            store.dispatch("itac/deleteItac", {
                uid: uid
            }).then(() => {
                selectedItacUid.value = null;
                resetItac();

                store.dispatch("log/addEvent", {
                    type: 'ITAC SETTINGS',
                    user: currentUser.value ? currentUser.value.username : 'Unknown',
                    title: 'ITAC Deleted',
                    description: `ITAC ${uid} configuration was deleted.`
                });
            }).catch(() => {
                setNotification(3000, err, 'bi-exclamation-circle-fill');
            });
        }

        async function saveItac() {
            if (currentItac.value.name === '') {
                showNotification.value = true;
                notificationMessage.value = "Empty name field - please add a name";
                return;
            }

            if (selectedItacUid.value) {
                let currentItacDeep = JSON.parse(JSON.stringify(currentItac.value));
                store.dispatch("itac/updateItac", currentItacDeep).then(() => {
                    store.dispatch("log/addEvent", {
                        type: 'ITAC SETTINGS',
                        user: currentUser.value ? currentUser.value.username : 'Unknown',
                        title: 'ITAC Updated',
                        description: `ITAC ${currentItac.value.name} configuration was updated.`
                    });
                    setNotification('3000', 'ITAC configuration updated.', 'fc-ok');
                }).catch(() => {
                    setNotification('3000', 'Error while updating ITAC.', 'bi-exclamation-circle-fill');
                });
            }
            else {
                generateID();
                let currentItacDeep = JSON.parse(JSON.stringify(currentItac.value));
                store.dispatch("itac/saveItac", currentItacDeep).then(() => {
                    selectedItacUid.value = currentItacDeep.uid;

                    store.dispatch("log/addEvent", {
                        type: 'ITAC SETTINGS',
                        user: currentUser.value ? currentUser.value.username : 'Unknown',
                        title: 'ITAC Updated',
                        description: `ITAC ${currentItac.value.name} configuration was added.`
                    });

                    setNotification('3000', 'ITAC configuration saved.', 'fc-ok');
                }).catch(() => {
                    setNotification('3000', 'Error while saving ITAC.', 'bi-exclamation-circle-fill');
                });
            }
        }

        function selectItac(itac) {
            if (selectedItacUid.value && selectedItacUid.value === itac.uid) {
                selectedItacUid.value = null;
                resetItac();
            }
            else {
                selectedItacUid.value = itac.uid;
                let itacDeep = JSON.parse(JSON.stringify(itac));
                currentItac.value.name = itacDeep.name;
                currentItac.value.destination_ip = itacDeep.destination_ip;
                currentItac.value.destination_port = itacDeep.destination_port;
                currentItac.value.start_booking_code = itacDeep.start_booking_code;
                currentItac.value.pass_booking_code = itacDeep.pass_booking_code;
                currentItac.value.fail_booking_code = itacDeep.fail_booking_code;
                currentItac.value.uid = itacDeep.uid;
            }
        }

        function generateID() {
            currentItac.value.uid = uuid.v4();
        }

        function resetItac() {
            currentItac.value.name = '';
            currentItac.value.destination_ip = '';
            currentItac.value.destination_port = '';
            currentItac.value.start_booking_code = '';
            currentItac.value.pass_booking_code = '';
            currentItac.value.fail_booking_code = '';
            currentItac.value.uid = 0;
        }

        function isSelected(itac) {
            if (selectedItacUid.value && selectedItacUid.value === itac.uid)
                return true;

            return false;
        }

        onMounted(() => {
            store.dispatch("itac/loadItacList");
        });

        return{
            currentItac,
            selectedItacUid,
            itacList,
            showNotification,
            notificationMessage,
            notificationIcon,
            notificationTimeout,
            clearNotification,
            isSelected,
            selectItac,
            saveItac,
            deleteItac
        }
    }
}
</script>

<style scoped>
input {
    background-color: rgb(37, 36, 36);
    color: rgba(204, 161, 82);
    border: 0;
    outline: none;
    margin-top: 8px;
    margin-bottom: 10px;
}

input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
}

::-webkit-scrollbar {
    width: 0;
    /* Remove scrollbar space */
    background: transparent;
    /* Optional: just make scrollbar invisible */
}

ul {
    list-style: none;
    padding-left: 0pt;
    height: 240px;
    background-color: rgb(37, 36, 36);
    overflow-y: scroll;
    margin-top: 20px;
    margin-right: 15px;
    margin-left: 15px;
    margin-bottom: 0;
    width: 30%;
    /* scrollbar-width: none; */
}

.button-scoped {
    margin-left: 30px;
    /* margin-right: 23px; */
    width: 12%;

}

.wrapper {
    display: flex;
    width: 100%;
    height: 100%;
    justify-content: center;
    align-items: center;
}

.flex-container-scoped {
    display: flex;
    background-color: rgb(68, 66, 66);
    width: 100%;
    height: 40%;
    justify-content: center;
    align-items: center;
}

.list-container {
    display: inline-block;
    width: 50%;

}

.input-container {
    color: rgba(204, 161, 82);
    display: flex;
    width: 50%;
    margin-top: 10px;
    margin-bottom: 10px;
    justify-content: start;
    align-items: center;
}

.ul-container {
    display: flex;
    margin: 0 auto;
    justify-content: end;
}

.button-container {
    display: flex;
    margin-left: 15px;
    margin-top: 10px;
    margin-bottom: 15px;
    margin-right: 13px;
    justify-content: end;
}

.list-element {
    display: list;
    text-align: left;
    user-select: none;
    color: rgba(204, 161, 82);
    padding: 2px;
}

.list-element:hover {
    background-color: rgba(121, 223, 63, 0.711);
    border-color: rgb(32, 31, 31);
    color: black;
    cursor: pointer;
}

.selected {
    background-color: rgba(121, 223, 63, 0.711);
    border-color: rgb(32, 31, 31);
    color: black;
    text-align: left;
    cursor: pointer;
    padding: 2px;
}

label {
    display: inline-block;
    width: 200px;
    text-align: left;
    padding-top: 8px;
    padding-bottom: 10px;
    padding-left: 0;
    color: rgba(204, 161, 82);
    /* font-family:'Lucida Console'; */
    /* border: 1px solid black; */
}

.icon {
    width: 20px;
    height: 20px;
    margin-right: 3px;
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

.listanim-leave-from,
.listanim-enter-to {
    opacity: 1;
    transform: translateX(0);
}

.listanim-leave-active {
    transition: all 0.3s ease-in;
    position: absolute;
}

.listanim-enter-active {
    transition: all 0.3s ease-out;
}

.listanim-leave-to,
.listanim-enter-from {
    opacity: 0;
    transform: translateX(-30px);
}

.listanim-move {
    transition: transform 0.8s ease;
}
</style>