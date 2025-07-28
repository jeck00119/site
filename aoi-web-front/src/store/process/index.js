import getters from "./getters.js";
import mutations from "./mutations.js";
import actions from "./actions.js";

export default {
    namespaced: true,
    state() {
        return {
            inspectionResults: [],
            currentInspectionResult: null,
            excelBlob : null,
            excelBlobPath:null,
            capabilityState:null,
            offsetState:null,
            itacState:null,
            processStatus:'IDLE',
            dmc: null
        }
    },

    getters: getters,
    mutations: mutations,
    actions: actions
}