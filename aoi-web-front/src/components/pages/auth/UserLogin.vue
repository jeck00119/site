<template>
    <div class="flex-container">
        <div class="slime-left"></div>
        <div class="slime-right"></div>
        <div class="title">
            <h1>Login</h1>
        </div>
        <div class="parent-container">
            <div class="card-container">
                <div class="icons-container">
                    <v-icon name="fc-camera-addon" scale="2.5"/>
                    <v-icon name="fc-command-line" scale="2.5"/>
                    <v-icon name="fc-support" scale="2.5"/>
                </div>
                <div class="text-container">
                    <h3>Login in order to make use of AOI web app full experience!</h3>
                </div>
            </div>
            <div class="form-container">
                <form @submit.prevent="login">
                    <div class="fields-container">
                        <div class="form-control">
                            <label for="email">Email:</label>
                            <input type="text" id="email" v-model.trim="email"/>
                        </div>
                        <div class="form-control">
                            <label for="password">Password:</label>
                            <input type="password" id="password" v-model.trim="password"/>
                        </div>
                    </div>
                    <div class="button-container">
                        <button class="submit-button">Login</button>
                    </div>
                    <div>
                        <hr>
                        <router-link :to="'/signup'">Do not have an account?</router-link>
                    </div>
                </form>
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
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';

import useNotification from '../../../hooks/notifications.js';

export default{
    setup() {
        const email = ref('');
        const password = ref('');

        const {showNotification, notificationMessage, notificationIcon, notificationTimeout, 
            setNotification, clearNotification} = useNotification();

        const store = useStore();
        const router = useRouter();

        async function login() {
            let error = false;

            if(email.value === '')
            {
                setNotification(3000, `Please enter your email.`, 'bi-exclamation-circle-fill');
                error = true;
            }

            if(password.value === '')
            {
                setNotification(3000, `Please enter your password.`, 'bi-exclamation-circle-fill');
                error = true;
            }

            if(!error)
            {
                const user = new FormData();

                user.append('username', email.value);
                user.append('password', password.value);
                
                try {
                    await store.dispatch("auth/login", user);

                    router.replace('/');
                }catch(e) {
                    setNotification(3000, `Something went wrong. Please try again.`, 'bi-exclamation-circle-fill');
                }
            }
        }

        onMounted(() => {
            store.dispatch("auth/loadUsers");
        });

        return {
            email,
            password,
            showNotification,
            notificationMessage,
            notificationIcon,
            notificationTimeout,
            login,
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

.slime-left {
    position: absolute;
    top: 0%;
    left: -5%;
    z-index:0;
    width: 30%;
    height: 80%;
    background-color: rgb(204, 161, 82);
    animation-name: slime-left;
    animation-duration: 5s;
    animation-timing-function: linear;
    animation-iteration-count: infinite;
}

.slime-right {
    position: absolute;
    top: 50%;
    left: 65%;
    z-index:0;
    width: 30%;
    height: 40%;
    background-color: rgb(204, 161, 82);
    animation-name: slime-right;
    animation-duration: 4s;
    animation-timing-function: linear;
    animation-iteration-count: infinite;
}

.parent-container {
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.26);
    display: flex;
    z-index: 1;
}

.card-container {
    display: flex;
    flex-direction: column;
    background-color: black;
    height: 40vh;
    width: 25vw;
    justify-content: center;
    align-items: center;
}

.icons-container {
    margin-bottom: 2vh;
    display: flex;
    justify-content: space-between;
    width: 50%;
}

.form-container {
    background-color: white;
    height: 40vh;
    width: 25vw;
    color: black;
    display: flex;
    justify-content: space-between;
}

.title {
    margin-bottom: 3vh;
}

form {
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    width: 100%;
}

.fields-container {
    width: 100%;
}

.form-control {
    margin: 5px 3px;
    display: flex;
    flex-direction: column;
    background-color: inherit;
    color: black;
    border: none;
    justify-content: flex-start;
    align-items: flex-start;
    width: 100%;
}

label {
    font-weight: bold;
}

input {
    width: 100%;
    border: none;
    border-bottom: 1px solid gray;
    outline: none;
}

input:focus {
    border: none;
    border-bottom: 1px solid black;
}

.submit-button {
    background-color: blue;
    color: white;
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

@keyframes slime-left {
    0% {border-radius: 12% 88% 46% 54% / 54% 34% 66% 46%;}
    25% {border-radius: 12% 88% 46% 54% / 54% 69% 31% 46%;}
    50% {border-radius: 12% 88% 80% 20% / 54% 75% 25% 46%;}
    75% {border-radius: 57% 43% 78% 22% / 26% 75% 25% 74%;}
    100% {border-radius: 12% 88% 46% 54% / 54% 34% 66% 46%;}
}

@keyframes slime-right {
    0% {border-radius: 69% 31% 55% 45% / 25% 75% 25% 75%;}
    25% {border-radius: 69% 31% 55% 45% / 25% 30% 70% 75%;}
    50% {border-radius: 69% 31% 55% 45% / 63% 30% 70% 37%;}
    75% {border-radius: 29% 71% 24% 76% / 63% 24% 76% 37%;}
    100% {border-radius: 69% 31% 55% 45% / 25% 75% 25% 75%;}
}

</style>