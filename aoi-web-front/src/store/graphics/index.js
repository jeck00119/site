import getters from './getters.js';
import actions from './actions.js';
import mutations from './mutations.js';

export default {
    namespaced: true,
    state() {
        return {
            canvas: null,
            graphicItems: [],
            referenceGraphicItems: [],
            compoundGraphicItems: []
        };
    },

    getters: getters,
    mutations: mutations,
    actions: actions
}