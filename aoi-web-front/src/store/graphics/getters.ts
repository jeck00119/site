import { canvasRegistry } from '../../utils/canvasRegistry';

export default {
    getCurrentGraphics(state) {
        return state.graphicItems;
    },

    getCurrentReferenceGraphics(state) {
        return state.referenceGraphicItems;
    },

    getCanvas(state) {
        return state.canvasId ? canvasRegistry.get(state.canvasId) : null;
    },

    getCurrentCompoundGraphics(state) {
        return state.compoundGraphicItems;
    },

    getCurrentCompoundGraphicsAtIdx: (state) => (idx) => {
        return state.compoundGraphicItems[idx];
    }
}