import api from "../../utils/api.js";

import { uuid } from "vue3-uuid";

let timer;

export default {
    async loadUsers(context) {
        try {
            const { response, responseData } = await api.get('/auth/users');

            if (!response.ok) {
                const error = new Error(`Failed to load users!`);
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
                sessionStorage.setItem('expiration-date', expirationDate);
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
            }
        } catch (error) {
            console.error('Failed to add user:', error);
            throw error;
        }
    },

    async login(context, payload) {
        try {
            const { response, responseData } = await api.postStream('/auth/login', new URLSearchParams(payload), {
                'Content-Type': 'application/x-www-form-urlencoded'
            });

            if (!response || !response.ok) {
                const error = new Error(`Failed to login! ${response ? `Status: ${response.status}` : 'Network error'}`);
                throw error;
            } else {
                const userData = response.headers.get('user-data');
                const tokenExpiration = response.headers.get('token-expiration');
                const userLevel = response.headers.get('level');

                const expiresIn = +tokenExpiration * 1000;
                const expirationDate = new Date().getTime() + expiresIn;

                sessionStorage.setItem('auth-token', 'Bearer ' + responseData["access_token"]);
                sessionStorage.setItem('user', userData);
                sessionStorage.setItem('expiration-date', expirationDate);
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
        }
    }
}