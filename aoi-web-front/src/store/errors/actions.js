export default {
    removeError(context, payload){
        const id = payload.errorId;
        context.commit('removeError', id);
    },

    addError(context, payload) {
        context.commit('addError', payload);
    }
}