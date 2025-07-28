import { get, post, postStream } from "../../utils/requests";
import { ipAddress, port } from "../../url.js";

import { uuid } from "vue3-uuid";

let timer;

export default {
    async loadUsers(context) {
        const { response, responseData } = await get(`http://${ipAddress}:${port}/auth/users`);

        if(!response.ok)
        {
            const error = new Error(`Failed to load users!`);
            throw error;
        }
        else
        {
            context.commit('setUsers', responseData);
        }
    },

    async loadAvailableRoles(context) {
        const { response, responseData } = await get(`http://${ipAddress}:${port}/auth/roles`);

        if(!response.ok)
        {
            const error = new Error(`Failed to load roles!`);
            throw error;
        }
        else
        {
            context.commit('setAvailableRoles', responseData);
        }
    },

    async updateUsersRole(context, payload) {
        const token = context.rootGetters["auth/getToken"];

        const response = await post(`http://${ipAddress}:${port}/auth/update_role`, payload, {
            'content-type': 'application/json',
            'Authorization': token
        });

        if(!response.ok)
        {
            const error = new Error(`Failed to update user's role!`);
            throw error;
        }
        else
        {
            context.commit('updateUsersRole', payload);
        }
    },

    async addUser(context, payload) {
        let user = {
            uid: uuid.v4(),
            username: payload.username,
            password: payload.password,
            level: ''
        };

        const response = await post(`http://${ipAddress}:${port}/auth/create_user`, user);

        if(!response.ok)
        {
            const error = new Error(`Failed to add user!`);
            throw error;
        }
        else
        {
            const responseData = await response.json();

            const userData = response.headers.get('user-data');
            const tokenExpiration = response.headers.get('token-expiration');
            const userLevel = response.headers.get('level');

            const expiresIn = +tokenExpiration * 1000;

            const expirationDate = new Date().getTime() + expiresIn;

            localStorage.setItem('auth-token', 'Bearer ' + responseData["access_token"]);
            localStorage.setItem('user', userData);
            localStorage.setItem('expiration-date', expirationDate);
            localStorage.setItem('level', userLevel);

            timer = setTimeout(function() {
                context.dispatch('autoLogout');
            }, expiresIn);

            context.commit('addUser',  user);

            context.commit('setUser', {
                token: 'Bearer ' + responseData["access_token"],
                user: {
                    username: userData,
                    level: userLevel
                }
            });
        }
    },

    async login(context, payload) {
        const response = await postStream(`http://${ipAddress}:${port}/auth/login`, new URLSearchParams(payload), {
            'Content-Type': 'application/x-www-form-urlencoded'
        });

        if(!response.ok)
        {
            const error = new Error(`Failed to login!`);
            throw error;
        }
        else
        {
            const responseData = await response.json();

            const userData = response.headers.get('user-data');
            const tokenExpiration = response.headers.get('token-expiration');
            const userLevel = response.headers.get('level');

            const expiresIn = +tokenExpiration * 1000;

            const expirationDate = new Date().getTime() + expiresIn;

            localStorage.setItem('auth-token', 'Bearer ' + responseData["access_token"]);
            localStorage.setItem('user', userData);
            localStorage.setItem('expiration-date', expirationDate);
            localStorage.setItem('level', userLevel);

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
    },

    autoLogout(context) {
        context.dispatch('logout');
        context.commit('setAutoLogout');
    },

    logout(context) {
        localStorage.removeItem('auth-token');
        localStorage.removeItem('user');
        localStorage.removeItem('expiration-date');
        localStorage.removeItem('level');

        clearTimeout(timer);

        context.commit('logout');
    },

    tryLogin(context) {
        const authToken = localStorage.getItem('auth-token');
        const userData = localStorage.getItem('user');
        const tokenExpiration = localStorage.getItem('expiration-date');
        const userLevel = localStorage.getItem('level');

        const expiresIn = +tokenExpiration - new Date().getTime();

        if(expiresIn < 0) {
            localStorage.removeItem('auth-token');
            localStorage.removeItem('user');
            localStorage.removeItem('expiration-date');
            localStorage.removeItem('level');
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