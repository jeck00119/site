export default {
    getInspectionResults(state) {
        return state.inspectionResults;
    },

    getInspectionResultByIdx: (state) => (idx) => {
        return state.inspectionResults[idx];
    },

    getCurrentInspectionResult(state){
        return state.currentInspectionResult;
    },

    getExcelBlobPath(state){
        return state.excelBlobPath;
    },

    getExcelBlob(state){
        return state.excelBlob;
    },

    getCapabilityState(state){
        return state.capabilityState;
    },
    
    getOffsetState(state){
        return state.offsetState;
    },

    getItacState(state){
        return state.itacState;
    },

    getProcessStatus(state){
        return state.processStatus
    },

    getDMC(state) {
        return state.dmc;
    }
}