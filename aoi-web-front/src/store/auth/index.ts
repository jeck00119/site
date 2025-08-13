import getters from "./getters";
import mutations from "./mutations";
import actions from "./actions";

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