import { ref } from 'vue';

export default function useNotification() {
    const showNotification = ref(false);
    const notificationMessage = ref('');
    const notificationIcon = ref('');
    const notificationTimeout = ref(null);

    function setNotification(timeout, message, icon) {
        notificationTimeout.value = timeout;
        showNotification.value = true;
        notificationMessage.value = message;
        notificationIcon.value = icon;
    }

    function clearNotification() {
        showNotification.value = false;
    }

    return {
        showNotification,
        notificationMessage,
        notificationIcon,
        notificationTimeout,
        setNotification,
        clearNotification
    }
}