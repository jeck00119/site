export default {
    setModels(state, payload) {
        state.models = payload;
    },

    addModel(state, payload) {
        state.models.push(payload);
    }
}