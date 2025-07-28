<template>
    <div class="footer-container">
        <div class="config-control">
            <h3>{{ currentConfiguration ? currentConfiguration.name : '-' }}</h3>
        </div>
        <div class="right-side-container">
            <div class="user-card" v-if="currentUser">
                <div class="user-info">
                    Hello, {{ currentUser.username }}
                </div>
                <div class="user-action">
                    <base-button-rectangle @state-changed="logout()" :style="{backgroundColor: 'black', border: 'none'}">
                        <div class="btn-container">
                            Logout
                        </div>
                    </base-button-rectangle>
                </div>
            </div>
            <div class="nvidia-logo-container">
                <img class="nvidia-logo" src="../../assets/icons/nvidia.png" alt="Nvidia Logo">
            </div>
            <div class="tct-logo-container">
                <img class="tct-logo" src="../../assets/icons/hro-tct-cropped.png" alt="TCT Logo">
            </div>
            <div class="error-list-control">
                <the-error-list-button></the-error-list-button>
            </div>
        </div>
    </div>
</template>

<script>
import { computed } from 'vue';
import { useStore } from 'vuex';
import TheErrorListButton from './TheErrorListButton.vue';
import { useRoute, useRouter } from 'vue-router';

export default {
    components:{
        TheErrorListButton
    },

    setup() {
        const store = useStore();
        const router = useRouter();
        const route = useRoute();

        const currentConfiguration = computed(function() {
            return store.getters["configurations/getCurrentConfiguration"];
        });

        const currentUser = computed(function() {
            return store.getters["auth/getCurrentUser"];
        });

        function logout() {
            store.dispatch("auth/logout");

            if(route.meta && route.meta.requiresAuth)
            {
                router.push('/');
            }
        }

        return {
            currentConfiguration,
            currentUser,
            logout
        }
    }
}
</script>

<style scoped>
.footer-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 100%;
}

.config-control {
    margin-left: 1%;
    align-self: center;
    height: 100%;
    width: 39%;
    display: flex;
    justify-content: flex-start;
    align-items: center;
}

.tct-logo-container {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 10%;
    height: 100%;
    margin-right: 2%;
    margin-left: 2%;
}

.tct-logo {
    max-width: 100%;
    height: auto;
    object-fit: cover;
}

.nvidia-logo-container {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 10%;
    height: 100%;
    margin-left: 2%;
}

.nvidia-logo {
    max-width: 50%;
    height: auto;
    object-fit: cover;
}

.error-list-control {
    align-self: center;
    margin-right: 1%;
    width: 10%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
}

.right-side-container {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    width: 60%;
    height: 100%;
}

.user-card {
    height: 100%;
    display: flex;
    justify-content: flex-end;
    align-items: center;
    margin-right: 1%;
    width: 80%;
}

.user-info {
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 1vw;
    margin-right: 0.5%;
}

.btn-container {
    padding: 0.5vh 0.5vw;
    color: white;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 1vw;
}
</style>