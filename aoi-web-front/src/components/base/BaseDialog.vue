<template>
    <teleport to="body">
      <div v-if="show" @click="tryClose" class="backdrop"></div>
      <transition name="dialog">
        <dialog open v-if="show">
            <div class="dialog-control">
                <header>
                    <slot name="header">
                        <div class="title-container">
                            <h4>{{ title }}</h4>
                        </div>
                    </slot>
                </header>
                <div class="content-wrapper" :style="{height: height}">
                    <section>
                        <slot></slot>
                    </section>
                    <menu>
                        <slot name="actions"></slot>
                    </menu>
                </div>
            </div>
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
    height: {
        type: String,
        required: false
    }
},

emits: ['close'],

setup(_, context) {
    function tryClose() {
        context.emit('close');
    };

    return {
        tryClose
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

    .content-wrapper {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 80%;
    }

    .dialog-control {
        height: 100%;
    }

    dialog {
        position: fixed;
        top: 20vh;
        left: 10%;
        width: 80%;
        /* height: 40%; */
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
        height: 5vh;
        display: flex;
    }

    header h4 {
        margin: 0;
    }

    .title-container {
        display: flex;
        align-items: center;
        margin-left: 0.5vw;
    }

    section {
        padding: 1vh 1vw;
        margin: 0;
    }

    menu {
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