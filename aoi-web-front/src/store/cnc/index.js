import getters from "./getters.js";
import mutations from "./mutations.js";
import actions from "./actions.js";

export default {
    namespaced: true,
    state() {
        return {
            cncs: [],
            cncTypes: [],
            ports: [],
            locations:null,
            cncStates: {},
            positionData: {},
            terminalStatus: ""
        };
    },

    getters: getters,
    mutations: mutations,
    actions: actions
}