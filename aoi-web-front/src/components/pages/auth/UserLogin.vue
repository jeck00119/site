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
                            <input 
                                type="text" 
                                id="email" 
                                :value="formData.email" 
                                @input="updateField('email', $event.target.value)"
                                :class="{ 'error': formErrors.email }"
                            />
                            <span v-if="formErrors.email" class="error-message">{{ formErrors.email }}</span>
                        </div>
                        <div class="form-control">
                            <label for="password">Password:</label>
                            <input 
                                type="password" 
                                id="password" 
                                :value="formData.password" 
                                @input="updateField('password', $event.target.value)"
                                :class="{ 'error': formErrors.password }"
                            />
                            <span v-if="formErrors.password" class="error-message">{{ formErrors.password }}</span>
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

import { useAuthStore, useFormState } from '@/composables/useStore';
import useNotification from '../../../hooks/notifications.js';
import { validateEmail, validatePassword, validateRequired, sanitizeInput } from '../../../utils/validation.js';

export default{
    setup() {
        const {showNotification, notificationMessage, notificationIcon, notificationTimeout, 
            setNotification, clearNotification} = useNotification();

        const authStore = useAuthStore();
        const router = useRouter();
        
        // Use form state composable for form management
        const { formData, updateField, resetForm } = useFormState({
            email: '',
            password: ''
        });

        // Form validation state
        const formErrors = ref({});

        // Validate individual field
        const validateField = (fieldName, value) => {
            const errors = {};
            
            if (fieldName === 'email') {
                const requiredResult = validateRequired(value, 'Email');
                if (!requiredResult.isValid) {
                    errors.email = requiredResult.errors[0];
                } else {
                    const emailResult = validateEmail(value);
                    if (!emailResult.isValid) {
                        errors.email = emailResult.errors[0];
                    }
                }
            }
            
            if (fieldName === 'password') {
                const requiredResult = validateRequired(value, 'Password');
                if (!requiredResult.isValid) {
                    errors.password = requiredResult.errors[0];
                } else {
                    const passwordResult = validatePassword(value);
                    if (!passwordResult.isValid) {
                        errors.password = passwordResult.errors[0];
                    }
                }
            }
            
            return errors;
        };

        // Enhanced field update with validation
        const onFieldUpdate = (fieldName, value) => {
            // Update field value
            updateField(fieldName, value);
            
            // Clear existing error when user starts typing
            if (formErrors.value[fieldName]) {
                const newErrors = { ...formErrors.value };
                delete newErrors[fieldName];
                formErrors.value = newErrors;
            }
        };

        // Validate entire form
        const validateForm = () => {
            const errors = {
                ...validateField('email', formData.value.email),
                ...validateField('password', formData.value.password)
            };
            
            formErrors.value = errors;
            return Object.keys(errors).length === 0;
        };

        async function login() {
            // Validate entire form
            const isValid = validateForm();
            
            if (!isValid) {
                // Show first validation error
                const firstError = Object.values(formErrors.value)[0];
                setNotification(3000, firstError, 'bi-exclamation-circle-fill');
                return;
            }
            {
                // Use centralized sanitization
                const sanitizedEmail = sanitizeInput(formData.value.email);
                const sanitizedPassword = formData.value.password.trim();
                
                const user = new FormData();
                user.append('username', sanitizedEmail);
                user.append('password', sanitizedPassword);
                
                try {
                    // Use auth store composable
                    await authStore.login(user);

                    router.replace('/configurations');
                    resetForm(); // Clear form after successful login
                }catch(e) {
                    // Display the specific error message from the backend
                    const errorMessage = e.message || 'Something went wrong. Please try again.';
                    setNotification(3000, errorMessage, 'bi-exclamation-circle-fill');
                }
            }
        }

        onMounted(() => {
            authStore.loadUsers();
        });

        return {
            formData,
            updateField: onFieldUpdate,
            formErrors,
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

input.error {
    border-bottom: 1px solid #dc3545;
}

.error-message {
    color: #dc3545;
    font-size: 0.8em;
    margin-top: 2px;
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