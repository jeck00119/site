import api from "../../utils/api";
import { handleApiError, getAuthErrorMessage } from "../../utils/errorHandler";

import { uuid } from "vue3-uuid";

let timer;
let expirationCheckInterval;

// Function to start periodic token expiration check
function startExpirationCheck(context) {
    // Clear any existing interval
    if (expirationCheckInterval) {
        clearInterval(expirationCheckInterval);
    }
    
    // Check token expiration every 5 seconds
    expirationCheckInterval = setInterval(() => {
        const tokenExpiration = sessionStorage.getItem('expiration-date');
        if (tokenExpiration) {
            const expiresIn = +tokenExpiration - new Date().getTime();
            if (expiresIn <= 0) {
                console.warn('Token expired - auto-logout triggered by periodic check');
                context.dispatch('autoLogout');
                clearInterval(expirationCheckInterval);
            }
        } else {
            // No expiration date found, stop checking
            clearInterval(expirationCheckInterval);
        }
    }, 5000); // Check every 5 seconds
}

export default {
    async loadUsers(context) {
        try {
            const { response, responseData } = await api.get('/auth/users');

            if (!response.ok) {
                const error = new Error(responseData?.detail || "Failed to load users!");
                throw error;
            } else {
                context.commit('setUsers', responseData);
            }
        } catch (error) {
            console.error('Failed to load users:', error);
            throw error;
        }
    },

    async loadAvailableRoles(context) {
        try {
            const { response, responseData } = await api.get('/auth/roles');

            if (!response.ok) {
                const error = new Error(`Failed to load roles!`);
                throw error;
            } else {
                context.commit('setAvailableRoles', responseData);
            }
        } catch (error) {
            console.error('Failed to load available roles:', error);
            throw error;
        }
    },

    async updateUsersRole(context, payload) {
        try {
            const token = context.rootGetters["auth/getToken"];

            const { response } = await api.post('/auth/update_role', payload, {
                'content-type': 'application/json',
                'Authorization': token
            });

            if (!response.ok) {
                const error = new Error(`Failed to update user's role!`);
                throw error;
            } else {
                context.commit('updateUsersRole', payload);
            }
        } catch (error) {
            console.error('Failed to update user role:', error);
            throw error;
        }
    },

    async addUser(context, payload) {
        try {
            let user = {
                uid: uuid.v4(),
                username: payload.username,
                password: payload.password,
                level: ''
            };

            const { response, responseData } = await api.post('/auth/create_user', user);

            if (!response.ok) {
                const error = new Error(`Failed to add user!`);
                throw error;
            } else {
                const userData = response.headers.get('user-data');
                const tokenExpiration = response.headers.get('token-expiration');
                const userLevel = response.headers.get('level');

                const expiresIn = +tokenExpiration * 1000;
                const expirationDate = new Date().getTime() + expiresIn;

                sessionStorage.setItem('auth-token', 'Bearer ' + responseData["access_token"]);
                sessionStorage.setItem('user', userData);
                sessionStorage.setItem('expiration-date', expirationDate.toString());
                sessionStorage.setItem('level', userLevel);

                timer = setTimeout(function() {
                    context.dispatch('autoLogout');
                }, expiresIn);

                context.commit('addUser', user);

                context.commit('setUser', {
                    token: 'Bearer ' + responseData["access_token"],
                    user: {
                        username: userData,
                        level: userLevel
                    }
                });

                // Start periodic expiration check
                startExpirationCheck(context);
            }
        } catch (error) {
            console.error('Failed to add user:', error);
            throw error;
        }
    },

    async login(context, payload) {
        try {
            // Convert FormData to proper URLSearchParams for OAuth2PasswordRequestForm
            let formData;
            if (payload instanceof FormData) {
                formData = new URLSearchParams();
                for (let [key, value] of payload.entries()) {
                    formData.append(key, value.toString());
                }
            } else {
                formData = new URLSearchParams(payload);
            }
            
            const { response, responseData } = await api.postStream('/auth/login', formData, {
                'Content-Type': 'application/x-www-form-urlencoded'
            });

            if (!response || !response.ok) {
                // Use centralized error handling following existing patterns
                const errorMessage = getAuthErrorMessage(responseData, response);
                const error = new Error(errorMessage);
                throw error;
            } else {
                const userData = response.headers.get('user-data');
                const tokenExpiration = response.headers.get('token-expiration');
                const userLevel = response.headers.get('level');

                console.log('Login successful - User:', userData, 'Level:', userLevel);

                const expiresIn = +tokenExpiration * 1000;
                const expirationDate = new Date().getTime() + expiresIn;

                sessionStorage.setItem('auth-token', 'Bearer ' + responseData["access_token"]);
                sessionStorage.setItem('user', userData);
                sessionStorage.setItem('expiration-date', expirationDate.toString());
                sessionStorage.setItem('level', userLevel);

                timer = setTimeout(function() {
                    context.dispatch('autoLogout');
                }, expiresIn);

                context.commit('setUser', {
                    token: 'Bearer ' + responseData["access_token"],
                    user: {
                        username: userData,
                        level: userLevel
                    }
                });
                
                console.log('User committed to store with level:', userLevel);

                // Start periodic expiration check
                startExpirationCheck(context);
            }
        } catch (error) {
            console.error('Failed to login:', error);
            throw error;
        }
    },

    autoLogout(context) {
        context.dispatch('logout');
        context.commit('setAutoLogout');
    },

    logout(context) {
        sessionStorage.removeItem('auth-token');
        sessionStorage.removeItem('user');
        sessionStorage.removeItem('expiration-date');
        sessionStorage.removeItem('level');

        clearTimeout(timer);
        clearInterval(expirationCheckInterval);

        context.commit('logout');
    },

    tryLogin(context) {
        const authToken = sessionStorage.getItem('auth-token');
        const userData = sessionStorage.getItem('user');
        const tokenExpiration = sessionStorage.getItem('expiration-date');
        const userLevel = sessionStorage.getItem('level');

        const expiresIn = +tokenExpiration - new Date().getTime();

        if(expiresIn < 0) {
            sessionStorage.removeItem('auth-token');
            sessionStorage.removeItem('user');
            sessionStorage.removeItem('expiration-date');
            sessionStorage.removeItem('level');
            return;
        }

        timer = setTimeout(function() {
            context.dispatch('autoLogout');
        }, expiresIn);

        if(authToken && userData)
        {
            context.commit('setUser', {
                token: authToken,
                user: {
                    username: userData,
                    level: userLevel
                }
            });

            // Start periodic expiration check for existing sessions
            startExpirationCheck(context);
        }
    }
}