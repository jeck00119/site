<template>
    <button class="error-button" @click="showErrorList">
        <v-icon name="fa-exclamation-triangle"/>
        <div v-show="hasErrors" class="red-circle">{{ numberOfErrors }}</div>
    </button>
    
    <the-error-list :show="listVisible" title="Errors" @close="hideErrorList"></the-error-list>
</template>

<script>
import { ref, computed } from 'vue';
import { useStore } from 'vuex';

import TheErrorList from './TheErrorList.vue';

export default {
    components: {
        TheErrorList
    },

    setup() {
        const store = useStore();

        const hasErrors = computed(function() {
            return !store.getters['errors/isEmpty'];
        });

        const numberOfErrors = computed(function() {
            return store.getters['errors/numberOfErrors'];
        });

        const listVisible = ref(false);

        function showErrorList() {
            listVisible.value = true;
        };

        function hideErrorList() {
            listVisible.value = false;
        };

        return {
            listVisible,
            hasErrors,
            numberOfErrors,
            showErrorList,
            hideErrorList
        };
    }
}
</script>

<style scoped>
button {
    border: none;
    border-radius: 50%;
    padding: 10%;
    color: black;
    background-color: rgb(204, 161, 82);
    box-shadow: 0 2px 4px black;
}

.error-button {
    position: relative;
    font-size: 1vw;
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 0;
    height: auto;
}

.red-circle {
    position: absolute;
    top: -15%;
    right: -10%;
    background-color: red;
    border-radius: 50%;
    width: 50%;
    height: 50%;
    color: white;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 3%;
    font-size: 0.8vw;
}
</style>