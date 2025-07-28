import getters from "./getters.js";
import actions from "./actions.js";
import mutations from "./mutations.js";

export default {
    namespaced: true,
    state() {
        return {
            components: [],
            identifications: [],
            references: [],
            currentComponent: null
        };
    },

    getters: getters,
    actions: actions,
    mutations: mutations
}