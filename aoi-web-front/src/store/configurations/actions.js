import { uuid } from "vue3-uuid";
import { get, post, update, remove } from '../../utils/requests.js';
import { ipAddress, port } from "../../url.js";

export default {
    async loadConfigurations(context) {
        const { response, responseData } = await get(`http://${ipAddress}:${port}/configurations`);

        if(!response.ok)
        {
            const error = new Error(`Failed to load configurations!`);
            throw error;
        }
        else
        {
            context.commit('setConfigurations', responseData);
        }
    },

    async loadConfiguration(context, payload) {
        const {response, _} = await get(`http://${ipAddress}:${port}/configurations/${payload.uid}`);

        if(!response.ok)
        {
            const error = new Error(`Failed to load configurations with name ${payload.name}!`);
            throw error;
        }
        else
        {
            context.commit('setCurrentConfiguration', payload);
        }
    },

    setCurrentConfiguration(context, payload) {
        context.commit('setCurrentConfiguration', payload);
    },

    async removeConfiguration(context, payload) {
        const token = context.rootGetters["auth/getToken"];

        const response = await remove(`http://${ipAddress}:${port}/configurations/${payload.uid}`, {
            "content-type": "application/json",
            "Authorization": token
        });

        if(!response.ok)
        {
            const error = new Error(`Failed to remove configuration with id: ${payload.uid}!`);
            throw error;
        }
        else
        {
            context.commit('removeConfiguration', payload);
        }
    },

    async editConfiguration(context, payload) {
        const token = context.rootGetters["auth/getToken"];

        const response = await update(`http://${ipAddress}:${port}/configurations/${payload.uid}`, payload, {
            "content-type": "application/json",
            "Authorization": token
        });

        if(!response.ok)
        {
            const error = new Error(`Failed to edit configuration with id: ${payload.uid}!`);
            throw error;
        }
        else
        {
            context.commit('editConfiguration', payload);
        }
    },

    async addConfiguration(context, payload) {
        payload.uid = uuid.v4();

        const token = context.rootGetters["auth/getToken"];

        const response = await post(`http://${ipAddress}:${port}/configurations`, payload, {
            "content-type": "application/json",
            "Authorization": token
        });

        if(!response.ok)
        {
            const error = new Error(`Failed to add new configuration: ${payload.name}!`);
            throw error;
        }
        else
        {
            context.commit('addConfiguration', payload);
        }
    },

    async copyConfiguration(context, payload) {
        payload.config.uid = uuid.v4();

        const token = context.rootGetters["auth/getToken"];

        const response = await post(`http://${ipAddress}:${port}/configurations/copy/${payload.originalConfigId}`, payload.config, {
            "content-type": "application/json",
            "Authorization": token
        });

        if(!response.ok)
        {
            const error = new Error(`Failed to add new configuration: ${payload.config.name}!`);
            throw error;
        }
        else
        {
            context.commit('addConfiguration', payload.config);
        }
    },

    async resetAllDatabases() {
        const response = await post(`http://${ipAddress}:${port}/configurations/reset_all_dbs`, null);

        if(!response.ok)
        {
            const error = new Error(`Failed to reset the databases!`);
            throw error;
        }
    },

    async tryLoadConfiguration(context) {
        const { response, responseData } = await get(`http://${ipAddress}:${port}/configurations/current`);

        if(!response.ok)
        {
            const error = new Error(`Failed to retrieve current configuration!`);
            throw error;
        }
        else
        {
            if(responseData)
            {
                context.commit('setCurrentConfiguration', responseData);
            }
        }
    },

    unloadConfiguration(context) {
        context.commit('setCurrentConfiguration', null);
    },

    async closeConfigurationChangedSocket(_, payload) {
        const response = await post(`http://${ipAddress}:${port}/configurations/${payload.uid}/ws/close`);

        if(!response.ok)
        {
            const error = new Error(`Failed to close configuration changes notifier socket!`);
            throw error;
        }
    }
}