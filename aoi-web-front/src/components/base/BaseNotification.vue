<template>
    <teleport to="body">
      <transition name="notification">
        <div class="notification-wrapper" v-if="showNotification" :style="{height: height, backgroundColor: color, top: top, left: left}">
            <slot></slot>
        </div>
      </transition>
    </teleport>
  </template>
  
<script>
import { ref, watch, toRef } from 'vue';

export default {
props: ['show', 'timeout', 'color', 'height', 'top', 'left'],

emits: ['close'],

setup(props, context) {
    const show = toRef(props, 'show');
    const timeout = toRef(props, 'timeout');
    const showNotification = ref(props.show);

    watch(show, (newValue) => {
        showNotification.value = newValue;
    });

    watch(showNotification, (newValue) => {
        if(newValue)
        {
            if(props.timeout)
            {
                setTimeout(() => {
                    showNotification.value = false;
                    context.emit('close');
                }, props.timeout);
            }
        }
    });

    watch(timeout, (newValue) => {
        if(newValue)
        {
            setTimeout(() => {
                showNotification.value = false;
                context.emit('close');
            }, props.timeout);
        }
    });

    return {
        showNotification
    };
}
};
</script>
  
<style scoped>
    .notification-wrapper {
        position: fixed;
        top: 1vh;
        left: 40%;
        width: 20%;
        /* height: 40%; */
        z-index: 50;
        border: 1px solid gray;
        border-radius: 8px;
        border: none;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.26);
        padding: 3px;
        margin: 0;
        overflow-y: auto;
        background-color: rgb(30, 28, 28);
        color: white;
        display: flex;
        justify-content: center;
    }

    .notification-enter-from,
    .notification-leave-to {
        opacity: 0;
        transform: scale(0.8);
    }

    .notification-enter-to,
    .notification-leave-from {
        opacity: 1;
        transform: scale(1);
    }

    .notification-enter-active {
        transition: all 0.3s ease-out;
    }

    .notification-leave-active {
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