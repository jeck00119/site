import { get, post } from '../../utils/requests.js';
import { ipAddress, port } from "../../url.js";

export default {
    async loadInspectionList(context) {
        const {response, responseData} = await get(`http://${ipAddress}:${port}/inspection_list`);

        if(!response.ok)
        {
            const error = new Error(responseData.detail || "Failed to fetch the inspection list!");
            throw error;
        }
        else
        {
            if(responseData)
            {
                context.commit('setColumnNames', responseData.columns || []);
                context.commit('setColumnTypes', responseData.columnTypes || []);

                if(responseData.inspections) {
                    context.dispatch('convertAndSetInspections', responseData.inspections);
                } else {
                    context.commit('setInspections', []);
                }
            }
        }
    },

    setColumnNames(context, payload) {
        context.commit('setColumnNames', payload);
    },

    setColumnTypes(context, payload) {
        context.commit('setColumnTypes', payload);
    },

    setInspections(context, payload) {
        context.commit('setInspections', payload);
    },

    convertAndSetInspections(context, payload) {
        let inspections = [];

        if(payload && typeof payload === 'object') {
            for(const [key, value] of Object.entries(payload))
            {
                inspections.push({
                    "Name": key,
                    ...value
                });
            }
        }

        context.commit('setInspections', inspections);
    },

    async updateInspectionList(context, payload) {
        const token = context.rootGetters["auth/getToken"];

        const response = await post(`http://${ipAddress}:${port}/inspection_list`, payload, {
            "content-type": "application/json",
            "Authorization": token
        });

        if(!response.ok)
        {
            const error = new Error("Failed to update the inspection list!");
            throw error;
        }
        else
        {
            if(payload)
            {
                context.commit('setColumnNames', payload.columns);
                context.commit('setColumnTypes', payload.columnTypes);
                context.dispatch('convertAndSetInspections', payload.inspections);
            }
        }
    }
}