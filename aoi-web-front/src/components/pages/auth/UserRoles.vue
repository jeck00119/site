<template>
    <div class="flex-container">
        <div class="title">
            <h1>User List</h1>
        </div>
        <div class="list-container">
            <div class="user-card" v-for="user in users">
                <div class="username">
                    {{ user.username }}
                </div>
                <div class="role-control">
                    <base-dropdown
                        width="100%"
                        :current="user.level"
                        :values="availableRoles"
                        name=""
                        @update-value="(_, value) => updateRole(user.uid, value)"
                    ></base-dropdown>
                </div>
            </div>
        </div>
        <base-notification
            :show="showNotification"
            :timeout="notificationTimeout"
            :message="notificationMessage"
            :icon="notificationIcon"
            :notificationType="notificationType"
            height="15vh"
            color="#CCA152"
            @close="clearNotification"
        />
    </div>
</template>

<script>
import { computed , onMounted, ref } from 'vue';
import { useAuthStore } from '@/composables/useStore';
import { validateRequired } from '../../../utils/validation.js';
import useNotification, { NotificationType } from '../../../hooks/notifications.js';
import { AuthMessages, ValidationMessages } from '@/constants/notifications';

export default{
    setup() {
        const authStore = useAuthStore();
        const { showNotification, notificationMessage, notificationIcon, notificationTimeout, notificationType, setTypedNotification, clearNotification } = useNotification();

        // These are already computed refs from the composables
        const users = authStore.users;

        const availableRoles = computed(() => {
            const roles = authStore.availableRoles.value || [];
            // Ensure roles is an array before using concat
            if (Array.isArray(roles)) {
                return roles.concat([""]);
            }
            return [""];
        });

        function updateRole(uid, role) {
            // Validate that a role is selected
            const requiredValidation = validateRequired(role, 'Role');
            
            if (!requiredValidation.isValid) {
                setTypedNotification(
                    'Please select a role for the user.',
                    NotificationType.ERROR,
                    3000
                );
                return;
            }
            
            try {
                authStore.updateUsersRole({
                    uid: uid,
                    role: role
                });
                
                setTypedNotification(
                    'User role updated successfully.',
                    NotificationType.SUCCESS,
                    2000
                );
            } catch (error) {
                setTypedNotification(
                    'Failed to update user role. Please try again.',
                    NotificationType.ERROR,
                    3000
                );
            }
        }

        onMounted(() => {
            authStore.loadUsers();
            authStore.loadAvailableRoles();
        });

        return {
            users,
            availableRoles,
            updateRole,
            showNotification,
            notificationMessage,
            notificationIcon,
            notificationTimeout,
            notificationType,
            clearNotification
        }
    }
}
</script>

<style scoped>
.flex-container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 90vh;
    color: white;
}

.list-container {
    display: flex;
    flex-direction: column;
    width: 100%;
    min-height: 100%;
    /* overflow-y: auto; - moved scrolling to body level */
    justify-content: flex-start;
    align-items: center;
}

.user-card {
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.26);
    display: flex;
    width: 95%;
    height: 20%;
    margin-bottom: 2%;
    /* background-color: blue; */
}

.username {
    width: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
}

.role-control {
    width: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
}

</style>