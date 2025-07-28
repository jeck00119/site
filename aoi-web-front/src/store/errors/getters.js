export default {
    getErrors(state){
        return state.errors;
    },

    isEmpty(state) {
        return state.errors.length === 0;
    },

    numberOfErrors(state) {
        return state.errors.length;
    }
}