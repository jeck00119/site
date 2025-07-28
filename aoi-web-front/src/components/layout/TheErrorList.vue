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
import { useStore } from 'vuex';

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
    const store = useStore();

    const errors = computed(function() {
        return store.getters['errors/getErrors'];
    });

    function removeError(id) {
        store.dispatch('errors/removeError', {errorId: id});
    }

    function tryClose() {
        if(props.fixed){
            return;
        }
        context.emit('close');
    };

    const hasValues = computed(function() {
        return !store.getters.isEmpty;
    });

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
        background-color: rgba(0, 0, 0, 0.75);
        z-index: 10;
    }

    .error-wrapper {
        color: white;
        margin: 5px;
    }

    .title-wrapper {
        display: flex;
        justify-content: space-between;
        height: 7vh;
        padding-bottom: 10px;
        padding-top: 10px;
    }

    .no-errors {
        color: white;
    }

    dialog {
        position: fixed;
        top: 20vh;
        left: 10%;
        width: 80%;
        height: 60%;
        z-index: 100;
        border-radius: 12px;
        border: none;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.26);
        padding: 0;
        margin: 0;
        overflow-y: auto;
        background-color: rgb(0, 0, 0);
    }

    header {
        background-color: rgb(204, 161, 82);
        color: rgb(0, 0, 0);
        width: 100%;
        padding: 1rem;
    }

    header h2 {
        margin: 0;
    }

    section {
        padding: 1rem;
    }

    menu {
        padding: 1rem;
        display: flex;
        justify-content: flex-end;
        margin: 0;
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
        transition: all 0.3s ease-out;
    }

    .dialog-leave-active {
        transition: all 0.3s ease-in;
    }

    ::-webkit-scrollbar {
            width: 10px;
    }

    ::-webkit-scrollbar-track {
        background: #888; 
    }
    
    ::-webkit-scrollbar-thumb {
        background: black; 
    }

    ::-webkit-scrollbar-thumb:hover {
        background: rgb(204, 161, 82); 
    }
  
    @media (min-width: 768px) {
        dialog {
            left: calc(50% - 20rem);
            width: 40rem;
        }
    }
</style>