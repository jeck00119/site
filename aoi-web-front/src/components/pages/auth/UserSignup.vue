<template>
    <div class="flex-container">
        <div class="slime"></div>
        <div class="title">
            <h1>Sign Up</h1>
        </div>
        <div class="parent-container">
            <div class="card-container">
                <div class="icons-container">
                    <v-icon name="fc-disclaimer" scale="2.5"/>
                    <v-icon name="fc-unlock" scale="2.5"/>
                    <v-icon name="fc-ok" scale="2.5"/>
                </div>
                <div class="text-container">
                    <h3>Create an account and unlock AOI web app features!</h3>
                </div>
            </div>
            <div class="form-container">
                <form @submit.prevent="signup">
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
                        <button class="submit-button">Continue</button>
                    </div>
                    <div>
                        <hr>
                        <router-link :to="'/login'">Already have an account?</router-link>
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
                    <v-icon :name="notificationIcon" scale="2.5" animation="float" />
                </div>
                <div class="text-wrapper">
                    {{ notificationMessage }}
                </div>
            </div>
        </base-notification>
    </div>
</template>

<script>
import { onMounted, ref, computed } from 'vue';
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

        const existingUsers = computed(function() {
            return store.getters["auth/getUsers"];
        });

        async function signup() {
            let existingUsernames = existingUsers.value.map(user => user.username);

            let error = false;

            if(email.value === '')
            {
                setNotification(3000, `Email field cannot be empty.`, 'bi-exclamation-circle-fill');
                error = true;
            }

            if(!email.value.includes('@forvia.com'))
            {
                setNotification(3000, `Please enter a valid email address.`, 'bi-exclamation-circle-fill');
                error = true;
            }

            if(password.value === '')
            {
                setNotification(3000, `Please choose a password.`, 'bi-exclamation-circle-fill');
                error = true;
            }

            if(existingUsernames.includes(email.value))
            {
                setNotification(3000, `The email provided is already associated with an account.`, 'bi-exclamation-circle-fill');
                error = true;
            }

            if(!error)
            {
                try {
                    await store.dispatch("auth/addUser", {
                        username: email.value,
                        password: password.value
                    });

                    router.replace('/');
                }catch(err) {
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
            signup,
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

.slime {
    position: absolute;
    top: 10%;
    left: 10%;
    z-index:0;
    width: 80%;
    height: 80%;
    background-color: rgb(204, 161, 82);
    animation-name: slime;
    animation-duration: 5s;
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
    z-index: 1;
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

@keyframes slime {
    0% {border-radius: 52% 48% 49% 51% / 45% 86% 14% 55%;}
    25% {border-radius: 19% 81% 68% 32% / 66% 44% 56% 34%; }
    50% {border-radius: 35% 65% 41% 59% / 27% 35% 65% 73%; }
    75% {border-radius: 35% 65% 65% 35% / 23% 80% 20% 77%; }
    100% {border-radius: 52% 48% 49% 51% / 45% 86% 14% 55%;}
}

@keyframes slime-second {
    0% {border-radius: 100% 0% 87% 13% / 49% 0% 100% 51%;}
    25% {border-radius: 100% 0% 92% 8% / 17% 0% 100% 83%;}
    50% {border-radius: 100% 0% 96% 4% / 4% 48% 52% 96%;}
    75% {border-radius: 100% 0% 100% 0% / 0% 80% 20% 100%;}
    100% {border-radius: 100% 0% 87% 13% / 49% 0% 100% 51%;}
}

</style>