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
    </div>
</template>

<script>
import { computed , onMounted } from 'vue';
import { useStore } from 'vuex';

export default{
    setup() {
        const store = useStore();

        const users = computed(function() {
            return store.getters["auth/getUsers"];
        });

        const availableRoles = computed(function() {
            return store.getters["auth/getAvailableRoles"].concat([""]);
        });

        function updateRole(uid, role) {
            store.dispatch("auth/updateUsersRole", {
                uid: uid,
                role: role
            });
        }

        onMounted(() => {
            store.dispatch("auth/loadUsers");
            store.dispatch("auth/loadAvailableRoles");
        });

        return {
            users,
            availableRoles,
            updateRole
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
    height: 100%;
    overflow-y: auto;
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