import getters from "./getters.js";
import mutations from "./mutations.js";
import actions from "./actions.js";

export default {
    namespaced: true,
    state() {
        return {
            users: [],
            token: null,
            currentUser: null,
            didAutoLogout: false,
            availableRoles: []
        };
    },

    getters: getters,
    mutations: mutations,
    actions: actions
}