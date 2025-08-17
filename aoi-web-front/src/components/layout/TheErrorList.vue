<template>
    <teleport to="body">
      <div v-if="show" @click="tryClose" class="backdrop"></div>
      <transition name="dialog">
        <dialog open v-if="show">
          <header>
            <slot name="header">
              <h2>{{ title }}</h2>
            </slot>
          </header>
          <section>
            <div v-if="hasValues">
                <div class="error-wrapper" v-for="error in errors" :key="error.id">
                    <div class="title-wrapper">
                        <h2>{{ error.title }}</h2>
                        <base-action-button @click="removeError(error.id)">Remove</base-action-button>
                    </div>
                    <p>{{ error.description }}</p>
                </div>
            </div>
            <div v-else>
                <p class="no-errors">There are no errors.</p>
            </div>
          </section>
          <menu v-if="!fixed">
          </menu>
      </dialog>
      </transition>
    </teleport>
  </template>
  
<script>
import { ref, computed } from 'vue';
import { useErrorsStore } from '@/composables/useStore';
import { logger } from '@/utils/logger';

export default {
props: {
    show: {
        type: Boolean,
        required: true,
    },
        title: {
        type: String,
        required: false,
    },
    fixed: {
        type: Boolean,
        required: false,
        default: false,
    },
},

emits: ['close'],

setup(props, context) {
    
    // Use centralized errors store composable
    const { errors, hasErrors, removeError: removeErrorFromStore } = useErrorsStore();
    
    function removeError(id) {
        logger.debug('Removing error', { errorId: id });
        removeErrorFromStore(id);
    }

    function tryClose() {
        if(props.fixed){
            return;
        }
        logger.debug('Closing error list');
        context.emit('close');
    }

    const hasValues = computed(() => hasErrors.value);
    
    // Component mounted - debug removed to reduce log spam

    return {
        errors,
        hasValues,
        tryClose,
        removeError,
    };
}
};
</script>
  
<style scoped>
    .backdrop {
        position: fixed;
        top: 0;
        left: 0;
        height: 100vh;
        width: 100%;
        background-color: var(--color-bg-overlay);
        z-index: var(--z-index-modal-backdrop);
    }

    .error-wrapper {
        color: var(--color-text-secondary);
        margin: var(--space-2);
        padding: var(--space-3);
        border-radius: var(--border-radius-base);
        background-color: var(--color-bg-secondary);
    }

    .title-wrapper {
        display: flex;
        justify-content: space-between;
        align-items: center;
        min-height: var(--button-height-lg);
        padding: var(--space-3) var(--space-0);
        margin-bottom: var(--space-2);
    }

    .no-errors {
        color: var(--color-text-secondary);
        text-align: center;
        padding: var(--space-8);
        font-style: italic;
    }

    dialog {
        position: fixed;
        top: 20vh;
        left: 10%;
        width: 80%;
        height: 60%;
        z-index: var(--z-index-modal);
        border-radius: var(--border-radius-modal);
        border: var(--border-width-0);
        box-shadow: var(--shadow-modal);
        padding: var(--space-0);
        margin: var(--space-0);
        overflow-y: auto;
        background-color: var(--color-bg-primary);
    }

    header {
        background-color: var(--color-primary);
        color: var(--color-text-inverse);
        width: 100%;
        padding: var(--space-4);
    }

    header h2 {
        margin: var(--space-0);
        font-size: var(--font-size-xl);
        font-weight: var(--font-weight-semibold);
    }

    section {
        padding: var(--space-4);
    }

    menu {
        padding: var(--space-4);
        display: flex;
        justify-content: flex-end;
        margin: var(--space-0);
    }

    .dialog-enter-from,
    .dialog-leave-to {
        opacity: 0;
        transform: scale(0.8);
    }

    .dialog-enter-to,
    .dialog-leave-from {
        opacity: 1;
        transform: scale(1);
    }

    .dialog-enter-active {
        transition: all var(--duration-slow) var(--ease-out);
    }

    .dialog-leave-active {
        transition: all var(--duration-slow) var(--ease-in);
    }

    ::-webkit-scrollbar {
        width: var(--space-3);
    }

    ::-webkit-scrollbar-track {
        background: var(--color-border-secondary); 
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--color-bg-tertiary); 
        border-radius: var(--border-radius-base);
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--color-primary); 
    }
  
    @media (min-width: 768px) {
        dialog {
            left: calc(50% - 20rem);
            width: 40rem;
        }
    }
</style>