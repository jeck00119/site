export default {
    setConfigurations(state, payload) {
        state.configurations = payload;
    },

    setCurrentConfiguration(state, payload){
        state.currentConfiguration = payload;
    },

    removeConfiguration(state, payload) {
        const configurationIdx = state.configurations.findIndex(config => config.uid === payload.uid);
        state.configurations.splice(configurationIdx, 1);
    },

    editConfiguration(state, payload) {
        const configuration = state.configurations.find(config => config.uid === payload.uid);
        configuration.name = payload.name;
    },

    addConfiguration(state, payload) {
        state.configurations.push(payload);
    }
}