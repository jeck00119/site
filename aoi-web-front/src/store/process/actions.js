import api from "../../utils/api.js";

export default {
    async startProcessing(_, payload) {
        const { response, responseData } = await api.get(`/processing/start_process?offline=${payload.offline}`);
        if (!response.ok) {
            const error = new Error(responseData.detail || "Failed to process with the current configuration!");
            throw error;
        }
    },

    async stopProcessing() {
        await api.get('/processing/stop_process');
    },

    async getCapabilityReport(context) {
        const url = await api.getFullUrl('/processing/capability_report');

        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'content-type': 'attachment'
            }
        });

        let blobURL = null;

        await response.blob()
            .then((myBlob) => {
                blobURL = URL.createObjectURL(myBlob);
            });

        context.commit("setExcelBlob", { 'excelBlob': 'blob', 'excelBlobPath': blobURL });
    },


    async getCapabilityState(context) {
        const { response, responseData } = await api.get('/processing/capability/state');
        context.commit("setCapabilityState", responseData);
    },

    async getOffsetState(context) {
        const { response, responseData } = await api.get('/processing/offset/state');
        context.commit("setOffsetState", responseData);

    },

    async getItacState(context) {
        const { response, responseData } = await api.get('/processing/itac/state');
        context.commit("setItacState", responseData);

    },

    async postCapabilityState(context) {
        const negCapabilityState = !context.state.capabilityState

        const { response, responseData } = await api.put(`/processing/capability/state?state=${negCapabilityState}`)
    },

    async postOffsetState(context) {
        const negOffsetState = !context.state.offsetState
        const { response, responseData } = await api.put(`/processing/offset/state?state=${negOffsetState}`)
    },

    async postItacState(context) {
        const negItacState = !context.state.itacState
        const { response, responseData } = await api.put(`/processing/itac/state?state=${negItacState}`)
    },

    resetInspectionResultsStatus(context) {
        context.commit("resetInspectionResultsStatus");
    },

    async setSaveFailImgsFlag(_, payload) {
        const { response, responseData } = await api.post('/processing/save_image_flag', payload);

        if(!response.ok)
        {
            const error = new Error(responseData.detail || `Failed to toggle save fail images flag to ${payload}!`);
            throw error;
        }
    },

    async closeProcessStateSocket(_, payload) {
        const { response, responseData } = await api.post(`/processing/${payload.uid}/ws/close`);

        if(!response.ok)
        {
            const error = new Error(responseData.detail || `Failed to close socket for CNC with ID ${payload.uid}!`);
            throw error;
        }
    }
}