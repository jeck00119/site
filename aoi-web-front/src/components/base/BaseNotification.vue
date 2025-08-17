<template>
    <teleport to="body">
      <transition name="notification">
        <div class="notification-wrapper" v-if="showNotification" :style="{height: height, backgroundColor: color, top: top, left: left}">
            <div class="flex-column-center">
                <div class="text-wrapper">
                    {{ message }}
                </div>
                <div class="flex-center">
                    <font-awesome-icon 
                        :icon="icon" 
                        :spin="notificationType === 'loading'" 
                        :class="{ 'success-icon': notificationType === 'success' }"
                        :style="{ color: notificationType === 'success' ? '#059669' : 'white' }"
                        size="2x"
                    />
                </div>
            </div>
        </div>
      </transition>
    </teleport>
  </template>
  
<script>
import { ref, watch, toRef } from 'vue';

export default {
props: ['show', 'timeout', 'color', 'height', 'top', 'left', 'message', 'icon', 'notificationType'],

emits: ['close'],

setup(props, context) {
    const show = toRef(props, 'show');
    const timeout = toRef(props, 'timeout');
    const showNotification = ref(props.show);
    let timeoutId = null;

    const clearExistingTimeout = () => {
        if (timeoutId) {
            clearTimeout(timeoutId);
            timeoutId = null;
        }
    };

    const setNotificationTimeout = () => {
        clearExistingTimeout();
        if (props.timeout && showNotification.value) {
            timeoutId = setTimeout(() => {
                showNotification.value = false;
                context.emit('close');
                timeoutId = null;
            }, props.timeout);
        }
    };

    watch(show, (newValue) => {
        showNotification.value = newValue;
        if (newValue) {
            setNotificationTimeout();
        } else {
            clearExistingTimeout();
        }
    });

    watch(timeout, () => {
        if (showNotification.value) {
            setNotificationTimeout();
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
        top: 42%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 300px;
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
        transform: translate(-50%, -50%) scale(0.8);
    }

    .notification-enter-to,
    .notification-leave-from {
        opacity: 1;
        transform: translate(-50%, -50%) scale(1);
    }

    .notification-enter-active {
        transition: all 0.3s ease-out;
    }

    .notification-leave-active {
        transition: all 0.3s ease-in;
    }

    .flex-column-center {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 10px;
    }

    .flex-center {
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .text-wrapper {
        text-align: center;
        font-weight: 500;
    }

    .success-icon {
        text-shadow: 0 0 3px white, 0 0 6px white;
        filter: drop-shadow(0 0 2px white);
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