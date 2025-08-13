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

    userLevel(state) {
        return state.currentUser?.level;
    },

    permissions(state) {
        // Return user permissions based on level or role
        if (!state.currentUser) return [];
        
        const level = state.currentUser.level;
        switch(level) {
            case 'admin':
                return ['read', 'write', 'delete', 'admin'];
            case 'user':
                return ['read', 'write'];
            case 'guest':
                return ['read'];
            default:
                return [];
        }
    },
}