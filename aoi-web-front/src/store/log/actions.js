import { get, post, update, remove } from '../../utils/requests.js';
import { ipAddress, port } from "../../url.js";


export default {
    async loadEvents(context) {
        const { response, responseData } = await get(`http://${ipAddress}:${port}/log`);

        if(!response.ok) 
        {
            const error = new Error(`Could not load the events!`);
            throw error;
        }
        else
        {
            context.commit('setEvents', responseData);
        }
    },

    async addEvent(context, payload) {
        const currentDate = new Date();

        const timestamp = currentDate.getDate() + '/' 
                          + (currentDate.getMonth() + 1) + '/' 
                          + currentDate.getFullYear() + ' '
                          + currentDate.getHours() + ':'
                          + currentDate.getMinutes() + ':'
                          + currentDate.getSeconds();

        const event = {
            timestamp: timestamp,
            user: payload.user,
            type: payload.type,
            title: payload.title,
            description: payload.description,
            details: payload.details ? JSON.stringify(payload.details) : JSON.stringify(null)
        };

        const { response, responseData } = await post(`http://${ipAddress}:${port}/log/add`, event);

        if(!response.ok) 
        {
            const error = new Error(responseData.detail || `Could not add the event!`);
            throw error;
        }
        else
        {
            context.commit('addEvent', event);
        }
    },

    async removeEvent(context, payload) {
        const events = context.getters.getEvents;
        const eventId = events.findIndex(event => event.timestamp === payload.timestamp);

        const { response, responseData } = await remove(`http://${ipAddress}:${port}/log/${eventId}`);

        if(!response.ok) 
        {
            const error = new Error(responseData.detail || `Could not remove the event!`);
            throw error;
        }
        else
        {
            context.commit('removeEvent', {
                uid: eventId
            });
        }
    }
}