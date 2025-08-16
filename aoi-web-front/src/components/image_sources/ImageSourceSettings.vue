<template>
    <div class="main-ct">
        <transition name="placeholder-anim" mode="out-in">
            <div class="settings-loaded" v-if="currentImageSource">
                <div class="top-buttons">
                    <div class="image-source" id="left-control">
                        <base-button-rectangle :class="[cameraActive ? 'toggle-active' : '']" id="toggle-source-button"
                            @state-changed="toggleImageSource">

                            <div v-if="cameraActive === false">
                                <font-awesome-icon icon="fa-toggle-off" size="2xl" />
                            </div>
                            <div v-else>
                                <font-awesome-icon icon="fa-toggle-on" size="2xl" />
                            </div>

                        </base-button-rectangle>
                        <!-- <label id="toggle-source-label">
                            <font-awesome-icon icon="fa-images" />
                            Image Source: {{ currentImageSource.name }}
                        </label> -->
                    </div>
                    <div class="image-source" id="right-control">
                        <base-button-rectangle @state-changed="savePhoto" class="save-control">
                            <font-awesome-icon icon="fa-floppy-disk" />
                            Save Photo
                        </base-button-rectangle>
                        <base-button-rectangle @state-changed="saveConfig" class="save-control">
                            <font-awesome-icon icon="fa-floppy-disk" />
                            Save Config
                        </base-button-rectangle>
                    </div>
                </div>

                <div class="settings-container">
                    <button :class="{ disabled: type === 'static' }" @click="toggleSetting('Camera')" class="setting">
                        <font-awesome-icon icon="fa-video-camera" />
                        Camera
                    </button>

                    <div class="settings-submenu" v-if="selectedSetting === 'Camera' && type === 'dynamic'">
                        <div class="submenu-input">
                            <div class="sub-submenu">
                                <label>
                                    Camera:
                                </label>
                                <div class="input-container">
                                    <select v-model="selectedCameraUid">
                                        <option v-for="camera in camerasList" :key="camera.uid" :value="camera.uid">
                                            {{ camera.name }}
                                        </option>
                                    </select>
                                </div>
                            </div>
                        </div>
                        <div class="camera-control">
                            <button class="submenu-button" @click="showAddCamDialog = true">
                                <font-awesome-icon icon="fa-plus" size="xl"/>
                                Add Camera
                            </button>
                            <button class="submenu-button" @click="deleteCamera">
                                <font-awesome-icon icon="fa-trash" size="lg"/>
                                Delete
                            </button>
                            <base-dialog :show="showAddCamDialog" :title="'Add Camera'" @close="closeDialog">
                                <div class="dialog-input-container">
                                    <label>Name: </label>
                                    <input type="text" v-model="newCamera.name">
                                    <label>Type:</label>
                                    <select v-model="newCamera.cameraType">
                                        <option value="" disabled hidden>
                                        </option>
                                        <option v-for="type in cameraTypesList" :value=type>
                                            {{ type }}
                                        </option>

                                    </select>
                                    <label>OpenCV Index:</label>
                                    <input type="text" v-model="newCamera.openCvIndexId">
                                </div>
                                <div class="dialog-ctrl-buttons-container">
                                    <base-button :width="'25%'" @click="closeDialog">Cancel</base-button>
                                    <base-button :width="'25%'" class="dialog-add-button"
                                        @click="addCamera">Add</base-button>
                                </div>
                            </base-dialog>

                        </div>
                    </div>

                    <button :class="{ disabled: type === 'static' || selectedCameraUid === '' }" @click="toggleSetting('Camera Settings')"
                        class="setting">
                        <font-awesome-icon icon="fa-gear" />
                        Camera Settings
                    </button>

                    <div class="settings-submenu" v-if="selectedSetting === 'Camera Settings' && type === 'dynamic'">
                        <div class="submenu-input">
                            <div class="sub-submenu">
                                <label class="settings-label">
                                    <font-awesome-icon icon="fa-gear" size="2xl"></font-awesome-icon>
                                    Settings:
                                </label>
                                <div class="input-container">
                                    <select v-if="selectedCameraUid === ''"></select>
                                    <select v-else v-model="currentCameraSettingsUid">
                                        <option v-for="cameraSettings in cameraSettingsList" :key="cameraSettings.uid"
                                            :value="cameraSettings.uid">
                                            {{ cameraSettings.name }}
                                        </option>
                                    </select>
                                </div>
                                <div class="submenu-button-container">
                                    <button class="cs-button" @click="newCameraSettings">
                                        <font-awesome-icon icon="fa-plus" size="xl"></font-awesome-icon>
                                    </button>
                                </div>
                            </div>
                            <div v-if="newCameraSettingsFlag === true" class="new-settings-container">
                                <label id="new-name">
                                    <font-awesome-icon icon="fa-file-circle-plus" size="xl"></font-awesome-icon>
                                    New settings name:
                                </label>
                                <input type="text" id="new-camera-settings-name" @keyup.enter="setCameraSettingsVisibility"
                                    @blur="setCameraSettingsVisibility" v-model.trim="newCameraSettingsName">
                            </div>

                            <div class="camera-controls-container" v-if="showCameraControls === true">
                                <!-- <button class="cs-button" @click="loadSettingsToCamera">Load</button> -->
                                <button class="cs-button" @click="saveCameraSettings(currentCameraSettings)">
                                    <font-awesome-icon icon="fa-floppy-disk"></font-awesome-icon>
                                    Save Config
                                </button>
                                <button class="cs-button" @click="deleteCameraSettings(currentCameraSettings)">
                                    <font-awesome-icon icon="fa-trash"></font-awesome-icon>
                                    Delete
                                </button>

                                <div class="settings-list" v-for="(setting, index) in cameraControls" :key="setting.name">
                                    <div class="settings-label">
                                        <font-awesome-icon :icon="icon[setting.name]" size="2xl" id="setting-icon" />
                                        {{ setting.name[0].toUpperCase() + setting.name.slice(- (setting.name.length - 1))
                                        }}
                                    </div>
                                    <div class="cs-wrapper" v-if="setting.type === 'dropdown'">
                                        <div class="cs-container">
                                            <base-dropdown id="camera-type" :name="setting.name" 
                                                :values="getDropdownValues(setting.name, setting.values)"
                                                :current="getDropdownCurrentValue(setting.name, currentCameraSettings[setting.name], setting.values)"
                                                @update-value="updateCurrentValue">
                                            </base-dropdown>
                                        </div>
                                    </div>
                                    <div class="cs-wrapper" v-else-if="setting.type === 'range'">
                                        <div class="cs-container">
                                            <div class="container">
                                                <base-integer-input :min="setting.values[0]" :max="setting.values[1]"
                                                    :current="currentCameraSettings[setting.name]" :step="setting.step"
                                                    :name="setting.name.toUpperCase()" @update-value="updateCurrentValue">
                                                </base-integer-input>
                                                <base-slider :min="setting.values[0]" :max="setting.values[1]"
                                                    :current="currentCameraSettings[setting.name]" :step="setting.step"
                                                    :name="setting.name.toUpperCase()" :icon="icon[setting.name]"
                                                    @update-value="updateCurrentValue">
                                                </base-slider>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="cs-wrapper" v-else-if="setting.type === 'bool'">
                                        <div class="cs-container">
                                            <base-checkbox :current="getCheckBoxValue(getDropdownCurrentValue(setting.name, currentCameraSettings[setting.name]))"
                                                :name="setting.name.toUpperCase()"
                                                @update-value="updateCheckBoxValue"></base-checkbox>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                    </div>

                    <button :class="{ disabled: type === 'dynamic' }" @click="toggleSetting('Images Path')" class="setting">
                        <font-awesome-icon icon="fa-folder-open" />
                        Images Path
                    </button>
                    <div class="settings-submenu" id="images-path" v-if="selectedSetting === 'Images Path' && type === 'static'">
                        <div class="submenu-input">
                            <div class="directory-name">
                                <label id="dir-label">
                                    Current Directory:
                                </label>
                                <div id="path-container">
                                    {{ currentGenerator.dirPath }}
                                </div>
                            </div>
                        </div>
                        <div class="submenu-button-container">
                            <button class="submenu-button" @click="$refs.browseDirectory.click()">
                                <font-awesome-icon icon="fa-magnifying-glass" />
                                Browse Directory
                            </button>
                            <ul id="listing"></ul>
                        </div>
                        <input type="file" ref="browseDirectory" style="display:none" name="select-image-path"
                            id="imagePathDirectory" webkitdirectory multiple @change="onFolderSelected" />
                    </div>

                    <button @click="toggleSetting('CNC Locations')" class="setting">
                        <font-awesome-icon icon="fa-location-dot" />
                        CNC Locations
                    </button>
                    <div class="settings-submenu" v-if="selectedSetting === 'CNC Locations'">
                        <div class="submenu-input">
                            <div class="sub-submenu">
                                <label class="settings-label">
                                    <font-awesome-icon icon="fa-location-dot" size="2xl"/>
                                    Location: 
                                </label>
                                <div class="input-container">
                                    <select class="dropdown-select" v-model="location">
                                        <option v-for="loc in locationsList"
                                            :key="loc.name"
                                            :value="loc.name"
                                        >
                                        {{ loc.name }}
                                        </option>
                                    </select>
                                </div>
                            </div>
                        </div>
                        <div class="submenu-input">
                            <div class="sub-submenu">
                                <label class="settings-label">
                                    <font-awesome-icon icon="fa-clock" size="2xl"/>
                                    Settle Time: 
                                </label>
                                <div class="input-container">
                                    <input type="number" step="0.01" class="number-input" v-model="settleTime">
                                </div>
                            </div>
                        </div>
                        <div class="submenu-input">
                            <div class="sub-submenu">
                                <label class="settings-label">
                                    <font-awesome-icon icon="fa-check" size="2xl"></font-awesome-icon>
                                    Activate Location:
                                </label>
                                <div class="input-container">
                                    <base-checkbox v-model="activateLocation"></base-checkbox>
                                </div>
                            </div>
                        </div>
                    </div>
                    <button @click="toggleSetting('Additional Settings')" class="setting">
                        <font-awesome-icon icon="fa-gears" />
                        Additional Settings
                    </button>
                    <div class="settings-submenu" v-if="selectedSetting === 'Additional Settings'">
                        <div class="submenu-input">
                            <div class="sub-submenu">
                                <label class="settings-label">
                                    <font-awesome-icon icon="fa-crop" size="2xl"></font-awesome-icon>
                                    FPS:
                                </label>
                                <div class="input-container">
                                    <input type="number" class="number-input" v-model="fps" @input="onFpsInputChange" @change="onFpsInputChange">
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div v-else class="not-loaded">
                <div class="warning">
                    <font-awesome-icon icon="exclamation-circle" style="color:rgba(204, 161, 82)" size="10x" />
                    <h1>No image source loaded.</h1>
                </div>
            </div>
        </transition>
        <base-notification
            :show="showNotification"
            :timeout="null"
            height="15vh"
            color="#CCA152"
            @close="clearNotification"
        >
            <div class="message-wrapper">
                <div class="icon-wrapper">
                    <v-icon :name="notificationIcon" scale="2.5" animation="pulse"/>
                </div>
                <div class="text-wrapper">
                    {{ notificationMessage }}
                </div>
            </div>
        </base-notification>
    </div>
</template>

<script>
import { computed, onMounted, ref, toRef, watch } from 'vue';

import { useCameraStore, useImageSourcesStore, useCncStore } from '@/composables/useStore';
import useNotification from '../../hooks/notifications.js';


export default {

    props: ['type', 'currentImageSource', 'currentImageGenerator'],

    emits: ['generator-updated', 'camera-updated', 'camera-settings-updated', 'fps-updated', 'show-camera', 'save-photo', 'save-src-status', 'save-settings-status'],

    setup(props, context) {
        // Initialize centralized store composables
        const cameraStore = useCameraStore();
        const imageSourcesStore = useImageSourcesStore();
        const cncStore = useCncStore();
        const { store } = cameraStore; // Keep raw store access for missing methods

        const cameraSettings = ref({
            resolution: '',
            brightness: 0,
            contrast: 0,
            saturation: 0,
            sharpness: 0,
            gain: 0,
            autoExposure: false,
            exposure: 0,
            pan: 0,
            tilt: 0,
            zoom: 0,
            focus: 0,
            autoFocus: false
        });

        const showAddCamDialog = ref(false);

        const selectedSetting = ref('Additional Settings');

        const cameraActive = ref(false);

        const newCamera = ref({
            name: '',
            cameraType: '',
            openCvIndexId: 0
        });

        const {showNotification, notificationMessage, notificationIcon, notificationTimeout, 
            setNotification, clearNotification} = useNotification();

        const selectedCameraUid = ref("")
        const currentCameraSettingsUid = ref("");

        const location = ref("");
        const settleTime = ref(0.0);
        const activateLocation = ref(false);
        const fps = ref(1);

        const selectedDirectory = ref("");

        const currentImageSource = toRef(props, 'currentImageSource');
        
        watch(() => props.type, (newValue) => {
            // Handle type changes
        }, { immediate: true });

        const folderExistsFlag = ref(false);
        const newFolderFlag = ref(false);

        const showCameraControls = ref(false);

        const newCameraSettingsFlag = ref(false);
        const newCameraSettingsName = ref('');
        const ignoreSettingsChange = ref(false);

        const icon = {
            resolution: "fa-arrows-up-down-left-right",
            brightness: "fa-sun",
            contrast: "fa-circle-half-stroke",
            saturation: "fa-droplet",
            sharpness: "fa-gem",
            gain: "fa-chart-line",
            auto_exposure: "fa-wand-magic-sparkles",
            exposure: "fa-plus-minus",
            pan: "fa-arrows-left-right",
            tilt: "fa-camera-rotate",
            zoom: "fa-magnifying-glass",
            focus: "fa-expand",
            auto_focus: "fa-wand-magic-sparkles"
        };

        // These are already computed refs from the composables


        const imageGeneratorsList = imageSourcesStore.imageSources;

        const camerasList = cameraStore.cameras;

        const cameraSettingsList = cameraStore.cameraSettings;

        const currentCameraSettings = cameraStore.currentCameraSettings;

        const currentCamera = cameraStore.selectedCamera;

        function getCheckBoxValue(value) {
            if(value)
                return true;
            else
                return false;
        }

        function getDropdownValues(settingName, values) {
            // Convert resolution arrays to strings for the dropdown
            if (settingName === 'resolution' && Array.isArray(values)) {
                return values.map(val => {
                    if (Array.isArray(val) && val.length === 2) {
                        return `${val[0]}x${val[1]}`;
                    }
                    return val;
                });
            }
            return values;
        }

        function getDropdownCurrentValue(settingName, currentValue, availableValues) {
            // Handle resolution array - convert to string format
            if (settingName === 'resolution' && Array.isArray(currentValue)) {
                // Current value is [640, 480], convert to "640x480"
                if (currentValue.length === 2) {
                    const resolutionString = `${currentValue[0]}x${currentValue[1]}`;
                    console.log(`ImageSourceSettings - Converting resolution ${JSON.stringify(currentValue)} to "${resolutionString}"`);
                    return resolutionString;
                }
            }
            
            // Handle field name mapping for auto_exposure -> autoExposure, auto_focus -> autoFocus
            if (settingName === 'auto_exposure' && currentValue === undefined) {
                const mappedValue = currentCameraSettings.value?.autoExposure;
                console.log(`ImageSourceSettings - mapping auto_exposure to autoExposure: ${mappedValue}`);
                return mappedValue;
            }
            
            if (settingName === 'auto_focus' && currentValue === undefined) {
                const mappedValue = currentCameraSettings.value?.autoFocus;
                console.log(`ImageSourceSettings - mapping auto_focus to autoFocus: ${mappedValue}`);
                return mappedValue;
            }
            
            return currentValue;
        }

        function addCamera() {
            cameraStore.addCamera(newCamera.value);
            closeDialog();
        }

        function deleteCamera() {
            cameraStore.removeCamera(selectedCamera.value);
        }

        function setCameraSettingsVisibility() {
            if (newCameraSettingsName.value != "") {
                currentCameraSettingsUid.value = "";

                showCameraControls.value = true;

                const defaultSettings = store.getters["cameraSettings/getCurrentCameraDefaultSettings"];

                cameraStore.setCurrentCameraConfig(defaultSettings);

                cameraStore.loadCameraSettingsFromObject({
                    cameraUid: selectedCameraUid.value,
                    settings: defaultSettings
                });

                cameraStore.setCurrentCameraConfigName(newCameraSettingsName.value);
                cameraStore.setCurrentCameraConfigCameraType(currentCamera.value.cameraType);
            }
        }

        async function loadCameraSettings(cameraUid) {
            try {
                console.log('ImageSourceSettings - loadCameraSettings called with cameraUid:', cameraUid);
                await cameraStore.fetchCameraSettingsList(cameraUid);
                console.log('ImageSourceSettings - fetchCameraSettingsList completed successfully');
            } catch (error) {
                console.error('ImageSourceSettings - loadCameraSettings error:', error);
                throw error;
            }
        }

        function loadSettingsToCamera() {
            const payload = {
                cameraUid: selectedCameraUid.value,
                cameraSettingUid: currentCameraSettingsUid.value
            }
            cameraStore.loadCameraSettingsToCamera(payload)
        }

        function toggleSetting(setting) {
            console.log('🚀 ImageSourceSettings - toggleSetting called with:', setting);
            console.log('ImageSourceSettings - current props.type:', props.type);
            console.log('ImageSourceSettings - current selectedSetting before:', selectedSetting.value);
            selectedSetting.value = setting;
            console.log('ImageSourceSettings - current selectedSetting after:', selectedSetting.value);
            
            // Debug camera data when Camera button is clicked
            if (setting === 'Camera') {
                console.log('ImageSourceSettings - DEBUG Camera button clicked:');
                console.log('ImageSourceSettings - camerasList:', camerasList.value);
                console.log('ImageSourceSettings - camerasList length:', camerasList.value?.length);
                console.log('ImageSourceSettings - selectedCameraUid:', selectedCameraUid.value);
            }
            
            // Debug camera settings data when Camera Settings button is clicked
            if (setting === 'Camera Settings') {
                console.log('ImageSourceSettings - DEBUG Camera Settings button clicked:');
                console.log('ImageSourceSettings - currentCameraSettings:', currentCameraSettings.value);
                console.log('ImageSourceSettings - cameraControls:', computed(() => store.getters["cameraSettings/getcameraControls"]).value);
                
                // Debug individual setting values AND their processed values
                const controls = computed(() => store.getters["cameraSettings/getcameraControls"]).value;
                if (controls && currentCameraSettings.value) {
                    console.log('ImageSourceSettings - Analyzing all fields:');
                    console.log('-------------------------------------------');
                    controls.forEach(control => {
                        const rawValue = currentCameraSettings.value[control.name];
                        const processedValue = control.type === 'dropdown' 
                            ? getDropdownCurrentValue(control.name, rawValue)
                            : control.type === 'bool'
                            ? getCheckBoxValue(getDropdownCurrentValue(control.name, rawValue))
                            : rawValue;
                        
                        console.log(`Field: ${control.name}`);
                        console.log(`  Type: ${control.type}`);
                        console.log(`  Raw Value: ${JSON.stringify(rawValue)} (${typeof rawValue})`);
                        console.log(`  Processed Value: ${JSON.stringify(processedValue)} (${typeof processedValue})`);
                        console.log(`  Control Values/Range: ${JSON.stringify(control.values)}`);
                        
                        // Check for issues
                        if (rawValue === undefined) {
                            console.log(`  ⚠️ WARNING: Value is undefined!`);
                        }
                        if (Array.isArray(rawValue) && control.type === 'dropdown') {
                            console.log(`  ⚠️ WARNING: Array value for dropdown!`);
                        }
                        if (control.type === 'dropdown' && control.values) {
                            const isValidOption = control.values.some(opt => {
                                if (Array.isArray(opt) && opt.length === 2) {
                                    // Option is [value, label] format
                                    return opt[0] === processedValue;
                                }
                                return opt === processedValue;
                            });
                            if (!isValidOption && processedValue !== undefined) {
                                console.log(`  ⚠️ WARNING: Processed value "${processedValue}" not in options!`);
                            }
                        }
                        console.log('---');
                    });
                }
            }
            
            // Debug CNC locations when CNC Locations button is clicked
            if (setting === 'CNC Locations') {
                console.log('ImageSourceSettings - DEBUG CNC Locations button clicked:');
                console.log('ImageSourceSettings - locationsList:', cncStore.locations.value);
                console.log('ImageSourceSettings - locationsList length:', cncStore.locations.value?.length);
                console.log('ImageSourceSettings - current location.value:', location.value);
                console.log('ImageSourceSettings - current settleTime.value:', settleTime.value);
                console.log('ImageSourceSettings - current activateLocation.value:', activateLocation.value);
                console.log('ImageSourceSettings - cnc store state:', store.state.cnc);
                console.log('ImageSourceSettings - cnc store raw locations:', store.state.cnc?.locations);
                
                // Check if locations need to be loaded
                if (!cncStore.locations.value || cncStore.locations.value.length === 0) {
                    console.log('ImageSourceSettings - ℹ️ INFO: Locations list is empty - this may be normal if no CNC locations have been configured');
                    console.log('ImageSourceSettings - Attempting to reload locations to double-check...');
                    // Try to reload locations when clicking the button
                    try {
                        cncStore.loadLocations().then(() => {
                            console.log('ImageSourceSettings - loadLocations() completed successfully');
                            console.log('ImageSourceSettings - reloaded locations:', cncStore.locations.value);
                            console.log('ImageSourceSettings - reloaded locations length:', cncStore.locations.value?.length);
                            
                            if (!cncStore.locations.value || cncStore.locations.value.length === 0) {
                                console.log('ImageSourceSettings - ✅ CONFIRMED: No CNC locations are configured in this system');
                                console.log('ImageSourceSettings - 💡 TIP: CNC locations would be created in the CNC/Tools section of the application');
                                console.log('ImageSourceSettings - The dropdown will remain empty until locations are added');
                            }
                        }).catch(error => {
                            console.error('ImageSourceSettings - error in loadLocations() promise:', error);
                        });
                        console.log('ImageSourceSettings - loadLocations() called successfully');
                    } catch (error) {
                        console.error('ImageSourceSettings - error calling loadLocations():', error);
                    }
                } else {
                    console.log('ImageSourceSettings - Locations loaded successfully:');
                    cncStore.locations.value.forEach((loc, index) => {
                        console.log(`  Location ${index}: name="${loc.name}" uid="${loc.uid}"`);
                        
                        // Check if current location value matches any of the available locations
                        if (location.value === loc.name) {
                            console.log(`  ✓ Current location "${location.value}" matches this entry`);
                        }
                    });
                    
                    // Verify the current location value exists in the list
                    const locationExists = cncStore.locations.value.some(loc => loc.name === location.value);
                    if (location.value && !locationExists) {
                        console.log(`ImageSourceSettings - ⚠️ WARNING: Current location "${location.value}" not found in locations list`);
                    }
                }
            }
        }

        function closeDialog() {

            newCamera.value = {
                name: '',
                cameraType: ''
            }
            showAddCamDialog.value = false;
        }

        async function onFolderSelected(event) {

            if (event.target.files.length === 0) {
                setNotification(4000, "The chosen folder is empty.", 'bi-exclamation-circle-fill');
            }
            else {
                selectedDirectory.value = event.target.files;

                const dirName = selectedDirectory.value[0].webkitRelativePath.slice(0, selectedDirectory.value[0].webkitRelativePath.indexOf("/"));
                let foundDirName = imageGeneratorsList.value.map(generator => generator.dir_path.includes(dirName));

                let foundIdx = foundDirName.findIndex(el => el === true);

                if (foundIdx != -1) {
                    folderExistsFlag.value = true;
                }
                else {
                    for (const file of selectedDirectory.value) {
                        if (file.type.startsWith("image")) {
                            const formData = new FormData();
                            formData.append('file', file);
                            await imageSourcesStore.uploadImagesFromGenerator(formData);
                        }
                        else {
                            setNotification(3000, `${file.name} is not an image.`, 'bi-exclamation-circle-fill');
                        }
                    }
                }

                if (folderExistsFlag.value === true) {
                    const gen = imageGeneratorsList.value[foundIdx];
                    generatorChanged(gen.uid);

                    imageSourcesStore.setCurrentImageGenerator(gen);

                    imageSourcesStore.setCurrentImageGeneratorProp({
                        key: "dir_path",
                        value: gen.dir_path
                    });
                    
                    folderExistsFlag.value = false;
                }
                else {
                    await imageSourcesStore.addImageGenerator();
                    imageSourcesStore.loadImageGeneratorAsCurrent(props.currentImageGenerator.uid);
                    newFolderFlag.value = !newFolderFlag.value;
                }
            }
        }

        watch(newFolderFlag, () => {
            generatorChanged(props.currentImageGenerator.uid);
        });

        // Watch currentCameraSettingsUid for all changes
        watch(currentCameraSettingsUid, (newValue, oldValue) => {
            // Handle camera settings UID changes
        }, { immediate: true });

        watch(currentImageSource, async (newValue) => {
            console.log('ImageSourceSettings - currentImageSource changed:', newValue);
            if(newValue)
            {
                console.log('ImageSourceSettings - setting values from:', newValue);
                console.log('ImageSourceSettings - setting fps.value to:', newValue.fps, 'current fps.value:', fps.value);
                fps.value = newValue.fps || 1;
                location.value = newValue.location_name;
                settleTime.value = newValue.settle_time;
                activateLocation.value = newValue.activate_location;

                if (newValue.image_source_type === "dynamic" && newValue.camera_uid) {
                    console.log('ImageSourceSettings - dynamic source, camera_uid:', newValue.camera_uid);
                    
                    if (newValue.camera_settings_uid && newValue.camera_settings_uid !== "") {
                        console.log('ImageSourceSettings - loading camera settings for camera:', newValue.camera_uid);
                        console.log('ImageSourceSettings - setting camera_settings_uid to:', newValue.camera_settings_uid);
                        try {
                            await loadCameraSettings(newValue.camera_uid);
                            console.log('ImageSourceSettings - About to set currentCameraSettingsUid to:', newValue.camera_settings_uid);
                            
                            // Set currentCameraSettingsUid BEFORE setting selectedCameraUid to avoid race condition
                            currentCameraSettingsUid.value = newValue.camera_settings_uid;
                            console.log('ImageSourceSettings - currentCameraSettingsUid.value is now:', currentCameraSettingsUid.value);
                        } catch (error) {
                            console.error('ImageSourceSettings - error in loadCameraSettings:', error);
                            // Continue execution but log the error
                        }
                    }
                    
                    // Set selectedCameraUid AFTER setting currentCameraSettingsUid
                    selectedCameraUid.value = newValue.camera_uid;
                    console.log('ImageSourceSettings - selectedCameraUid set to:', newValue.camera_uid);
                }
            }
        });

        watch(fps, (newValue) => {
            console.log('ImageSourceSettings - FPS changed, updating store immediately:', { newValue, currentImageSource: props.currentImageSource });
            
            // Immediately update the image source in the store with the new FPS
            if (props.currentImageSource && newValue != null) {
                const updatedImageSource = {
                    ...props.currentImageSource,
                    fps: newValue
                };
                
                // Update the store immediately
                imageSourcesStore.setCurrentImageSource(updatedImageSource);
                imageSourcesStore.updateImageSource(updatedImageSource);
                
                console.log('ImageSourceSettings - Store updated with new FPS:', newValue);
            }
            
            fpsChanged(newValue);
        });

        watch(selectedCameraUid, async (newValue) => {
            console.log('ImageSourceSettings - selectedCameraUid watcher fired with:', newValue);
            if (newValue && newValue !== "") {
                // Ensure cameras list is loaded
                if (camerasList.value.length === 0) {
                    console.log('ImageSourceSettings - cameras list is empty, fetching...');
                    try {
                        await cameraStore.fetchCamerasList();
                        console.log('ImageSourceSettings - cameras list fetched in watcher:', camerasList.value.length);
                        console.log('ImageSourceSettings - cameras list content:', camerasList.value);
                        console.log('ImageSourceSettings - store state after fetch:', store.state.cameraSettings);
                    } catch (error) {
                        console.error('ImageSourceSettings - error fetching cameras list in watcher:', error);
                    }
                }
                
                cameraStore.fetchCameraSettingsList(newValue);
                cameraStore.fetchCamera(newValue);
                cameraChanged(newValue);
            }
            showCameraControls.value = false;
            // Don't reset currentCameraSettingsUid here - it should be managed by the currentImageSource watcher
            console.log('ImageSourceSettings - selectedCameraUid watcher complete, currentCameraSettingsUid:', currentCameraSettingsUid.value);
        });

        watch(currentCameraSettingsUid, async (newValue) => {
            console.log('ImageSourceSettings - currentCameraSettingsUid watcher fired with:', newValue);
            console.log('ImageSourceSettings - ignoreSettingsChange.value:', ignoreSettingsChange.value);
            if (newValue != "" && !ignoreSettingsChange.value) {
                console.log('ImageSourceSettings - fetching camera settings for UID:', newValue);
                await cameraStore.fetchCameraSettings(newValue);
                console.log('ImageSourceSettings - loading camera settings to camera');
                await cameraStore.loadCameraSettingsToCamera({ 'cameraUid': selectedCameraUid.value, 'cameraSettingUid': newValue });
                showCameraControls.value = true;
                console.log('ImageSourceSettings - camera settings loaded successfully');
                console.log('ImageSourceSettings - currentCameraSettings after load:', currentCameraSettings.value);
                console.log('ImageSourceSettings - typeof currentCameraSettings:', typeof currentCameraSettings.value);
                console.log('ImageSourceSettings - Object.keys(currentCameraSettings):', Object.keys(currentCameraSettings.value || {}));
            }
            ignoreSettingsChange.value = false;
        });

        function newCameraSettings() {
            newCameraSettingsFlag.value = !newCameraSettingsFlag.value;
            showCameraControls.value = false;
        };

        async function saveCameraSettings(settings) {
            console.log('ImageSourceSettings - saveCameraSettings called with:', settings);
            console.log('ImageSourceSettings - newCameraSettingsFlag.value:', newCameraSettingsFlag.value);
            console.log('ImageSourceSettings - currentCameraSettingsUid.value:', currentCameraSettingsUid.value);
            
            cameraSettings.value = settings;
            
            // Ensure we have the correct UID for existing settings
            if (!newCameraSettingsFlag.value && currentCameraSettingsUid.value) {
                cameraSettings.value.uid = currentCameraSettingsUid.value;
                console.log('ImageSourceSettings - using current settings UID:', currentCameraSettingsUid.value);
            }
            
            console.log('ImageSourceSettings - final settings to save:', cameraSettings.value);
            
            if (newCameraSettingsFlag.value) {
                // Creating new camera settings
                try {
                    const result = await cameraStore.postCameraSettings(cameraSettings.value);
                    console.log('ImageSourceSettings - new camera settings created:', result);
                    currentCameraSettingsUid.value = cameraSettings.value.uid;
                    ignoreSettingsChange.value = true;
                    newCameraSettingsFlag.value = false;
                    newCameraSettingsName.value = '';
                    context.emit('save-settings-status', true);
                } catch (error) {
                    console.error('ImageSourceSettings - error creating camera settings:', error);
                    context.emit('save-settings-status', false);
                }
            }
            else {
                // Updating existing camera settings
                if (!cameraSettings.value.uid || cameraSettings.value.uid === '') {
                    console.error('ImageSourceSettings - cannot update camera settings: missing or invalid UID');
                    context.emit('save-settings-status', false);
                    return;
                }
                
                try {
                    const result = await cameraStore.putCameraSettings(cameraSettings.value);
                    console.log('ImageSourceSettings - camera settings updated:', result);
                    context.emit('save-settings-status', true);
                } catch (error) {
                    console.error('ImageSourceSettings - error updating camera settings:', error);
                    context.emit('save-settings-status', false);
                }
            }
        }

        async function deleteCameraSettings(settings) {
            cameraSettings.value = settings;
            if (newCameraSettingsFlag.value) {
                showCameraControls.value = false;
                newCameraSettingsFlag.value = false;
                currentCameraSettingsUid.value = '';
            }
            else {
                cameraStore.removeCameraSettings(cameraSettings.value.uid);
                showCameraControls.value = false;
                newCameraSettingsFlag.value = false;
            }
        }

        function savePhoto() {
            context.emit('save-photo');
        }

        function saveConfig() {
            if (props.type === "static") {
                const newStaticConfig = {
                    camera_settings_uid: "",
                    camera_uid: "",
                    image_generator_uid: props.currentImageGenerator.uid,
                    image_source_type: props.type,
                    location_name: location.value,
                    settle_time: settleTime.value,
                    activate_location: activateLocation.value,
                    name: props.currentImageSource.name,
                    uid: props.currentImageSource.uid,
                    fps: fps.value
                };
                imageSourcesStore.updateImageSource(newStaticConfig).then(() => {
                    context.emit('save-src-status', true);
                }).catch(() => {
                    context.emit('save-src-status', false);
                });

            } else if (props.type === "dynamic") {
                const newDynamicConfig = {
                    camera_settings_uid: currentCameraSettingsUid.value,
                    camera_uid: selectedCameraUid.value,
                    image_generator_uid: "",
                    image_source_type: props.type,
                    location_name: location.value,
                    name: props.currentImageSource.name,
                    uid: props.currentImageSource.uid,
                    fps: fps.value,
                    settle_time: settleTime.value,
                    activate_location: activateLocation.value,
                };

                imageSourcesStore.updateImageSource(newDynamicConfig).then(() => {
                    context.emit('save-src-status', true);
                }).catch(() => {
                    context.emit('save-src-status', false);
                });
            }
        }

        function onFpsInputChange(event) {
            const newFps = parseInt(event.target.value);
            console.log('ImageSourceSettings - FPS input changed directly:', { newFps, inputValue: event.target.value });
            if (!isNaN(newFps) && newFps > 0) {
                fps.value = newFps;
            }
        }

        function fpsChanged(newFps) {
            context.emit('fps-updated', newFps);
        }

        function generatorChanged(uid) {
            context.emit('generator-updated', uid);
        }

        function cameraChanged(uid) {
            context.emit('camera-updated', uid);
        }

        function cameraSettingsChanged(uid) {
            context.emit('camera-settings-updated', uid);
        }

        function toggleImageSource() {
            cameraActive.value = !cameraActive.value;
            context.emit('show-camera', cameraActive.value);
        }

        async function updateCurrentValue(name, newVal) {
            console.log('ImageSourceSettings - updateCurrentValue called with:', name, newVal);
            
            let processedValue = newVal;
            
            // Handle resolution: convert "640x480" back to [640, 480] for backend
            if (name.toLowerCase() === 'resolution' && typeof newVal === 'string' && newVal.includes('x')) {
                const parts = newVal.split('x');
                if (parts.length === 2) {
                    processedValue = [parseInt(parts[0]), parseInt(parts[1])];
                    console.log('ImageSourceSettings - converted resolution from', newVal, 'to', processedValue);
                }
            }
            
            console.log('ImageSourceSettings - sending to backend:', { name: name.toLowerCase(), value: processedValue });
            
            try {
                await cameraStore.patchCameraSetting({
                    name: name.toLowerCase(),
                    value: processedValue,
                    cameraUid: selectedCameraUid.value
                });
                console.log('ImageSourceSettings - camera setting updated successfully');
            } catch (error) {
                console.error('ImageSourceSettings - error updating camera setting:', error);
            }
        }

        async function updateCheckBoxValue(name, newVal) {
            await cameraStore.patchCameraSetting({
                name: name.toLowerCase(),
                value: newVal? 1 : 0,
                cameraUid: selectedCameraUid.value
            });
        }

        onMounted(async () => {
            imageSourcesStore.getAllImageGenerators();
            
            // Load cameras
            cameraStore.fetchCamerasList().catch(error => {
                console.error('ImageSourceSettings - error loading cameras:', error);
            });
            
            cameraStore.readCameraTypes();
            
            // Load CNC locations with timeout to prevent hanging
            const timeoutPromise = new Promise((_, reject) => {
                setTimeout(() => reject(new Error('loadLocations timeout after 5 seconds')), 5000);
            });
            
            Promise.race([cncStore.loadLocations(), timeoutPromise])
                .catch((error) => {
                    if (!error.message.includes('timeout')) {
                        console.error('ImageSourceSettings - error loading CNC locations:', error);
                    }
                });
        });

        return {
            camerasList,
            cameraTypesList: computed(() => store.getters["cameraSettings/getCameraTypes"]),
            cameraSettingsList,
            locationsList: cncStore.locations,
            cameraControls: computed(() => store.getters["cameraSettings/getcameraControls"]),
            currentCameraSettings,
            selectedCameraUid,
            selectedSetting,
            showAddCamDialog,
            newCamera,
            cameraActive,
            selectedDirectory,
            activateLocation,
            location,
            settleTime,
            fps,
            currentImageSource,
            imageGeneratorsList,
            folderExistsFlag,
            newFolderFlag,
            cameraSettings,
            showCameraControls,
            currentCameraSettingsUid,
            newCameraSettingsFlag,
            newCameraSettingsName,
            icon,
            showNotification,
            notificationMessage,
            notificationIcon,
            notificationTimeout,
            newCameraSettings,
            addCamera,
            toggleSetting,
            closeDialog,
            addCamera,
            deleteCamera,
            getCheckBoxValue,
            getDropdownValues,
            getDropdownCurrentValue,
            loadSettingsToCamera,
            onFolderSelected,
            saveConfig,
            savePhoto,
            toggleImageSource,
            generatorChanged,
            cameraChanged,
            cameraSettingsChanged,
            fpsChanged,
            onFpsInputChange,
            updateCurrentValue,
            updateCheckBoxValue,
            saveCameraSettings,
            deleteCameraSettings,
            setCameraSettingsVisibility,
            clearNotification
        }
    }
}
</script>

<style scoped>
.settings-container {
    display: block;
    width: 100%;
    height: 84.3%;
    color: white;
}

.setting {
    border: none;
    color: var(--color-primary);
    width: 100%;
    margin: 3px;
}

.setting:hover {
    background-color: var(--color-primary);
    color: white;
    transform: scale(1.02);
}

.number-input {
    width: 80%;
    margin: 7px;
    outline: none;
}

label {
    margin: 7px;
    color: var(--color-primary);
    width:50%;
    display:flex;
    justify-content: space-between;
    align-items:center;
}

select {
    width: 80%;
    margin: 5px;
    color: var(--color-primary);
    height: 100%;

}

.cnc-label {
    width: 60%;
    display: flex;
    justify-content: flex-start;
}

.cnc-value {
    width: 40%;
}

.settings-submenu {
    display: block;
    background-color: rgb(37, 36, 36);
    color: var(--color-primary);
    min-height: 52.7%;
    margin: 2%;
    position: relative;
    overflow-y: auto;
}

.submenu-input {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: center;
    width: 100%;
}

.camera-control {
    display: flex;
    width: 60%;
    margin: auto;
    justify-content: space-around;
}

.sub-submenu {
    display: flex;
    padding-left: 3px;
    align-items: center;
    width: 100%;
}

.input-container{
    width:100%;
    height:100%;
    background-color:rgb(77, 75, 75);
    border-radius:15px;
    margin:2%;
    display: flex;
    justify-content: center;
    align-items: center;
}

#images-path {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.directory-name {
    display:flex;
    align-items: center;
    width:100%;
}

#path-container{
    background-color:rgb(77, 75, 75);
    width:100%;
    border-radius:10px;
    padding:5px;
}

.slidecontainer {
    display: flex;
    justify-content: right;
    width: 60%;
}

.slider {
    -webkit-appearance: none;
    appearance: none;
    width: 100%;
    background-color: var(--color-primary);
    height: 5px;
    border-radius: 25px;
    outline: none;
    cursor: pointer;
}

.submenu-checkbox {
    display: flex;
    justify-content: center;
}


.top-buttons {
    display: flex;
    width: 100%;
    height: 5%;
    justify-content: space-between;
    margin-bottom: 1%;
}

.image-source {
    display: inline-flex;
    width: 50%;
}

#left-control {
    display: flex;
    justify-content: flex-start;
    width: 30%;
}

#right-control {
    display: flex;
    justify-content: flex-end;
    width: 40%;
}

.save-control {
    width: 49%;
    margin-left: 1%;
}

#toggle-source-button {
    width: 50%;
    height: 100%;
}

.toggle-active {
    background-color: var(--color-primary);
    color: white;
}

.toggle-active:hover {
    background-color: rgb(215, 171, 90);
    color: white;
}

#toggle-source-label {
    width: 100%;
    overflow: hidden;
    margin: 0;
    font-size: 90%;
    display: flex;
    justify-content: space-around;
}

.main-ct {
    width: 100%;
    height: 100%;
    display: block;
    border-radius: 20px;
}

.submenu-button {
    color: var(--color-primary);
    outline: none;
    border: none;
    height: 100%;
}

h1 {
    color: var(--color-primary);
}

.warning {
    /* opacity:0.7; */
    width: 100%;
}

.not-loaded {
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: rgb(37, 36, 36);
    height: 100%;
    width: 100%;
    border-radius: 20px;
}

.settings-loaded {
    display: block;
    height: 100%;
    width: 100%;
}

.disabled {
    pointer-events: none;
    color: gray;
    background-color: rgb(69, 68, 68);
}

input {
    width: 80%;
    margin: 5px;
    margin: none;
    outline: none;
}

.dropdown-select{
    background-color: rgb(37, 36, 36);
    border:none;
    margin:1vh;
}

#camera-type {
    background-color: rgb(37, 36, 36);
    border: none;
    margin: 4px;
}

label {
    margin-right: 15%;
}

.dialog-input-container {
    display: flexbox;
    margin: 2%;
}

.dialog-ctrl-buttons-container {
    display: flex;
    justify-content: end;
    margin: 5%;
}

.dialog-add-button {
    background-color: var(--color-primary);
    color: white;
}


.placeholder-anim-leave-from,
.placeholder-anim-enter-to {
    opacity: 1;
    /* transform: translateX(0); */
}

.placeholder-anim-leave-to,
.placeholder-anim-enter-from {
    opacity: 0;
    /* transform: translateX(20px); */
}

.placeholder-anim-leave-active,
.placeholder-anim-enter-active {
    transition: all 0.5s ease-in;
}


.switch {
    position: relative;
    display: inline-block;
    width: 50px;
    height: 25px;
}

.switch input {
    opacity: 0;
    width: 0;
    height: 0;
}

.toggle {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgb(35, 34, 34);
    -webkit-transition: .4s;
    transition: .4s;
}

.toggle:before {
    position: absolute;
    content: "";
    height: 17px;
    width: 17px;
    left: 4px;
    bottom: 4px;
    background-color: var(--color-primary);
    -webkit-transition: .4s;
    transition: .4s;
}


input:checked+.toggle {
    background-color: var(--color-primary);
}

input:focus+.toggle {
    box-shadow: 0 0 1px #2196F3;
}

input:checked+.toggle:before {
    -webkit-transform: translateX(26px);
    -ms-transform: translateX(26px);
    transform: translateX(26px);
    background-color: white;
}

.toggle.round {
    border-radius: 34px;
}

.toggle.round:before {
    border-radius: 50%;
}

.camera-controls-container {
    width: 100%;
}

.cs-button {
    background-color: rgb(0, 0, 0);
    margin: 0.5vw;
    color: var(--color-primary);
    border: none;
}

.cs-button:hover {
    background-color: rgb(23, 22, 22);
}

button:disabled,
button[disabled] {
    border: 1px solid #999999;
    background-color: #cccccc;
    color: #666666;
    cursor: not-allowed;
}

.settings-list {
    display: flex;
}

.settings-label {
    margin:7px;
    margin-right:15%;
    color: var(--color-primary);
    width:50%;
    display:flex;
    justify-content: space-between;
    align-items:center;

}

.new-settings-container {
    display: flex;
    height: 10%;
    width: 100%;
}

#new-name{
    display:flex;
    justify-content: space-around;
    width: 30%;
}

#new-camera-settings-name{
    width: 70%;
}

#setting-icon {
    padding: 0.2vh;
}

.cs-wrapper {
    width: 100%;
    height: 100%;
    padding-bottom: 0.5vh;
    padding-top: 0.5vh;
}

.cs-container {
    background-color: rgb(77, 75, 75);
    width: 100%;
    height: 100%;
    /* margin-bottom:10px; */
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 10px;
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