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
            height="15vh"
            :timeout="notificationTimeout"
            @close="clearNotification"
        >
            <div class="message-wrapper">
                <div class="icon-wrapper">
                    <v-icon :name="notificationIcon" scale="2.5" animation="spin"/>
                </div>
                <div class="text-wrapper">
                    {{ notificationMessage }}
                </div>
            </div>
        </base-notification>
    </div>
</template>

<script>
import { computed , onMounted, ref } from 'vue';
import { useAuthStore } from '@/composables/useStore';
import { validateRequired } from '../../../utils/validation.js';
import useNotification from '../../../hooks/notifications.js';

export default{
    setup() {
        const authStore = useAuthStore();
        const { showNotification, notificationMessage, notificationIcon, notificationTimeout, setNotification, clearNotification } = useNotification();

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
                setNotification(3000, 'Please select a role for the user.', 'bi-exclamation-circle-fill');
                return;
            }
            
            try {
                authStore.updateUsersRole({
                    uid: uid,
                    role: role
                });
                
                setNotification(2000, 'User role updated successfully.', 'bi-check-circle-fill');
            } catch (error) {
                setNotification(3000, 'Failed to update user role. Please try again.', 'bi-exclamation-circle-fill');
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

.message-wrapper {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.icon-wrapper {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 3%;
}

.text-wrapper {
    font-size: 100%;
    width: 95%;
    text-align: center;
}
</style>