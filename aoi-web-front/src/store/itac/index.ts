import getters from "./getters";
import mutations from "./mutations";
import actions from "./actions";

export default {
    namespaced: true,

    state() {
        return {
            itacList: []
        };
    },

    getters: getters,
    mutations: mutations,
    actions: actions
}