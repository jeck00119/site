<template>
    <div class="flex-container">
        <div class="card">
            <div class="title">
                <h1 class="prevent-select">Audio</h1>
            </div>
            <div class="form-container">
                <div class="form">
                    <div class="fields-container">
                        <div class="form-control">
                            <label for="name">Name:</label>
                            <base-dropdown
                                width="50%"
                                :current="eventName"
                                :values="events"
                                name="name"
                                @update-value="updateEventName"
                            ></base-dropdown>
                        </div>
                        <div class="form-control">
                            <label for="timeout">Timeout:</label>
                            <input type="number" id="timeout" v-model.trim="timeout"/>
                        </div>
                        <div class="form-control">
                            <label for="file">Audio file:</label>
                            <base-dropdown
                                width="50%"
                                :current="filename"
                                :values="files"
                                name="file"
                                @update-value="updateFilename"
                            ></base-dropdown>
                        </div>
                        <div class="form-control">
                            <label for="channel">Channel:</label>
                            <base-dropdown
                                width="50%"
                                :current="channel"
                                :values="channels"
                                name="channel"
                                @update-value="updateChannel"
                            ></base-dropdown>
                        </div>
                        <div class="form-control">
                            <label for="priority">Priority:</label>
                            <base-dropdown
                                width="50%"
                                :current="priority"
                                :values="priorities"
                                name="priority"
                                @update-value="updatePriority"
                            ></base-dropdown>
                        </div>
                        <div class="form-control">
                            <label for="priority">Volume:</label>
                            <base-slider
                                :min="0"
                                :max="100"
                                :current="volume"
                                :step="1"
                                name="volume"
                                width="50%"
                                @update-value="updateVolume">
                            </base-slider>
                        </div>
                    </div>
                    <div class="actions-container">
                        <base-button-rectangle width="50%" @state-changed="saveCurrentConfig">
                            <div class="button-container">
                                <div class="button-icon">
                                    <v-icon name="ri-save-3-fill" scale="1.5"/>
                                </div>
                                <div class="button-text">Save</div>
                            </div>
                        </base-button-rectangle>
                        <base-button-rectangle width="50%" @state-changed="addChannel">
                            <div class="button-container">
                                <div class="button-icon">
                                    <v-icon name="io-add-circle-sharp" scale="1.5"/>
                                </div>
                                <div class="button-text">Add Channel</div>
                            </div>
                        </base-button-rectangle>
                    </div>
                </div>
            </div>
        </div>
        <base-notification
            :show="showNotification"
            height="15vh"
            :timeout="notificationTimeout"
            @close="clearNotification"
        >
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
import { computed, onMounted, ref } from 'vue';
import { useMediaStore, useConfigurationsStore } from '@/composables/useStore';
import useNotification from '../../../hooks/notifications.js';

export default {
    setup() {
        const priorities = ['LOW', 'MEDIUM', 'HIGH'];

        const {showNotification, notificationMessage, notificationIcon, notificationTimeout, 
            setNotification, clearNotification} = useNotification();

        const mediaStore = useMediaStore();
        const configurationsStore = useConfigurationsStore();

        // These are already computed refs from the composables


        const currentConfiguration = configurationsStore.currentConfiguration;

        const events = mediaStore.events;

        const channels = mediaStore.channels;

        const files = mediaStore.files;

        // Handle both array of strings and array of objects
        const getInitialEventName = () => {
            if (events.value.length === 0) return "";
            const firstEvent = events.value[0];
            return typeof firstEvent === 'string' ? firstEvent : firstEvent.name || "";
        };
        
        const getInitialFileName = () => {
            if (files.value.length === 0) return "";
            const firstFile = files.value[0];
            return typeof firstFile === 'string' ? firstFile : firstFile.name || "";
        };
        
        const eventName = ref(getInitialEventName());
        const timeout = ref(0);
        const filename = ref(getInitialFileName());
        const channel = ref("");
        const priority = ref("LOW");
        let priorityIdx = 0;
        const volume = ref(50);

        function updateEventName(_, value) {
            eventName.value = value;
        }

        function updateFilename(_, value) {
            filename.value = value;
        }

        function updateChannel(_, value) {
            channel.value = value;
        }

        function updatePriority(_, value) {
            priority.value = value;
            priorityIdx = priorities.findIndex(priority => priority === value);
        }

        function updateVolume(_, value) {
            volume.value = parseInt(value);
        }

        function saveCurrentConfig() {
            let error = false;

            if(eventName.value === "")
            {
                setNotification(3000, `Please choose an event name before saving.`, 'bi-exclamation-circle-fill');
                error = true;
            }

            if(filename.value === "")
            {
                setNotification(3000, `Please choose an audio file before saving.`, 'bi-exclamation-circle-fill');
                error = true;
            }

            if(channel.value === "")
            {
                setNotification(3000, `Please choose a channel before saving.`, 'bi-exclamation-circle-fill');
                error = true;
            }

            if(!error)
            {
                try {
                    mediaStore.addEvent(
                        eventName.value,
                        filename.value,
                        timeout.value,
                        channel.value,
                        priorityIdx,
                        volume.value
                    );
                }catch(err) {
                    setNotification(3000, err, 'bi-exclamation-circle-fill');
                }
            }
        }

        function addChannel() {
            try {
                mediaStore.addChannel();
            }
            catch(err) {
                setNotification(3000, err, 'bi-exclamation-circle-fill');
            }
        }

        onMounted(() => {
            if(currentConfiguration.value)
            {
                mediaStore.loadEvents();
                mediaStore.loadChannels();
                mediaStore.loadFiles();
            }
        });

        return {
            events,
            channels,
            files,
            priorities,
            eventName,
            timeout,
            filename,
            channel,
            priority,
            volume,
            showNotification,
            notificationIcon,
            notificationMessage,
            notificationTimeout,
            updateEventName,
            updateFilename,
            updateChannel,
            updatePriority,
            updateVolume,
            saveCurrentConfig,
            addChannel,
            clearNotification
        }
    }
}
</script>

<style scoped>
.flex-container {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: center;
    width: 95%;
    height: 100%;
    color: white;
    margin: auto;
}

.prevent-select {
    -webkit-user-select: none; /* Safari */
    -ms-user-select: none; /* IE 10 and IE 11 */
    user-select: none;
}

.card {
    background-color: rgb(22, 20, 20);
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.26);
    display: flex;
    width: 80%;
    height: 70%;
    margin: auto;
}

.form-container {
    width: 100%;
    height: 100%;
}

.form {
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    width: 100%;
    height: 100%;
}

.form-control {
    background-color: inherit;
    color: white;
    border: none;
    display: flex;
    /* background-color: red; */
    justify-content: center;
}


label {
   width: 20%;
}

input {
    width: 50%;
    background-color: rgb(67, 46, 46);
    color: white;
    border: none;
}

.actions-container {
    display: flex;
    justify-content: center;
    align-items: center;
    /* background-color: violet; */
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