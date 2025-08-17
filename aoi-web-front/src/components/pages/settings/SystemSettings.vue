<template>
    <div class="flex-container">
        <div class="tab-wrapper-container">
            <base-tabs-wrapper>
                    <base-tab title="CNCs">
                        <cnc-settings
                            :cncs="cncs"
                            :available-ports="availablePorts"
                            :cnc-types="cncTypes"
                            :disable="!currentConfiguration"
                            @remove-cnc="removeCNC"
                            @add-cnc="addCNC"
                            @save-cncs="saveCNCs"
                            @update-port="updatePort"
                            @update-type="updateCNCType"
                        ></cnc-settings>
                    </base-tab>
                    <base-tab title="Robots">
                        <robot-settings
                            :robots="robots"
                            :robot-types="robotTypes"
                            :robot-ports="robotPorts"
                            :disable="!currentConfiguration"
                            @remove-robot="removeRobot"
                            @add-robot="addRobot"
                            @save-robots="saveRobots"
                            @update-connection-id="updateRobotIP"
                            @update-type="updateRobotType"
                        ></robot-settings>
                    </base-tab>
                    <base-tab title="Profilometers">
                        <profilometer-settings
                            :profilometers="profilometers"
                            :profilometer-types="profilometerTypes"
                            :disable="!currentConfiguration"
                            @remove-profilometer="removeProfilometer"
                            @add-profilometer="addProfilometer"
                            @save-profilometers="saveProfilometers"
                            @update-id="updateProfID"
                            @update-path="updateProfPath"
                            @update-type="updateProfType"
                        ></profilometer-settings>
                    </base-tab>
                </base-tabs-wrapper>
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
import { ref, onMounted, computed } from 'vue';
import { useConfigurationsStore, useAuthStore, useCncStore, useRobotsStore, useProfilometersStore, useLogStore } from '@/composables/useStore';

import CncSettings from '../../settings/CncSettings.vue';
import RobotSettings from '../../settings/RobotSettings.vue';
import ProfilometerSettings from '../../settings/ProfilometerSettings.vue';
import useNotification, { NotificationType } from '../../../hooks/notifications';
import { ValidationMessages, GeneralMessages } from '@/constants/notifications';
import { validateRequired, validateIP, validateLength, sanitizeInput } from '../../../utils/validation.js';

export default {
    components: {
        CncSettings,
        RobotSettings,
        ProfilometerSettings
    },

    setup() {
        const configurationsStore = useConfigurationsStore();
        const authStore = useAuthStore();
        const cncStore = useCncStore();
        const robotsStore = useRobotsStore();
        const profilometersStore = useProfilometersStore();
        const logStore = useLogStore();

        const {showNotification, notificationMessage, notificationIcon, notificationTimeout, notificationType,
            setTypedNotification, clearNotification} = useNotification();

        // These are already computed refs from the composables, no need to wrap again
        const currentConfiguration = configurationsStore.currentConfiguration;
        const currentUser = authStore.currentUser;
        const cncs = cncStore.cncs;
        const robots = robotsStore.robots;
        const profilometers = profilometersStore.profilometers;
        const availablePorts = cncStore.ports;
        const robotPorts = robotsStore.ultraArmPorts;
        const cncTypes = cncStore.cncTypes;
        const robotTypes = robotsStore.robotTypes;
        const profilometerTypes = profilometersStore.profilometerTypes;

        function addCNC(name)
        {
            // Validate CNC name
            const nameValidation = validateRequired(name, 'CNC Name');
            if (!nameValidation.isValid) {
                setTypedNotification(
                    nameValidation.errors[0],
                    NotificationType.ERROR,
                    3000
                );
                return;
            }
            
            const lengthValidation = validateLength(name, 1, 50, 'CNC Name');
            if (!lengthValidation.isValid) {
                setTypedNotification(
                    lengthValidation.errors[0],
                    NotificationType.ERROR,
                    3000
                );
                return;
            }
            
            const sanitizedName = sanitizeInput(name);
            cncStore.addCNC(sanitizedName, '', '');

            setTypedNotification(
                `Added new CNC named ${sanitizedName}. Do not forget to save in order for the changes to take place.`,
                NotificationType.WARNING,
                3000
            );

            logStore.addEvent(
                'CNC SETTINGS',
                currentUser.value ? currentUser.value.username : 'Unknown',
                'CNC Added',
                `CNC ${sanitizedName} was added.`
            );
        }

        function removeCNC(uid)
        {
            cncStore.removeCNC(uid);

            logStore.addEvent(
                'CNC SETTINGS',
                currentUser.value ? currentUser.value.username : 'Unknown',
                'CNC Removed',
                `CNC with uid ${uid} was removed.`
            );
        }

        function saveCNCs() {
            const errors = [];
            
            // Validate each CNC
            cncs.value.forEach((cnc, index) => {
                const nameValidation = validateRequired(cnc.name, `CNC ${index + 1} Name`);
                if (!nameValidation.isValid) {
                    errors.push(nameValidation.errors[0]);
                }
                
                const portValidation = validateRequired(cnc.port, `CNC ${index + 1} Port`);
                if (!portValidation.isValid) {
                    errors.push(portValidation.errors[0]);
                }
                
                const typeValidation = validateRequired(cnc.type, `CNC ${index + 1} Type`);
                if (!typeValidation.isValid) {
                    errors.push(typeValidation.errors[0]);
                }
            });
            
            // Check for duplicate ports
            const ports = cncs.value.map(cnc => cnc.port).filter(port => port !== '');
            if (hasDuplicates(ports)) {
                errors.push('Two or more CNCs have the same port assigned.');
            }
            
            if (errors.length > 0) {
                setTypedNotification(
                    errors[0],
                    NotificationType.ERROR,
                    3000
                );
                return;
            }
            
            try {
                cncStore.saveCNCs();
                setTypedNotification(
                    'CNCs configuration saved successfully.',
                    NotificationType.SUCCESS,
                    2000
                );

                logStore.addEvent(
                    'CNC SETTINGS',
                    currentUser.value ? currentUser.value.username : 'Unknown',
                    'CNCs Saved',
                    `CNCs configuration was saved.`
                );
            } catch(err) {
                setTypedNotification(
                    err.message || 'Failed to save CNCs configuration.',
                    NotificationType.ERROR,
                    3000
                );
            }
        }

        function updatePort(uid, value) {
            cncStore.updateCNCPort(uid, value);

            logStore.addEvent(
                'CNC SETTINGS',
                currentUser.value ? currentUser.value.username : 'Unknown',
                'CNC Port Changed',
                `CNC with uid ${uid} changed its port to ${value}.`
            );
        }

        function updateCNCType(uid, value) {
            cncStore.updateCNCType(uid, value);

            logStore.addEvent(
                'CNC SETTINGS',
                currentUser.value ? currentUser.value.username : 'Unknown',
                'CNC Type Changed',
                `CNC with uid ${uid} changed its type to ${value}.`
            );
        }

        function addRobot(name)
        {
            // Validate robot name
            const nameValidation = validateRequired(name, 'Robot Name');
            if (!nameValidation.isValid) {
                setTypedNotification(
                    nameValidation.errors[0],
                    NotificationType.ERROR,
                    3000
                );
                return;
            }
            
            const lengthValidation = validateLength(name, 1, 50, 'Robot Name');
            if (!lengthValidation.isValid) {
                setTypedNotification(
                    lengthValidation.errors[0],
                    NotificationType.ERROR,
                    3000
                );
                return;
            }
            
            const sanitizedName = sanitizeInput(name);
            robotsStore.addRobot(sanitizedName, '', '');

            setTypedNotification(
                `Added new robot named ${sanitizedName}. Do not forget to save in order for the changes to take place.`,
                NotificationType.WARNING,
                3000
            );

            logStore.addEvent(
                'ROBOT SETTINGS',
                currentUser.value ? currentUser.value.username : 'Unknown',
                'Robot Added',
                `Robot ${sanitizedName} was added.`
            );
        }

        function removeRobot(uid)
        {
            robotsStore.removeRobot(uid);

            logStore.addEvent(
                'ROBOT SETTINGS',
                currentUser.value ? currentUser.value.username : 'Unknown',
                'Robot Removed',
                `Robot with uid ${uid} was removed.`
            );
        }

        function saveRobots() {
            const errors = [];
            
            // Validate each robot
            robots.value.forEach((robot, index) => {
                const nameValidation = validateRequired(robot.name, `Robot ${index + 1} Name`);
                if (!nameValidation.isValid) {
                    errors.push(nameValidation.errors[0]);
                }
                
                const ipValidation = validateRequired(robot.ip, `Robot ${index + 1} IP`);
                if (!ipValidation.isValid) {
                    errors.push(ipValidation.errors[0]);
                } else {
                    const ipFormatValidation = validateIP(robot.ip);
                    if (!ipFormatValidation.isValid) {
                        errors.push(`Robot ${index + 1}: ${ipFormatValidation.errors[0]}`);
                    }
                }
                
                const typeValidation = validateRequired(robot.type, `Robot ${index + 1} Type`);
                if (!typeValidation.isValid) {
                    errors.push(typeValidation.errors[0]);
                }
            });
            
            if (errors.length > 0) {
                setTypedNotification(
                    errors[0],
                    NotificationType.ERROR,
                    3000
                );
                return;
            }
            
            try {
                robotsStore.saveRobots();
                setTypedNotification(
                    'Robots configuration saved successfully.',
                    NotificationType.SUCCESS,
                    2000
                );

                logStore.addEvent(
                    'ROBOT SETTINGS',
                    currentUser.value ? currentUser.value.username : 'Unknown',
                    'Robots Saved',
                    `Robots configuration was saved.`
                );
            } catch(err) {
                setTypedNotification(
                    err.message || 'Failed to save robots configuration.',
                    NotificationType.ERROR,
                    3000
                );
            }
        }

        function updateRobotIP(uid, value) {
            // Validate IP address if provided
            if (value && value.trim() !== '') {
                const ipValidation = validateIP(value);
                if (!ipValidation.isValid) {
                    setTypedNotification(
                        ipValidation.errors[0],
                        NotificationType.ERROR,
                        3000
                    );
                    return;
                }
            }
            
            const sanitizedValue = sanitizeInput(value);
            robotsStore.updateRobotConnectionID(uid, sanitizedValue);

            logStore.addEvent(
                'ROBOT SETTINGS',
                currentUser.value ? currentUser.value.username : 'Unknown',
                'Robot IP Changed',
                `Robot with uid ${uid} changed its IP to ${sanitizedValue}.`
            );
        }

        function updateRobotType(uid, value) {
            robotsStore.updateRobotType(uid, value);

            logStore.addEvent(
                'Robot SETTINGS',
                currentUser.value ? currentUser.value.username : 'Unknown',
                'Robot Type Changed',
                `Robot with uid ${uid} changed its type to ${value}.`
            );
        }

        function addProfilometer(name)
        {
            // Validate profilometer name
            const nameValidation = validateRequired(name, 'Profilometer Name');
            if (!nameValidation.isValid) {
                setTypedNotification(
                    nameValidation.errors[0],
                    NotificationType.ERROR,
                    3000
                );
                return;
            }
            
            const lengthValidation = validateLength(name, 1, 50, 'Profilometer Name');
            if (!lengthValidation.isValid) {
                setTypedNotification(
                    lengthValidation.errors[0],
                    NotificationType.ERROR,
                    3000
                );
                return;
            }
            
            const sanitizedName = sanitizeInput(name);
            profilometersStore.addProfilometer(sanitizedName, '', '', '');

            setTypedNotification(
                `Added new profilometer named ${sanitizedName}. Do not forget to save in order for the changes to take place.`,
                NotificationType.WARNING,
                3000
            );

            logStore.addEvent(
                'PROFILOMETER SETTINGS',
                currentUser.value ? currentUser.value.username : 'Unknown',
                'Profilometer Added',
                `Profilometer ${sanitizedName} was added.`
            );
        }

        function removeProfilometer(uid)
        {
            profilometersStore.removeProfilometer(uid);

            logStore.addEvent(
                'PROFILOMETER SETTINGS',
                currentUser.value ? currentUser.value.username : 'Unknown',
                'Profilometer Removed',
                `Profilometer with uid ${uid} was removed.`
            );
        }

        function saveProfilometers() {
            const ids = profilometers.value.map(prof => prof.ip);
            const paths = profilometers.value.map(prof => prof.ip);
            const types = profilometers.value.map(prof => prof.type);

            let error = false;

            if(ids.includes(''))
            {
                setTypedNotification(
                    'There are profilometers with no ID chosen. Cannot save the changes.',
                    NotificationType.ERROR,
                    3000
                );

                error = true;
            }

            if(paths.includes(''))
            {
                setTypedNotification(
                    'There are profilometers with no path chosen. Cannot save the changes.',
                    NotificationType.ERROR,
                    3000
                );

                error = true;
            }

            if(types.includes(''))
            {
                setTypedNotification(
                    'There are profilometers with no type chosen. Cannot save the changes.',
                    NotificationType.ERROR,
                    3000
                );

                error = true;
            }

            if(!error)
            {
                profilometersStore.saveProfilometers();

                logStore.addEvent(
                    'PROFILOMETER SETTINGS',
                    currentUser.value ? currentUser.value.username : 'Unknown',
                    'Profilometers Saved',
                    `Profilometers configuration was saved.`
                );
            }
        }

        function updateProfID(uid, value) {
            profilometersStore.updateProfilometerID(uid, value);

            logStore.addEvent(
                'PROFILOMETER SETTINGS',
                currentUser.value ? currentUser.value.username : 'Unknown',
                'Profilometer ID Changed',
                `Profilometer with uid ${uid} changed its ID to ${value}.`
            );
        }

        function updateProfPath(uid, value) {
            profilometersStore.updateProfilometerServerPath(uid, value);

            logStore.addEvent(
                'PROFILOMETER SETTINGS',
                currentUser.value ? currentUser.value.username : 'Unknown',
                'Profilometer Path Changed',
                `Profilometer with uid ${uid} changed its path to ${value}.`
            );
        }

        function updateProfType(uid, value) {
            profilometersStore.updateProfilometerType(uid, value);

            logStore.addEvent(
                'PROFILOMETER SETTINGS',
                currentUser.value ? currentUser.value.username : 'Unknown',
                'Profilometer Type Changed',
                `Profilometer with uid ${uid} changed its type to ${value}.`
            );
        }

        function hasDuplicates(array) {
            return (new Set(array)).size !== array.length;
        }

        onMounted(() => {
            if(currentConfiguration.value)
            {
                cncStore.loadCNCs();
                cncStore.loadCNCTypes();
                cncStore.loadPorts();

                robotsStore.loadRobots();
                robotsStore.loadRobotTypes();
                robotsStore.loadUltraArmPorts();

                profilometersStore.loadProfilometers();
                profilometersStore.loadProfilometerTypes();
            }
        });

        return {
            cncs,
            robots,
            profilometers,
            availablePorts,
            robotPorts,
            cncTypes,
            robotTypes,
            profilometerTypes,
            currentConfiguration,
            showNotification,
            notificationIcon,
            notificationMessage,
            notificationTimeout,
            notificationType,
            removeCNC,
            addCNC,
            saveCNCs,
            updatePort,
            updateCNCType,
            removeRobot,
            addRobot,
            saveRobots,
            updateRobotIP,
            updateRobotType,
            removeProfilometer,
            addProfilometer,
            saveProfilometers,
            updateProfID,
            updateProfPath,
            updateProfType,
            clearNotification
        }
    }
}
</script>

<style scoped>
.flex-container {
    display: flex;
    justify-content: center;
    align-items: flex-start;
    width: 100%;
    height: 90%;
    color: white;
    margin: 5vh auto;
}

.tab-wrapper-container {
    width: 90%;
    height: 100%;
    background-color: rgb(25, 24, 24);
}

</style>
