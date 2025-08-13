export default {
    getConfigurations(state) {
        return state.configurations;
    },

    getConfigurationById: (state) => (id) => {
        return state.configurations.find(configuration => configuration.uid === id);
    },

    getCurrentConfiguration(state) {
        return state.currentConfiguration;
    }
}