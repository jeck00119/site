import api from "../../utils/api";

export default {
    async loadEvents(context) {
        try {
            const { response, responseData } = await api.get('/media/events');

            if (!response.ok) {
                const error = new Error(`Failed to load events!`);
                throw error;
            } else {
                context.commit('setEvents', responseData);
            }
        } catch (error) {
            console.error('Failed to load media events:', error);
            throw error;
        }
    },

    async loadChannels(context) {
        try {
            const { response, responseData } = await api.get('/media/channels');

            if (!response.ok) {
                const error = new Error(`Failed to load channels!`);
                throw error;
            } else {
                context.commit('setChannels', responseData);
            }
        } catch (error) {
            console.error('Failed to load media channels:', error);
            throw error;
        }
    },

    async loadFiles(context) {
        try {
            const { response, responseData } = await api.get('/media/files');

            if (!response.ok) {
                const error = new Error(`Failed to load files!`);
                throw error;
            } else {
                context.commit('setFiles', responseData);
            }
        } catch (error) {
            console.error('Failed to load media files:', error);
            throw error;
        }
    },

    async addChannel(context) {
        try {
            const token = context.rootGetters["auth/getToken"] || sessionStorage.getItem('auth-token');
            
            const { response } = await api.post('/media/channel', {}, {
                "content-type": "application/json",
                "Authorization": token
            });

            if (!response.ok) {
                const error = new Error(`Failed to add channel!`);
                throw error;
            } else {
                context.commit('addChannel');
            }
        } catch (error) {
            console.error('Failed to add media channel:', error);
            throw error;
        }
    },

    async addEvent(context, payload) {
        try {
            const token = context.rootGetters["auth/getToken"] || sessionStorage.getItem('auth-token');
             
            const { response } = await api.post('/media/add_event', payload, {
                "content-type": "application/json",
                "Authorization": token
            });

            if (!response.ok) {
                const error = new Error(`Failed to add event!`);
                throw error;
            }
        } catch (error) {
            console.error('Failed to add media event:', error);
            throw error;
        }
    }
}