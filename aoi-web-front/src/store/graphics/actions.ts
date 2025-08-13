export default {
    setGraphicItems(context, payload) {
        context.commit('setGraphicItems', payload);
    },

    setReferenceGraphicItems(context, payload) {
        context.commit('setReferenceGraphicItems', payload);
    },

    resetGraphicsItems(context) {
        context.commit('resetGraphicsItems');
    },

    resetReferenceGraphicItems(context) {
        context.commit('resetReferenceGraphicItems');
    },

    setCanvas(context, payload) {
        context.commit('setCanvas', payload);
    },

    addGraphicsToCompoundItems(context, payload) {
        context.commit('addGraphicsToCompoundItems', payload)
    },

    setCompoundGraphicItems(context, payload) {
        context.commit('setCompoundGraphicItems', payload);
    },

    resetCompoundGraphicItems(context) {
        context.commit('resetCompoundGraphicItems');
    }
}