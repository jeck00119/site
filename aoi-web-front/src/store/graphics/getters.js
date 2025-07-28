export default {
    getCurrentGraphics(state) {
        return state.graphicItems;
    },

    getCurrentReferenceGraphics(state) {
        return state.referenceGraphicItems;
    },

    getCanvas(state) {
        return state.canvas;
    },

    getCurrentCompoundGraphics(state) {
        return state.compoundGraphicItems;
    },

    getCurrentCompoundGraphicsAtIdx: (state) => (idx) => {
        return state.compoundGraphicItems[idx];
    }
}