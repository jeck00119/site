<template>
    <div class="flex-container">
        <div class="content-container">
            <div class="title">
                <p>Usage Manual</p>
            </div>
            <div class="close">
                <router-link :to="'/inspections-and-results'">&#10006;</router-link>
            </div>
            <div class="pdf-container">
                <vue-pdf-embed :source="helpDocument" class="vue-pdf-embed"></vue-pdf-embed>
            </div>
            <div class="video-container">
                <!-- <video height="500" controls>
                    <source src="../../../assets/videos/AOIWebApp.mp4" type="video/mp4">
                    Your browser does not support the video tag.
                </video> -->
            </div>
            <div>
                <router-link :to="'/inspections-and-results'">Back to main page</router-link>
            </div>
        </div>
        <!-- <div class="title">
            <p>Usage Manual</p>
        </div>
        <div class="close">
                <router-link :to="'/inspections-and-results'">&#10006;</router-link>
        </div>
        <div class="pdf-container">
            <vue-pdf-embed :source="helpDocument" class="vue-pdf-embed"></vue-pdf-embed>
        </div>
        <div class="video-container">
            <video controls>
                <source src="../../../assets/videos/AOIWebApp.mp4" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        </div>
        <div>
            <router-link :to="'/inspections-and-results'">Back to main page</router-link>
        </div> -->
    </div>
</template>

<script>
import { computed, onMounted, onUnmounted } from 'vue';
import { useStore } from 'vuex';

import VuePdfEmbed from 'vue-pdf-embed';

export default{
    components: {
        VuePdfEmbed
    },

    setup() {
        const store = useStore();

        const helpDocument = computed(function() {
            return 'data:appliation/pdf;base64,' + store.getters['help/getHelpDocument'];
        });

        onMounted(() => {
            store.dispatch('help/loadHelpDocument');
        });

        onUnmounted(() => {
            store.dispatch('help/setHelpDocument', '');
        });

        return {
            helpDocument
        }
    }
}
</script>

<style scoped>
.flex-container {
    display: flex;
    flex-direction: column;
    width: 100%;
    height: 90vh;
    color: white;
}

.content-container {
    overflow-y: auto;
    background-color: #333;
    color: white;
    padding: 1%;
}

.content-container::-webkit-scrollbar { 
    display: none;  /* Safari and Chrome */
}

.flex-container .close {
    position: absolute;
    top: 1%;
    right: 1%;
    font-size: 1.5vw;
}

.title {
    font-weight: bolder;
    font-size: xx-large;
}

.pdf-container {
    width: 100%;
    height: 90vh;
    overflow-y: auto;
}

.vue-pdf-embed > div {
    overflow-y: auto;
    height: 100%;
}

.video-container {
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 5vh;
}
</style>