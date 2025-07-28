import { uuid } from "vue3-uuid";
import { get, post } from "../../utils/requests";
import { ipAddress, port } from "../../url.js";

export default {
    async loadProfilometers(context) {
        const { response, responseData } = await get(`http://${ipAddress}:${port}/profilometer`);

        if(!response.ok)
        {
            const error = new Error(responseData.detail || `Failed to fetch profilometers!`);
            throw error;
        }
        else
        {
            context.commit('loadProfilometers', responseData);
        }
    },

    async loadProfilometerTypes(context) {
        const { response, responseData } = await get(`http://${ipAddress}:${port}/profilometer/profilometer_types`);

        if(!response.ok)
        {
            const error = new Error(responseData.detail || `Failed to fetch profilometer types!`);
            throw error;
        }
        else
        {
            context.commit('loadProfilometerTypes', responseData);
        }
    },

    resetProfilometers(context) {
        context.commit('resetProfilometers');
    },

    resetProfilometerTypes(context) {
        context.commit('resetProfilometerTypes');
    },

    addProfilometer(context, payload) {
        const profilometer = {
            uid: uuid.v4(),
            name: payload.name,
            type: payload.type,
            id: payload.id,
            path: payload.path
        };

        context.commit('addProfilometer', profilometer);
    },

    removeProfilometer(context, payload) {
        context.commit('removeProfilometer', payload);
    },

    async saveProfilometers(context) {
        const profilometers = context.getters.getProfilometers;
        const token = context.rootGetters["auth/getToken"];

        const response =  await post(`http://${ipAddress}:${port}/profilometer/save`, profilometers, {
            "content-type": "application/json",
            "Authorization": token
        });

        if(!response.ok)
        {
            const error = new Error(`Failed to save profilometers!`);
            throw error;
        }
    },

    updateProfilometerID(context, payload) {
        context.commit('updateProfilometerID', payload);
    },

    updateProfilometerServerPath(context, payload) {
        context.commit('updateProfilometerServerPath', payload);
    },

    updateProfilometerType(context, payload) {
        context.commit('updateProfilometerType', payload);
    }
}