import getters from "./getters";
import mutations from "./mutations";
import actions from "./actions";

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