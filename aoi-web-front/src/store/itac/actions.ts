import { get, post, remove, update } from "../../utils/requests";
import { ipAddress, port } from "../../url";

export default {
    async loadItacList(context) {
        const {response, responseData} = await get(`http://${ipAddress}:${port}/itac`);

        if(!response.ok)
        {
            const error = new Error(responseData.detail || "Failed to fetch the ITAC list!");
            throw error;
        }
        else
        {
            context.commit("loadItacList", responseData);
        }
    },

    async deleteItac(context, payload) {
        const token = context.rootGetters["auth/getToken"] || sessionStorage.getItem('auth-token');

        const response = await remove(`http://${ipAddress}:${port}/itac/`+ payload.uid, {
            "content-type": "application/json",
            "Authorization": token
        });

        if(!response.ok)
        {
            const error = new Error("Failed to delete ITAC configuration!");
            throw error;
        }
        else
        {
            context.commit("deleteItac", payload.uid);
        }
    },

    async saveItac(context, payload) {
        const token = context.rootGetters["auth/getToken"] || sessionStorage.getItem('auth-token');

        const response = await post(`http://${ipAddress}:${port}/itac`, payload, {
            "content-type": "application/json",
            "Authorization": token
        });

        if(!response.ok)
        {
            const error = new Error("Failed to save ITAC configuration!");
            throw error;
        }
        else
        {
            context.commit("saveItac", payload);
        }
    },

    async updateItac(context, payload) {
        const token = context.rootGetters["auth/getToken"] || sessionStorage.getItem('auth-token');

        const response = await update(`http://${ipAddress}:${port}/itac/`+ payload.uid, payload, {
            "content-type": "application/json",
            "Authorization": token
        });

        if(!response.ok)
        {
            const error = new Error("Failed to update ITAC configuration!");
            throw error;
        }
        else
        {
            context.commit("updateItac", payload);
        }
    }
}