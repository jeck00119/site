<template>
    <div class="nav-container">
        <transition name="slide-fade" mode="out-in">
            <div class="brg-container" v-if="!navBarVisibility" @click="showNavBar" height="10vh">
                <svg viewBox="0 0 100 80" width="40" height="40" fill="background-color: rgb(204, 161, 82)">
                    <rect width="100" height="20" rx="10"></rect>
                    <rect y="25" width="100" height="20" rx="10"></rect>
                    <rect y="50" width="100" height="20" rx="10"></rect>
                </svg>
            </div>
            <div class="nav-menu" v-else>
                <div class="header">
                    <div class="header-item-logo">
                        <img class="aoi-logo" src="../../assets/icons/aoi-logo.png" alt="AOI Logo">
                    </div>
                </div>
                <div class="header-item-hide">
                    <img src="../../assets/icons/back.png" alt="Hide navigation bar" @click="hideNavBar">
                </div>
                <div class="primary-buttons-container">
                    <div v-for="button in buttons">
                        <nav-primary-button :id="button.id" :name="button.name" :subpages="button.subpages" :iconName="button.icon" :showSubPages="button.showSubPages" @route-changed="hideNavBar" @collapse="collapseSubPages">
                        </nav-primary-button>
                    </div>
                </div>
            </div>
        </transition>
    </div>
</template>

<script>
import NavPrimaryButton from './NavPrimaryButton.vue';
import {ref, watch} from 'vue';

export default {
    components: {
        NavPrimaryButton
    },

    emits: ['visibility-changed'],

    setup(_, context) {
        const buttons = ref([
            {
                id: 1,
                name: "HOME",
                icon: 'house',
                subpages: ["AOI", "Inspections and Results"],
                showSubPages: false
            },
            {
                id: 2,
                name: "INSPECTIONS",
                icon: 'magnifying-glass-chart',
                subpages: ["Components", "Identification", "References", "Custom Components", "Inspection List"],
                showSubPages: false
            },
            {
                id: 3,
                name: "TOOLS",
                icon: 'screwdriver-wrench',
                subpages: ["CNC Machine", "Robot Control", "Camera Calibration", "Stereo Calibration", "Algorithm Debug", "Log", "Media"],
                showSubPages: false
            },
            {
                id: 4,
                name: "SETTINGS",
                icon: 'gear',
                subpages: ["Itac Settings", "System Settings", "Image Sources"],
                showSubPages: false
            },
            {
                id: 5,
                name: "AUTHENTICATION",
                icon: 'user',
                subpages: ["Signup", "Login", "Roles"],
                showSubPages: false
            },
            {
                id: 6,
                name: "ABOUT",
                icon: 'circle-info',
                subpages: ["Help"],
                showSubPages: false
            },
            {
                id: 7,
                name: "CONFIGURATIONS",
                icon: 'clipboard-check',
                subpages: ["Configurations"],
                showSubPages: false
            }
        ]);

        const navBarVisibility = ref(false);

        function hideNavBar(){
            navBarVisibility.value = false;
        }

        function showNavBar() {
            navBarVisibility.value = true;
        }

        function collapseSubPages(id) {
            buttons.value.forEach(button => {
                if (button.id !== id) {
                    button.showSubPages = false;
                }
                else
                {
                    button.showSubPages = !button.showSubPages;
                }
            });
        }

        watch(navBarVisibility, (newVal) => {
            context.emit("visibility-changed", newVal);
        });

        return {
            buttons,
            navBarVisibility,
            hideNavBar,
            showNavBar,
            collapseSubPages
        };
    }
};
</script>

<style scoped>
    .nav-container {
        display: flex;
        position: fixed;
        z-index: 100;
    }

    .header {
        display: flex;
        background-color: rgb(0, 0, 0);
        margin: 0px;
        padding: 0px;
        justify-content: center;
        border: none;
        height: 20%;
    }
    .nav-menu {
        /* position: fixed; */
        /* z-index: 100; */
        background-color: rgb(0, 0, 0);
        width: 20vw;
        overflow-y: auto;
        margin: 0px;
        height: 100vh;
    }

    .nav-menu::-webkit-scrollbar { 
        display: none;  /* Safari and Chrome */
    }

    h1 {
        color: rgb(204, 161, 82);
        font-weight: 900;
    }

    .primary-buttons-container {
        margin-top: 1vh;
        padding: 0px;
    }

    .header-item-logo {
        align-self: center;
        margin-left: auto;
        margin-right: auto;
        height: 100%;
        width: 100%;
    }

    .aoi-logo {
        max-width: 100%;
        height: auto;
        object-fit: cover;
    }

    img {
        max-width: 100%;
        max-height: 100%;
    }

    .header-item-hide {
        align-self: flex-start;
        position: absolute;
        top: 1%;
        right: 1%;
    }

    .header-item-hide:hover {
        cursor: pointer;
        background-color: rgb(25, 25, 25);
    }

    .brg-container {
        margin-left: 0.5vw;
        margin-top: 0.4vh;
    }

    .brg-container:hover {
        cursor: pointer;
    }

    .slide-fade-enter-active {
        transition: all .3s ease-in;
    }
    .slide-fade-leave-active {
        /* transition: all .8s cubic-bezier(1.0, 0.5, 0.8, 1.0); */
        transition: all .3s ease-out;
    }

    .slide-fade-enter-from,
    .slide-fade-leave-to {
        transform: translateX(-20vw);
    }

    .slide-fade-enter-to,
    .slide-fade-leave-from {
        transform: translateX(0);
    }

    .slide-fade-leave-from {
        transform: translateX(0);
    }

    ::-webkit-scrollbar {
        width: 10px;
    }

    ::-webkit-scrollbar-track {
        background: black; 
    }
 
    ::-webkit-scrollbar-thumb {
        background: #888; 
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #555; 
    }
</style>