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
                                width="35%"
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
                                width="35%"
                                :current="filename"
                                :values="files"
                                name="file"
                                @update-value="updateFilename"
                            ></base-dropdown>
                        </div>
                        <div class="form-control">
                            <label for="channel">Channel:</label>
                            <base-dropdown
                                width="35%"
                                :current="channel"
                                :values="channels"
                                name="channel"
                                @update-value="updateChannel"
                            ></base-dropdown>
                        </div>
                        <div class="form-control">
                            <label for="priority">Priority:</label>
                            <base-dropdown
                                width="35%"
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
                                width="35%"
                                @update-value="updateVolume">
                            </base-slider>
                        </div>
                    </div>
                    <div class="actions-container">
                        <base-button-rectangle width="25%" @state-changed="saveCurrentConfig">
                            <div class="button-container">
                                <div class="button-icon">
                                    <v-icon name="ri-save-3-fill" scale="1.5"/>
                                </div>
                                <div class="button-text">Save</div>
                            </div>
                        </base-button-rectangle>
                        <base-button-rectangle width="25%" @state-changed="addChannel">
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
import { computed, onMounted, ref } from 'vue';
import { useMediaStore, useConfigurationsStore } from '@/composables/useStore';
import useNotification, { NotificationType } from '../../../hooks/notifications.js';
import { ValidationMessages, GeneralMessages, FileMessages } from '@/constants/notifications';

export default {
    setup() {
        const priorities = ['LOW', 'MEDIUM', 'HIGH'];

        const {showNotification, notificationMessage, notificationIcon, notificationTimeout, notificationType,
            setTypedNotification, clearNotification} = useNotification();

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
                setTypedNotification(
                    ValidationMessages.EVENT_NAME_REQUIRED,
                    NotificationType.ERROR,
                    3000
                );
                error = true;
            }

            if(filename.value === "")
            {
                setTypedNotification(
                    ValidationMessages.AUDIO_FILE_REQUIRED,
                    NotificationType.ERROR,
                    3000
                );
                error = true;
            }

            if(channel.value === "")
            {
                setTypedNotification(
                    'Please choose a channel before saving.',
                    NotificationType.ERROR,
                    3000
                );
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
                    setTypedNotification(
                        err || GeneralMessages.ERROR_OCCURRED,
                        NotificationType.ERROR,
                        3000
                    );
                }
            }
        }

        function addChannel() {
            try {
                mediaStore.addChannel();
            }
            catch(err) {
                setTypedNotification(
                    err || GeneralMessages.ERROR_OCCURRED,
                    NotificationType.ERROR,
                    3000
                );
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
            notificationType,
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
    justify-content: center; /* Changed from flex-start to center for vertical centering */
    align-items: center;
    width: 95%;
    min-height: 80vh; /* Changed from height: 100% to min-height: 80vh to ensure proper viewport centering */
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
    align-items: center; /* Vertically align labels with their fields */
    /* background-color: red; */
    justify-content: center;
    margin-left: -0.5%; /* Very slight shift to the right */
}


label {
   width: 8%; /* Much closer - minimal space between label and field */
}

input {
    width: 35%;
    background-color: rgb(67, 46, 46);
    color: white;
    border: none;
}

.actions-container {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1rem; /* Added gap for spacing between buttons */
    margin-top: 2rem; /* Add space between volume control and buttons */
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

</style>