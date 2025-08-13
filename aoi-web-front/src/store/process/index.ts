import getters from "./getters";
import mutations from "./mutations";
import actions from "./actions";

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