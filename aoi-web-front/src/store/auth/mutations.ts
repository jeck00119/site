export default {
    setUsers(state, payload) {
        state.users = payload;
    },

    setAvailableRoles(state, payload) {
        state.availableRoles = payload;
    },

    addUser(state, payload) {
        state.users.push(payload);
    },

    setAutoLogout(state) {
        state.didAutoLogout = true;
    },

    setUser(state, payload) {
        state.token = payload.token;
        state.currentUser = payload.user;
        state.didAutoLogout = false;
    },

    updateUsersRole(state, payload) {
        const idx = state.users.findIndex(user => user.uid === payload.uid);
        state.users[idx].level = payload.role;
    },

    logout(state) {
        state.token = null;
        state.currentUser = null;
    }
}