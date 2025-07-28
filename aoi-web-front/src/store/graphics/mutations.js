export default {
    setGraphicItems(state, payload) {
        state.graphicItems = payload.items;
    },

    resetGraphicsItems(state) {
        state.graphicItems = [];
    },

    setReferenceGraphicItems(state, payload) {
        state.referenceGraphicItems = payload.items;
    },

    resetReferenceGraphicItems(state) {
        state.referenceGraphicItems = [];
    },

    setCanvas(state, payload) {
        state.canvas = payload;
    },

    addGraphicsToCompoundItems(state, payload) {
        state.compoundGraphicItems.push(payload);
    },

    setCompoundGraphicItems(state, payload) {
        state.compoundGraphicItems = payload;
    },

    resetCompoundGraphicItems(state) {
        state.compoundGraphicItems = [];
    }
}