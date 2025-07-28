export default {
    removeError(state, id){
        const errorIndex = state.errors.findIndex(error => error.id === id);
        state.errors.splice(errorIndex, 1);
    },

    addError(state, payload) {
        state.errors.push(payload);
    }
}