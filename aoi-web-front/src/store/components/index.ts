import getters from "./getters";
import actions from "./actions";
import mutations from "./mutations";

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