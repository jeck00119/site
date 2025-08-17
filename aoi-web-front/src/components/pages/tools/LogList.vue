<template>
    <div class="flex-container">
        <div class="title-wrapper">
            <h1>Log View</h1>
        </div>

        <div class="filters-container">
            <div class="filters-wrapper">
                <vue-multiselect
                    v-model="filters"
                    :options="eventTypes"
                    :searchable="false"
                    :multiple="true"
                    :close-on-select="true"
                    placeholder="Choose filters">
                </vue-multiselect>
            </div>
        </div>

        <div class="table-wrapper">
            <table class="log-table">
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>User</th>
                        <th>Type</th>
                        <th>Title</th>
                        <th>Description</th>
                        <th></th>
                    </tr>
                </thead>
                <tr v-for="(event, idx) in events" :key="idx">
                    <td>{{ event.timestamp }}</td>
                    <td>{{ event.user }}</td>
                    <td>{{ event.type }}</td>
                    <td>{{ event.title }}</td>
                    <td
                        @mouseenter="showCurrentDetails(idx)"
                        @mouseleave="hideCurrentDetails"
                        ref="cell"
                        class="cell"
                    >{{ event.description }}</td>
                    <td><base-button @click="removeEvent(event.timestamp)">&#10005;</base-button></td>
                </tr>
            </table>
        </div>
        <div
            v-if="showDetails && currentDetails"
            class="hover-div"
            :style="divPosition"
            @mouseenter="showDetails = true"
            @mouseleave="hideCurrentDetails"
        >
            <div class="details-container">
                <div v-for="formattedObject, idx in formattedObjects" class="version" :key="idx">
                    <pre :class="{'old': idx % 2 === 0}" v-html="formattedObject"></pre>
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
import { ref, computed, onMounted } from 'vue';
import { useLogStore } from '@/composables/useStore';
import useNotification, { NotificationType } from '../../../hooks/notifications.js';
import { GeneralMessages } from '@/constants/notifications';
import { logger } from '@/utils/logger';

import VueMultiselect from 'vue-multiselect';

export default {
    components: {
        VueMultiselect
    },

    setup() {
        const filters = ref([]);
        const showDetails = ref(false);

        const currentDetails = ref(null);
        const formattedObjects = ref([]);
        
        const cell = ref(null);

        const divPosition = ref({
            top: '0px',
            left: '0px',
        });

        const {showNotification, notificationMessage, notificationIcon, notificationTimeout, notificationType,
            setTypedNotification, clearNotification} = useNotification();
        
        const logStore = useLogStore();

        const events = computed(function() {
            const events = logStore.events;

            // Ensure events is an array
            if (!events || !Array.isArray(events)) {
                return [];
            }

            let filteredEvents = null;

            if(filters.value.length > 0)
            {
                filteredEvents = events.filter(event => filters.value.includes(event.type));
            }
            else
            {
                filteredEvents = events;
            }

            return filteredEvents;
        });

        const eventTypes = computed(function() {
            const events = logStore.events;

            // Ensure events is an array
            if (!events || !Array.isArray(events)) {
                return [];
            }

            const types = events.map(event => event.type);

            return [... new Set(types)];
        });

        function removeEvent(timestamp) {
            try {
                logStore.removeEvent(timestamp);
            }catch(err) {
                setTypedNotification(
                    err || GeneralMessages.ERROR_OCCURRED,
                    NotificationType.ERROR,
                    3000
                );
            }
        }

        function showCurrentDetails(idx) {
            showDetails.value = true;
            currentDetails.value = events.value[idx].details;

            formatObjects();
            updateDivPosition(idx);
        }

        function hideCurrentDetails() {
            showDetails.value = false;
            currentDetails.value = null;
        }

        function updateDivPosition(idx) {
            if(cell.value[idx])
            {
                const cellRect = cell.value[idx].getBoundingClientRect();

                divPosition.value.top = `${cellRect.bottom}px`;
                divPosition.value.left = `${cellRect.left - 300}px`;
            }
        }

        function formatObjects() {
            if(currentDetails.value !== null)
            {
                formattedObjects.value = currentDetails.value.map(obj => {
                    return JSON.stringify(obj, null, 2);
                });
            }
        }

        onMounted(async () => {
            try {
                await logStore.loadEvents();
            } catch (error) {
                logger.error('Failed to load events', { error });
                setTypedNotification(
                    'Failed to load events',
                    NotificationType.ERROR,
                    3000
                );
            }
        });

        return {
            showDetails,
            events,
            filters,
            eventTypes,
            cell,
            divPosition,
            currentDetails,
            formattedObjects,
            showNotification,
            notificationIcon,
            notificationMessage,
            notificationTimeout,
            notificationType,
            removeEvent,
            showCurrentDetails,
            hideCurrentDetails,
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
    width: 100%;
    color: white;
}

.title-wrapper {
    width: 100%;
    text-align: center;
}

.table-wrapper {
    max-height: 70vh;
    margin-top: 5vh;
    overflow-y: auto;
}

.table-wrapper thead th {
    position: sticky;
    top: 0;
    z-index: 1;
}

.filters-container {
    width: 100%;
    margin-top: 5vh;
    display: flex;
    justify-content: flex-start;
}

.filters-wrapper {
    background-color: rgb(255, 252, 252);
    width: 20vw;
    margin-left: 2.5vw;
}

.phone {
    color: red;
    /* height: 50px; */
}

table {
    border-collapse: collapse;
    border-radius: 1em;
}

.log-table {
    background-color: rgb(0, 0, 0);
    color: rgb(255, 255, 255);
    width: 90vw;
    border-radius: 1em;
    border-collapse: collapse;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.26);
}

.log-table-header {
    background-color: rgb(204, 161, 82);
    width: 100%;
}

.table-header {
    border-radius: 20px;
}

th {
    background-color: rgb(0, 0, 0);
    border-radius: 1%;
    color: white;
}

.log-table tr:nth-child(even){
    background-color: #141313;
}

.log-table th{
    color: white;
    height: 5vh;
    position: sticky;
}

.log-table td {
    height: 3.5vh;
}

.table-wrapper::-webkit-scrollbar {
    display: none;
}

.cell {
  position: relative;
}

.hover-div {
  position: absolute;
  background-color: #272727;
  padding: 10px;
  border: 1px solid #ccc;
  width: 45vw;
  max-height: 25vh;
  display: flex;
  justify-content: flex-start;
  z-index: 5;
}

.details-container {
    display: flex;
    justify-content: flex-start;
    width: 100%;
    height: 100%;
}

pre {
    white-space: pre-wrap;
    font-family: monospace;
    /* display: flex;
    justify-content: flex-start; */
    outline: 1px dashed black;
    outline-offset: 0px;
    background-color: green;
}

.version {
    width: 100%;
    height: 100%;
    outline-offset: 0px;
}

.old {
    background-color: red;
}

ul {
    list-style-type: none;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: flex-start;
}

</style>

<!-- <style>
.multiselect__tags {
    font-weight: bold;
}

.multiselect__tag {
    border: 1px solid rgba(60, 60, 60, 0.26) !important;
    margin-bottom: 0px !important;
    margin-right: 5px !important;
}

.multiselect__placeholder {
    display: inline-block !important;
    margin-bottom: 0px !important;
    padding-top: 0px !important;
}
</style> -->