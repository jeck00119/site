import { get, post } from "../../utils/requests";
import { ipAddress, port } from "../../url.js";

export default {
    async loadEvents(context) {
        const  { response, responseData } = await get(`http://${ipAddress}:${port}/media/events`);

        if(!response.ok)
        {
            const error = new Error(`Failed to load events!`);
            throw error;
        }
        else
        {
            context.commit('setEvents', responseData);
        }
    },

    async loadChannels(context) {
        const  { response, responseData } = await get(`http://${ipAddress}:${port}/media/channels`);

        if(!response.ok)
        {
            const error = new Error(`Failed to load events!`);
            throw error;
        }
        else
        {
            context.commit('setChannels', responseData);
        }
    },

    async loadFiles(context) {
        const { response, responseData } = await get(`http://${ipAddress}:${port}/media/files`);

        if(!response.ok)
        {
            const error = new Error(`Failed to load events!`);
            throw error;
        }
        else
        {
            context.commit('setFiles', responseData);
        }
    },

    async addChannel(context) {
        const token = context.rootGetters["auth/getToken"];
        
        const response = await post(`http://${ipAddress}:${port}/media/channel`, {
            "content-type": "application/json",
            "Authorization": token
        });

        if(!response.ok)
        {
            const error = new Error(`Failed to add channel!`);
            throw error;
        }
        else
        {
            context.commit('addChannel');
        }
    },

    async addEvent(context, payload) {
        const token = context.rootGetters["auth/getToken"];
         
        const response = await post(`http://${ipAddress}:${port}/media/add_event`, payload, {
            "content-type": "application/json",
            "Authorization": token
        });

        if(!response.ok)
        {
            const error = new Error(`Failed to add event!`);
            throw error;
        }
    }
}