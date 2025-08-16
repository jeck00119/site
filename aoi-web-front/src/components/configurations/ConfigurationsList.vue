<template>
    <div class="configurations-container">
        <div class="list-wrapper">
            <div v-for="configuration in configurations" :key="configuration.uid">
                <div class="card-wrapper">
                    <base-card>
                        <div class="name">
                            <h3>{{ configuration.name }}</h3>
                        </div>
                        <div class="actions">
                            <base-button
                                width="8vw"
                                @click="loadConfiguration(configuration.uid)"
                            >
                                <div class="flex-center">
                                    <div class="button-icon">
                                        <v-icon name="fa-file-import" scale="1"/>
                                    </div>
                                    <div class="button-text">
                                        Load
                                    </div>
                                </div>
                            </base-button>
                            <base-button
                                width="8vw"
                                @click="removeConfiguration(configuration.uid)"
                                :disabled="!isAuthorized"
                            >
                                <div class="flex-center">
                                    <div class="button-icon">
                                        <v-icon name="md-delete-round" scale="1"/>
                                    </div>
                                    <div class="button-text">
                                        Delete
                                    </div>
                                </div>
                            </base-button>
                            <base-button
                                width="8vw"
                                @click="showDialog(configuration.uid)"
                                :disabled="!isAuthorized"
                            >
                                <div class="flex-center">
                                    <div class="button-icon">
                                        <v-icon name="md-modeeditoutline-sharp" scale="1"/>
                                    </div>
                                    <div class="button-text">
                                        Edit
                                    </div>
                                </div>
                            </base-button>
                            <base-button
                                width="8vw"
                                @click="copyConfigDialog(configuration.uid)"
                                :disabled="!isAuthorized"
                            >
                                <div class="flex-center">
                                    <div class="button-icon">
                                        <v-icon name="fa-copy" scale="1"/>
                                    </div>
                                    <div class="button-text">
                                        Copy
                                    </div>
                                </div>
                            </base-button>
                        </div>
                    </base-card>
                </div>
            </div>
        </div>
        <base-dialog title="Rename Configuration:" :show="showEditConfiguration" @close="closeDialog">
            <template #default>
                <div class="form-control">
                    <label for="component-name">Configuration Name:</label>
                    <input type="text" name="component-name" id="component-name" v-model.trim.lazy="configurationSelected.name"><br><br>
                    <label for="component-type">Configuration Type:</label>
                    <input type="text" name="component-type" id="component-type" v-model.trim.lazy="configurationSelected.type"><br><br>
                    <label for="part-number">Part Number:</label>
                    <input type="text" name="part-number" id="part-number" v-model.trim.lazy="configurationSelected.part_number"><br><br>
                </div>
                <transition name="error">
                    <div class="error" v-if="invalidName">
                        <p>Component name should not be an empty string.</p>
                    </div>
                </transition>
            </template>
            <template #actions>
                <div class="action-control">
                    <base-button width="7vw" @click="closeDialog">Cancel</base-button>
                    <base-button width="7vw" mode="flat" @click="editConfiguration">Ok</base-button>
                </div>
            </template>
        </base-dialog>
        <base-dialog title="Add Configuration:" :show="showAddConfiguration" @close="closeAddDialog">
            <template #default>
                <div class="form-control">
                    <label for="component-name">Configuration Name:</label>
                    <input type="text" name="component-name" id="component-name" v-model.trim="newConfigName"><br><br>
                    <label for="component-type">Configuration Type:</label>
                    <input type="text" name="component-type" id="component-type" v-model.trim="newComponentType"><br><br>
                    <label for="part-number">Part Number:</label>
                    <input type="text" name="part-number" id="part-number" v-model.trim="newPartNumber"><br><br>
                </div>
                <transition name="error">
                    <div class="error" v-if="invalidName">
                        <p>Configuration name should not be an empty string or an existing configuration name. Part number should also be unique.</p>
                    </div>
                </transition>
            </template>
            <template #actions>
                <div class="action-control">
                    <base-button width="7vw" @click="closeAddDialog">Cancel</base-button>
                    <base-button width="7vw" mode="flat" @click="addConfiguration">Add</base-button>
                </div>
            </template>
        </base-dialog>
        <div class="add-button" >
            <base-button-rectangle
                width="15vw"
                @click="showAddDialog"
                :disabled="!isAuthenticated"
            >
                <div class="flex-center">
                    <div class="button-icon">
                        <v-icon name="io-add-circle-sharp" scale="1"/>
                    </div>
                    <div class="button-text">
                        Add configuration
                    </div>
                </div>
            </base-button-rectangle>
        </div>
        <base-notification
            :show="showNotification"
            :timeout="notificationTimeout"
            height="15vh"
            color="#CCA152"
            @close="clearNotification"
        >
            <div class="flex-column-center">
                <div class="flex-center">
                    <v-icon :name="notificationIcon" scale="2.5" animation="spin"/>
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
import { useAlgorithmsStore, useImageSourcesStore, useConfigurationsStore, useAuthStore, useAuditStore } from '@/composables/useStore';

import useNotification from '../../hooks/notifications.js';

export default{
    setup() {
        const configurationSelected = ref(null);
        const showEditConfiguration = ref(false);
        const showAddConfiguration = ref(false);

        const newConfigName = ref('');
        const newComponentType = ref('');
        const newPartNumber = ref('');

        const copyConfigurationId = ref(null);
        const addConfigurationFlag = ref(false);
        const copyConfigurationFlag = ref(false);

        const {showNotification, notificationMessage, notificationIcon, notificationTimeout, 
            setNotification, clearNotification} = useNotification();

        const invalidName = ref(false);

        // Use centralized composables instead of direct store access
        const { loadAlgorithms, loadReferenceAlgorithms, loadConfiguredAlgorithms, loadBasicAlgorithms } = useAlgorithmsStore();
        const { loadImageSources } = useImageSourcesStore();
        const configStore = useConfigurationsStore();
        const { 
            configurations, 
            currentConfiguration,
            loadConfigurations,
            setCurrentConfiguration,
            resetAllDatabases,
            removeConfiguration: removeConfig,
            addConfiguration: addConfig,
            copyConfiguration,
            editConfiguration: editConfig,
            getConfigurationById
        } = configStore;
        const authStore = useAuthStore();
        const auditStore = useAuditStore();

        // These are already computed refs from the composables


        const currentUser = authStore.currentUser;

        const isAuthenticated = authStore.isAuthenticated;

        const isAuthorized = computed(function() {
            if (currentUser.value && (currentUser.value.level === 'admin' || currentUser.value.level === 'technician'))
                return true;

            return false;
        });

        async function loadConfiguration(id) {
            setNotification(null, 'Loading configuration. Please wait.', 'fa-cog');

            const configuration = configurations.value.find(config => config.uid === id);

            try {
                await configStore.loadConfiguration(configuration);

                loadAlgorithms();
                loadReferenceAlgorithms();

                loadImageSources();
                
                loadConfiguredAlgorithms();
                loadBasicAlgorithms();
            }catch(err) {
                setNotification(5000, err, 'bi-exclamation-circle-fill');
            }
            
            clearNotification();
        }

        async function removeConfiguration(id) {
            if(currentConfiguration.value && currentConfiguration.value.uid === id)
            {
                try {
                    await resetAllDatabases();
                    
                    setCurrentConfiguration(null);

                    await removeConfig({
                        uid: id
                    });

                    await auditStore.addEvent({
                        type: 'CONFIGURATIONS',
                        user: currentUser.value ? currentUser.value.username : 'Unknown',
                        title: 'Configuration Removed',
                        description: `Configuration with uid: ${id} was removed.`
                    });
                }catch (error) {
                    setNotification(5000, "Could not remove current configuration.", 'bi-exclamation-circle-fill');
                }
            }
            else
            {
                try {
                    await removeConfig({
                        uid: id
                    });

                    await auditStore.addEvent({
                        type: 'CONFIGURATIONS',
                        user: currentUser.value ? currentUser.value.username : 'Unknown',
                        title: 'Configuration Removed',
                        description: `Configuration with uid: ${id} was removed.`
                    });
                }catch(err) {
                    setNotification(5000, "Could not remove configuration.", 'bi-exclamation-circle-fill');
                }
            }
        } 

        async function addConfiguration() {
            invalidName.value = false;

            if(newConfigName.value === '')
            {
                invalidName.value = true;
                return;
            }

            let existingConfigurationNames = configurations.value.map(elem => elem.name);
            let existingConfigurationPartNumbers = configurations.value.map(elem => elem.part_number);

            if (existingConfigurationNames.includes(newConfigName.value) || existingConfigurationPartNumbers.includes(newPartNumber.value))
            {
                invalidName.value = true;
                return;
            }

            if (addConfigurationFlag.value)
            {
                try {
                    await addConfig({
                        name: newConfigName.value,
                        type: newComponentType.value,
                        part_number: newPartNumber.value
                    });

                    auditStore.addEvent({
                        type: 'CONFIGURATIONS',
                        user: currentUser.value ? currentUser.value.username : 'Unknown',
                        title: 'Configuration Added',
                        description: `Configuration ${newConfigName.value}  was aded.`
                    });
                }catch(err) {
                    setNotification(5000, `Could not add configuration ${newConfigName.value}.`, 'bi-exclamation-circle-fill');
                }
            }

            if (copyConfigurationFlag.value)
            {
                try {
                    await copyConfiguration({
                        config: {
                            name: newConfigName.value,
                            type: newComponentType.value,
                            part_number: newPartNumber.value
                        },
                        originalConfigId: copyConfigurationId.value
                    });

                    auditStore.addEvent({
                        type: 'CONFIGURATIONS',
                        user: currentUser.value ? currentUser.value.username : 'Unknown',
                        title: 'Configuration Copied',
                        description: `Configuration ${newConfigName.value}  was aded.`
                    });
                }catch(err) {
                    setNotification(5000, `Could not add configuration ${newConfigName.value}.`, 'bi-exclamation-circle-fill');
                }
            }
            
            closeAddDialog();
        }

        async function editConfiguration() {
            invalidName.value = false;

            if(configurationSelected.value.name === '')
            {
                invalidName.value = true;
                return;
            }

            try {
                await editConfig(configurationSelected.value);

                await auditStore.addEvent({
                    type: 'CONFIGURATIONS',
                    user: currentUser.value ? currentUser.value.username : 'Unknown',
                    title: 'Configuration Modified',
                    description: `Configuration ${configurationSelected.value.name} was modified.`
                });
            }catch(err) {
                setNotification(5000, `Could not edit configuration ${configurationSelected.value.name}.`, 'bi-exclamation-circle-fill');
            }

            closeDialog();
        }

        function showDialog(id) {
            const configuration = getConfigurationById(id);
            configurationSelected.value = configuration;
            showEditConfiguration.value = true;
        }

        function copyConfigDialog(id) {
            const configuration = getConfigurationById(id);

            newConfigName.value = configuration.name;
            newComponentType.value = configuration.type;
            newPartNumber.value = configuration.part_number;

            copyConfigurationId.value = id;
            copyConfigurationFlag.value = true;

            showAddConfiguration.value = true;
        }

        function closeDialog() {
            configurationSelected.value = null;
            showEditConfiguration.value = false;
        }

        function showAddDialog() {
            addConfigurationFlag.value = true;
            showAddConfiguration.value = true;
        }

        function closeAddDialog() {
            invalidName.value = false;

            newConfigName.value = '';
            newComponentType.value = '';
            newPartNumber.value = '';

            copyConfigurationFlag.value = false;
            addConfigurationFlag.value = false;

            copyConfigurationId.value = null;

            showAddConfiguration.value = false;

        }

        onMounted(() => {
            loadConfigurations();
        })

        return {
            configurations,
            configurationSelected,
            showEditConfiguration,
            showAddConfiguration,
            newConfigName,
            invalidName,
            newComponentType,
            newPartNumber,
            isAuthenticated,
            isAuthorized,
            showNotification,
            notificationMessage,
            notificationIcon,
            notificationTimeout,
            loadConfiguration,
            removeConfiguration,
            editConfiguration,
            addConfiguration,
            showDialog,
            copyConfigDialog,
            closeDialog,
            showAddDialog,
            closeAddDialog,
            clearNotification
        }
    }
}
</script>

<style scoped>
.configurations-container {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    /* align-items: center; */
    width: 100%;
    min-height: 100%;
    color: white;
}

.list-wrapper {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    justify-content: space-between;
    margin: 1%;
}

.card-wrapper {
    margin: 2%;
    width: 45vw;
}

.name {
    margin: 2vh 2vw;
}

.form-control {
    background-color: inherit;
    border: none;
    color: white;
    display: inline-block;
    justify-content: space-between;
}

.button-icon {
    height: 100%;
}

.button-text {
    height: 100%;
}

.error {
    color: red;
}

input {
    width: 60%;
    background-color: rgb(56, 54, 54);
    border: none;
    float: right;
    clear: both;
    appearance: textfield;
    color: white;
}


.text-wrapper {
    font-size: 100%;
    width: 95%;
    text-align: center;
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
</style>