import { ref, type Ref } from 'vue';
import { 
    NotificationType, 
    NotificationOptions,
    getNotificationConfig,
    createNotification 
} from '@/constants/notifications';

interface NotificationHookReturn {
    showNotification: Ref<boolean>;
    notificationMessage: Ref<string>;
    notificationIcon: Ref<string>;
    notificationTimeout: Ref<number | null>;
    notificationColor: Ref<string>;
    notificationType: Ref<NotificationType | null>;
    setNotification: (timeout: number, message: string, icon: string) => void;
    setTypedNotification: (message: string, type?: NotificationType, customTimeout?: number) => void;
    setNotificationFromOptions: (options: NotificationOptions) => void;
    clearNotification: () => void;
}

/**
 * Enhanced Notification Hook for managing user notifications
 * Now supports centralized message types and configurations
 * 
 * @returns Hook with notification state and management functions
 */
export default function useNotification(): NotificationHookReturn {
    const showNotification: Ref<boolean> = ref(false);
    const notificationMessage: Ref<string> = ref('');
    const notificationIcon: Ref<string> = ref('');
    const notificationTimeout: Ref<number | null> = ref(null);
    const notificationColor: Ref<string> = ref('blue');
    const notificationType: Ref<NotificationType | null> = ref(null);

    /**
     * Set a notification to be displayed (legacy method for backward compatibility)
     * @param timeout - Duration in milliseconds before auto-hide
     * @param message - Notification message text
     * @param icon - Icon name to display
     */
    function setNotification(timeout: number, message: string, icon: string): void {
        notificationTimeout.value = timeout;
        notificationMessage.value = message;
        notificationIcon.value = icon;
        notificationColor.value = 'blue'; // Default color for legacy calls
        notificationType.value = null;
        showNotification.value = true;
    }

    /**
     * Set a typed notification using the centralized notification system
     * @param message - Notification message text
     * @param type - Notification type (success, error, warning, info, loading)
     * @param customTimeout - Optional custom timeout (overrides default)
     */
    function setTypedNotification(
        message: string, 
        type: NotificationType = NotificationType.INFO,
        customTimeout?: number
    ): void {
        const config = getNotificationConfig(type);
        
        notificationMessage.value = message;
        notificationType.value = type;
        notificationIcon.value = config.icon;
        notificationColor.value = config.color;
        notificationTimeout.value = customTimeout ?? config.timeout;
        showNotification.value = true;
    }

    /**
     * Set a notification from a NotificationOptions object
     * @param options - Notification options object
     */
    function setNotificationFromOptions(options: NotificationOptions): void {
        const type = options.type || NotificationType.INFO;
        const config = getNotificationConfig(type);
        
        notificationMessage.value = options.message;
        notificationType.value = type;
        notificationIcon.value = options.icon || config.icon;
        notificationColor.value = options.color || config.color;
        notificationTimeout.value = options.timeout ?? config.timeout;
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
            notificationColor.value = 'blue';
            notificationType.value = null;
        }, 300);
    }

    return {
        showNotification,
        notificationMessage,
        notificationIcon,
        notificationTimeout,
        notificationColor,
        notificationType,
        setNotification, // Keep for backward compatibility
        setTypedNotification, // New typed method
        setNotificationFromOptions, // New options-based method
        clearNotification
    };
}

// Export notification types for convenience
export { NotificationType } from '@/constants/notifications';