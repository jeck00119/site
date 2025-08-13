export default {
    setInspectionResults(state, payload) {
        state.inspectionResults = payload;
    },

    setDMC(state, payload) {
        state.dmc = payload;
    },

    setCurrentInspectionResult(state,payload){
        for (let i=0; i<state.inspectionResults.length; i++){
            if(state.inspectionResults[i].name === payload){
                state.currentInspectionResult = state.inspectionResults[i];
                break;
            }  
        }
    },

    setExcelBlob(state, payload){
        state.excelBlob = payload.excelBlob
        state.excelBlobPath = payload.excelBlobPath
    },

    setCapabilityState(state, payload){
        state.capabilityState = payload
    },

    setOffsetState(state, payload){
        state.offsetState = payload
    },

    setItacState(state, payload){
        state.itacState = payload
    },

    setProcessStatus(state, payload){
        state.processStatus = payload
    },

    resetInspectionResultsStatus(state) {
        for(const inspectionIdx in state.inspectionResults)
        {
            for(const dataIdx in state.inspectionResults[inspectionIdx].data)
            {
                state.inspectionResults[inspectionIdx].data[dataIdx].pass = true;
            }
        }
    }
}