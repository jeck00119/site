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
import { ref, onMounted, computed } from 'vue';
import { useStore } from 'vuex';

import CncSettings from '../../settings/CncSettings.vue';
import RobotSettings from '../../settings/RobotSettings.vue';
import ProfilometerSettings from '../../settings/ProfilometerSettings.vue';
import useNotification from '../../../hooks/notifications.js';

export default {
    components: {
        CncSettings,
        RobotSettings,
        ProfilometerSettings
    },

    setup() {
        const store = useStore();

        const {showNotification, notificationMessage, notificationIcon, notificationTimeout, 
            setNotification, clearNotification} = useNotification();

        const currentConfiguration = computed(function() {
            return store.getters["configurations/getCurrentConfiguration"];
        });

        const currentUser = computed(function() {
            return store.getters["auth/getCurrentUser"];
        });

        const cncs = computed(function() {
            return store.getters["cnc/getCNCs"];
        });

        const robots = computed(function() {
            return store.getters["robots/getRobots"];
        });

        const profilometers = computed(function() {
            return store.getters["profilometers/getProfilometers"];
        });

        const availablePorts = computed(function() {
            return store.getters["cnc/getPorts"];
        });

        const robotPorts = computed(function() {
            return store.getters["robots/getUltraArmPorts"];
        });

        const cncTypes = computed(function() {
            return store.getters["cnc/getCNCTypes"];
        });
        
        const robotTypes = computed(function() {
            return store.getters["robots/getRobotTypes"];
        });
        const profilometerTypes = computed(function() {
            return store.getters["profilometers/getProfilometerTypes"];
        });

        function addCNC(name)
        {
            store.dispatch("cnc/addCNC", {
                name: name,
                port: '',
                type: ''
            });

            setNotification(
                3000, 
                `Added new CNC named ${name}. Do not forget to save in order for the changes to take place.`,
                'bi-exclamation-circle-fill'
            );

            store.dispatch("log/addEvent", {
                type: 'CNC SETTINGS',
                user: currentUser.value ? currentUser.value.username : 'Unknown',
                title: 'CNC Added',
                description: `CNC ${name} was added.`
            });
        }

        function removeCNC(uid)
        {
            store.dispatch("cnc/removeCNC", {
                uid: uid
            });

            store.dispatch("log/addEvent", {
                type: 'CNC SETTINGS',
                user: currentUser.value ? currentUser.value.username : 'Unknown',
                title: 'CNC Removed',
                description: `CNC with uid ${uid} was removed.`
            });
        }

        function saveCNCs() {
            const ports = cncs.value.map(cnc => cnc.port);
            const types = cncs.value.map(cnc => cnc.type);

            let error = false;

            if(ports.includes('') || hasDuplicates(ports))
            {
                setNotification(
                    3000,
                    `There are CNCs with no port chosen or two or more CNCs with the same port assigned. Cannot save the changes.`,
                    'bi-exclamation-circle-fill'
                );
                error = true;
            }

            if(types.includes(''))
            {
                setNotification(
                    3000,
                    `There are CNCs with no type chosen. Cannot save the changes.`,
                    'bi-exclamation-circle-fill'
                );
                error = true;
            }

            if(!error)
            {
                try {
                    store.dispatch("cnc/saveCNCs");

                    store.dispatch("log/addEvent", {
                        type: 'CNC SETTINGS',
                        user: currentUser.value ? currentUser.value.username : 'Unknown',
                        title: 'CNCs Saved',
                        description: `CNCs configuration was saved.`
                    });
                }catch(err) {
                    setNotification(3000, err, 'bi-exclamation-circle-fill');
                }
            }
        }

        function updatePort(uid, value) {
            store.dispatch("cnc/updateCNCPort", {
                uid: uid,
                port: value
            });

            store.dispatch("log/addEvent", {
                type: 'CNC SETTINGS',
                user: currentUser.value ? currentUser.value.username : 'Unknown',
                title: 'CNC Port Changed',
                description: `CNC with uid ${uid} changed its port to ${value}.`
            });
        }

        function updateCNCType(uid, value) {
            store.dispatch("cnc/updateCNCType", {
                uid: uid,
                type: value
            });

            store.dispatch("log/addEvent", {
                type: 'CNC SETTINGS',
                user: currentUser.value ? currentUser.value.username : 'Unknown',
                title: 'CNC Type Changed',
                description: `CNC with uid ${uid} changed its type to ${value}.`
            });
        }

        function addRobot(name)
        {
            store.dispatch("robots/addRobot", {
                name: name,
                ip: '',
                type: ''
            });

            setNotification(
                3000,
                `Added new robot named ${name}. Do not forget to save in order for the changes to take place.`,
                'bi-exclamation-circle-fill'
            );

            store.dispatch("log/addEvent", {
                type: 'ROBOT SETTINGS',
                user: currentUser.value ? currentUser.value.username : 'Unknown',
                title: 'Robot Added',
                description: `Robot ${name} was added.`
            });
        }

        function removeRobot(uid)
        {
            store.dispatch("robots/removeRobot", {
                uid: uid
            });

            store.dispatch("log/addEvent", {
                type: 'ROBOT SETTINGS',
                user: currentUser.value ? currentUser.value.username : 'Unknown',
                title: 'Robot Removed',
                description: `Robot with uid ${uid} was removed.`
            });
        }

        function saveRobots() {
            const ips = robots.value.map(robot => robot.ip);
            const types = robots.value.map(robot => robot.type);

            let error = false;

            if(ips.includes(''))
            {
                setNotification(
                    3000,
                    `There are robots with no IP chosen. Cannot save the changes.`,
                    'bi-exclamation-circle-fill'
                );

                error = true;
            }

            if(types.includes(''))
            {
                setNotification(
                    3000,
                    `There are robots with no type chosen. Cannot save the changes.`,
                    'bi-exclamation-circle-fill'
                );

                error = true;
            }

            if(!error)
            {
                store.dispatch("robots/saveRobots");

                store.dispatch("log/addEvent", {
                    type: 'ROBOT SETTINGS',
                    user: currentUser.value ? currentUser.value.username : 'Unknown',
                    title: 'Robots Saved',
                    description: `Robots configuration was saved.`
                });
            }
        }

        function updateRobotIP(uid, value) {
            store.dispatch("robots/updateRobotConnectionID", {
                uid: uid,
                id: value
            });

            store.dispatch("log/addEvent", {
                type: 'ROBOT SETTINGS',
                user: currentUser.value ? currentUser.value.username : 'Unknown',
                title: 'Robot IP Changed',
                description: `Robot with uid ${uid} changed its IP to ${value}.`
            });
        }

        function updateRobotType(uid, value) {
            store.dispatch("robots/updateRobotType", {
                uid: uid,
                type: value
            });

            store.dispatch("log/addEvent", {
                type: 'Robot SETTINGS',
                user: currentUser.value ? currentUser.value.username : 'Unknown',
                title: 'Robot Type Changed',
                description: `Robot with uid ${uid} changed its type to ${value}.`
            });
        }

        function addProfilometer(name)
        {
            store.dispatch("profilometers/addProfilometer", {
                name: name,
                id: '',
                path: '',
                type: ''
            });

            setNotification(
                3000,
                `Added new profilometer named ${name}. Do not forget to save in order for the changes to take place.`,
                'bi-exclamation-circle-fill'
            );

            store.dispatch("log/addEvent", {
                type: 'PROFILOMETER SETTINGS',
                user: currentUser.value ? currentUser.value.username : 'Unknown',
                title: 'Profilometer Added',
                description: `Profilometer ${name} was added.`
            });
        }

        function removeProfilometer(uid)
        {
            store.dispatch("profilometers/removeProfilometer", {
                uid: uid
            });

            store.dispatch("log/addEvent", {
                type: 'PROFILOMETER SETTINGS',
                user: currentUser.value ? currentUser.value.username : 'Unknown',
                title: 'Profilometer Removed',
                description: `Profilometer with uid ${uid} was removed.`
            });
        }

        function saveProfilometers() {
            const ids = profilometers.value.map(prof => prof.ip);
            const paths = profilometers.value.map(prof => prof.ip);
            const types = profilometers.value.map(prof => prof.type);

            let error = false;

            if(ids.includes(''))
            {
                setNotification(
                    3000,
                    `There are profilometers with no ID chosen. Cannot save the changes.`,
                    'bi-exclamation-circle-fill'
                );

                error = true;
            }

            if(paths.includes(''))
            {
                setNotification(
                    3000,
                    `There are profilometers with no path chosen. Cannot save the changes.`,
                    'bi-exclamation-circle-fill'
                );

                error = true;
            }

            if(types.includes(''))
            {
                setNotification(
                    3000,
                    `There are profilometers with no type chosen. Cannot save the changes.`,
                    'bi-exclamation-circle-fill'
                );

                error = true;
            }

            if(!error)
            {
                store.dispatch("profilometers/saveProfilometers");

                store.dispatch("log/addEvent", {
                    type: 'PROFILOMETER SETTINGS',
                    user: currentUser.value ? currentUser.value.username : 'Unknown',
                    title: 'Profilometers Saved',
                    description: `Profilometers configuration was saved.`
                });
            }
        }

        function updateProfID(uid, value) {
            store.dispatch("profilometers/updateProfilometerID", {
                uid: uid,
                id: value
            });

            store.dispatch("log/addEvent", {
                type: 'PROFILOMETER SETTINGS',
                user: currentUser.value ? currentUser.value.username : 'Unknown',
                title: 'Profilometer ID Changed',
                description: `Profilometer with uid ${uid} changed its ID to ${value}.`
            });
        }

        function updateProfPath(uid, value) {
            store.dispatch("profilometers/updateProfilometerServerPath", {
                uid: uid,
                path: value
            });

            store.dispatch("log/addEvent", {
                type: 'PROFILOMETER SETTINGS',
                user: currentUser.value ? currentUser.value.username : 'Unknown',
                title: 'Profilometer Path Changed',
                description: `Profilometer with uid ${uid} changed its path to ${value}.`
            });
        }

        function updateProfType(uid, value) {
            store.dispatch("profilometers/updateProfilometerType", {
                uid: uid,
                type: value
            });

            store.dispatch("log/addEvent", {
                type: 'PROFILOMETER SETTINGS',
                user: currentUser.value ? currentUser.value.username : 'Unknown',
                title: 'Profilometer Type Changed',
                description: `Profilometerr with uid ${uid} changed its type to ${value}.`
            });
        }

        function hasDuplicates(array) {
            return (new Set(array)).size !== array.length;
        }

        onMounted(() => {
            if(currentConfiguration.value)
            {
                store.dispatch("cnc/loadCNCs");
                store.dispatch("cnc/loadCNCTypes");
                store.dispatch("cnc/loadPorts");

                store.dispatch("robots/loadRobots");
                store.dispatch("robots/loadRobotTypes");
                store.dispatch("robots/loadUltraArmPorts");

                store.dispatch("profilometers/loadProfilometers");
                store.dispatch("profilometers/loadProfilometerTypes");
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
