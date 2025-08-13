import { ref, type Ref } from 'vue';

interface NotificationHookReturn {
    showNotification: Ref<boolean>;
    notificationMessage: Ref<string>;
    notificationIcon: Ref<string>;
    notificationTimeout: Ref<number | null>;
    setNotification: (timeout: number, message: string, icon: string) => void;
    clearNotification: () => void;
}

/**
 * Notification Hook for managing user notifications
 * 
 * @returns Hook with notification state and management functions
 */
export default function useNotification(): NotificationHookReturn {
    const showNotification: Ref<boolean> = ref(false);
    const notificationMessage: Ref<string> = ref('');
    const notificationIcon: Ref<string> = ref('');
    const notificationTimeout: Ref<number | null> = ref(null);

    /**
     * Set a notification to be displayed
     * @param timeout - Duration in milliseconds before auto-hide
     * @param message - Notification message text
     * @param icon - Icon name to display
     */
    function setNotification(timeout: number, message: string, icon: string): void {
        notificationTimeout.value = timeout;
        notificationMessage.value = message;
        notificationIcon.value = icon;
        showNotification.value = true;
    }

    /**
     * Clear/hide the current notification
     */
    function clearNotification(): void {
        showNotification.value = false;
        // Reset other values after a short delay to allow animations
        setTimeout(() => {
            notificationMessage.value = '';
            notificationIcon.value = '';
            notificationTimeout.value = null;
        }, 300);
    }

    return {
        showNotification,
        notificationMessage,
        notificationIcon,
        notificationTimeout,
        setNotification,
        clearNotification
    };
}