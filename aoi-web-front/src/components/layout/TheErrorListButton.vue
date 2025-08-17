<template>
    <button class="error-button" @click="showErrorList">
        <v-icon name="fa-exclamation-triangle"/>
        <div v-show="hasErrors" class="red-circle">{{ numberOfErrors }}</div>
    </button>
    
    <the-error-list :show="listVisible" title="Errors" @close="hideErrorList"></the-error-list>
</template>

<script>
import { ref, computed } from 'vue';
import { useErrorsStore } from '@/composables/useStore';
import { logger } from '@/utils/logger';

import TheErrorList from './TheErrorList.vue';

export default {
    components: {
        TheErrorList
    },

    setup() {
        
        // Use centralized errors store composable
        const { errors, hasErrors } = useErrorsStore();
        const numberOfErrors = computed(() => errors.value.length);
        
        const listVisible = ref(false);

        function showErrorList() {
            logger.debug('Showing error list');
            listVisible.value = true;
        }

        function hideErrorList() {
            logger.debug('Hiding error list');
            listVisible.value = false;
        }
        
        // Component mounted - debug removed to reduce log spam

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
    border: var(--border-width-0);
    border-radius: var(--border-radius-full);
    padding: var(--space-2);
    color: var(--color-text-inverse);
    background-color: var(--color-primary);
    box-shadow: var(--shadow-button);
    transition: var(--transition-button);
}

button:hover {
    box-shadow: var(--shadow-button-hover);
}

.error-button {
    position: relative;
    font-size: var(--font-size-sm);
    display: flex;
    justify-content: center;
    align-items: center;
    margin: var(--space-0);
    height: auto;
}

.red-circle {
    position: absolute;
    top: -15%;
    right: -10%;
    background-color: var(--color-error);
    border-radius: var(--border-radius-full);
    width: 50%;
    height: 50%;
    color: var(--color-text-secondary);
    display: flex;
    justify-content: center;
    align-items: center;
    padding: var(--space-1);
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-bold);
}
</style>