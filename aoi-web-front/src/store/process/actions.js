import { get, patch, post, put } from "../../utils/requests"
import { ipAddress, port } from "../../url.js";

export default {
    async startProcessing(_, payload) {
        const url = `http://${ipAddress}:${port}/processing/start_process?offline=${payload.offline}`;
        const { response, responseData } = await get(url);
        if (!response.ok) {
            const error = new Error(responseData.detail || "Failed to process with the current configuration!");
            throw error;
        }
    },

    async stopProcessing() {
        await get(`http://${ipAddress}:${port}/processing/stop_process`);
    },

    async getCapabilityReport(context) {
        const url = `http://${ipAddress}:${port}/processing/capability_report`

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
        const url = `http://${ipAddress}:${port}/processing/capability/state`
        const { response, responseData } = await get(url);
        context.commit("setCapabilityState", responseData);
    },

    async getOffsetState(context) {
        const url = `http://${ipAddress}:${port}/processing/offset/state`
        const { response, responseData } = await get(url);
        context.commit("setOffsetState", responseData);

    },

    async getItacState(context) {
        const url = `http://${ipAddress}:${port}/processing/itac/state`
        const { response, responseData } = await get(url);
        context.commit("setItacState", responseData);

    },

    async postCapabilityState(context) {
        const negCapabilityState = !context.state.capabilityState

        const url = `http://${ipAddress}:${port}/processing/capability/state?state=${negCapabilityState}`
        const { response, responseData } = await put(url)
    },

    async postOffsetState(context) {
        const negOffsetState = !context.state.offsetState
        const url = `http://${ipAddress}:${port}/processing/offset/state?state=${negOffsetState}`
        const { response, responseData } = await put(url)
    },

    async postItacState(context) {
        const negItacState = !context.state.itacState
        const url = `http://${ipAddress}:${port}/processing/itac/state?state=${negItacState}`
        const { response, responseData } = await put(url)
    },

    resetInspectionResultsStatus(context) {
        context.commit("resetInspectionResultsStatus");
    },

    async setSaveFailImgsFlag(_, payload) {
        const response = await post(`http://${ipAddress}:${port}/processing/save_image_flag`, payload);

        if(!response.ok)
        {
            const error = new Error(`Failed to toggle save fail images flag to ${payload}!`);
            throw error;
        }
    },

    async closeProcessStateSocket(_, payload) {
        const response = await post(`http://${ipAddress}:${port}/processing/${payload.uid}/ws/close`);

        if(!response.ok)
        {
            const error = new Error(`Failed to close socket for CNC with ID ${payload.uid}!`);
            throw error;
        }
    }
}