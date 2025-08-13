import getters from "./getters";
import actions from "./actions";
import mutations from "./mutations";

export default {
    namespaced: true,
    state() {
        return {
            canvasId: null, // Store canvas ID instead of canvas object
            graphicItems: [],
            referenceGraphicItems: [],
            compoundGraphicItems: []
        };
    },

    getters: getters,
    mutations: mutations,
    actions: actions
}