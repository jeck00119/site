export default {
    loadProfilometers(state, payload) {
        state.profilometers = payload;
    },

    loadProfilometerTypes(state, payload) {
        state.profilometerTypes = payload;
    },

    resetProfilometers(state) {
        state.profilometers = [];
    },

    resetProfilometerTypes(state) {
        state.profilometerTypes = [];
    },

    addProfilometer(state, payload) {
        state.profilometers.push(payload);
    },

    removeProfilometer(state, payload) {
        const idx = state.profilometers.findIndex(prof => prof.uid === payload.uid);
        state.profilometers.splice(idx, 1);
    },

    updateProfilometerID(state, payload) {
        const idx = state.profilometers.findIndex(prof => prof.uid === payload.uid);
        state.profilometers[idx].id = payload.id;
    },

    updateProfilometerServerPath(state, payload) {
        const idx = state.profilometers.findIndex(prof => prof.uid === payload.uid);
        state.profilometers[idx].path = payload.path;
    },

    updateProfilometerType(state, payload) {
        const idx = state.profilometers.findIndex(prof => prof.uid === payload.uid);
        state.profilometers[idx].type = payload.type;
    }
}