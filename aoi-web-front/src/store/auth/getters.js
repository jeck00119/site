export default {
    getUsers(state) {
        return state.users;
    },

    didAutoLogout(state) {
        return state.didAutoLogout;
    },

    getToken(state) {
        return state.token;
    },

    getCurrentUser(state) {
        return state.currentUser;
    },

    getAvailableRoles(state) {
        return state.availableRoles;
    },

    isAuthenticated(state) {
        return !!state.token;
    },
}