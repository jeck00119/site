import { v4 as uuidv4 } from "uuid";
import api from "../../utils/api";
import { logger } from "../../utils/logger";

export default {
    async addComponent(context, payload) {
        let component = null;

        if(payload.type === 'custom_component')
        {
            component = {
                uid: uuidv4(),
                name: payload.name,
                imageSourceUid: '',
                algorithms: [],
                blocks: []
            }
        }
        else
        {
            component = {
                uid: uuidv4(),
                name: payload.name,
                imageSourceUid: '',
                algorithmUid: '',
                algorithmType: '',
                referenceUid: ''
            };
        }

        const token = context.rootGetters["auth/getToken"] || sessionStorage.getItem('auth-token');

        const { response } = await api.post(`/${payload.type}`, component, {
            "content-type": "application/json",
            "Authorization": token
        });

        if(!response.ok) 
        {
            const error = new Error(`Could not create ${payload.type}!`);
            throw error;
        }
        else
        {
            if (payload.type === 'component' || payload.type === 'custom_component')
            {
                context.commit('addComponent', component);
            }
            else if (payload.type === 'identification')
            {
                context.commit('addIdentification', component);
            }
            else
            {
                context.commit('addReference', component);
            }
            
        }
    },

    async removeComponent(context, payload) {
        const token = context.rootGetters["auth/getToken"] || sessionStorage.getItem('auth-token');
        const { response } = await api.delete(`/${payload.type}/${payload.uid}`, {
            "content-type": "application/json",
            "Authorization": token
        });

        if(!response.ok) {
            const error = new Error(`Could not remove ${payload.type}!`);
            throw error;
        }
        else
        {
            if(payload.type === 'reference')
            {
                context.commit('removeReference', payload.uid);
            }
            else if(payload.type === 'identification')
            {
                context.commit('removeIdentification', payload.uid);
            }
            else
            {
                context.commit('removeComponent', payload.uid);
            }
        }
    },

    async loadComponents(context, payload) {
        const token = context.rootGetters["auth/getToken"] || sessionStorage.getItem('auth-token');
        
        if (!token) {
            logger.error('No authentication token available');
            const error = new Error('Authentication required');
            throw error;
        }
        
        const { response, responseData } = await api.get(`/${payload.type}`, {
            "content-type": "application/json",
            "Authorization": token,
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        });

        if(!response.ok)
        {
            logger.error('loadComponents API error', { status: response.status, type: payload.type, responseData });
            const error = new Error(responseData.detail || `Failed to fetch the ${payload.type}s! Status: ${response.status}`);
            throw error;
        }
        else
        {
            const components = [];

            for(const key in responseData)
            {
                const component = {
                    uid: responseData[key].uid,
                    name: responseData[key].name
                };

                components.push(component);
            }

            if(payload.type === 'reference')
            {
                context.commit('setReferences', components);
            }
            else if(payload.type === 'identification')
            {
                context.commit('setIdentifications', components);
            }
            else
            {
                context.commit('setComponents', components);
            }
        }
    },

    setComponents(context, payload) {
        context.commit('setComponents', payload);
    },

    async loadComponent(context, payload) {
        const token = context.rootGetters["auth/getToken"] || sessionStorage.getItem('auth-token');
        
        const { response, responseData } = await api.get(`/${payload.type}/${payload.uid}`, {
            "content-type": "application/json",
            "Authorization": token
        });

        if(!response.ok)
        {
            const error = new Error(responseData.detail || `Failed to fetch the ${payload.type}!`);
            throw error;
        }
        else
        {
            context.commit('setCurrentComponent', responseData);
        }
    },

    setCurrentComponent(context, payload){
        context.commit('setCurrentComponent', payload);
    },

    async updateComponent(context, payload) {
        const type = payload.type;
        const component = payload.data;

        const token = context.rootGetters["auth/getToken"] || sessionStorage.getItem('auth-token');

        const { response } = await api.update(`/${type}/${component.uid}`, component, {
            "content-type": "application/json",
            "Authorization": token
        });

        if(!response.ok)
        {
            const error = new Error(`Failed to update the ${type}!`);
            throw error;
        }
        else
        {
            if(payload.type === 'reference')
            {
                context.commit('updateReference', component);
            }
            else if(payload.type === 'identification')
            {
                context.commit('updateIdentification', component);
            }
            else
            {
                context.commit('updateComponent', component);
            }
        }
    },

    async addReference(context, payload) {
        let component = {
            uid: uuidv4(),
            name: payload.name,
            imageSourceUid: '',
            algorithmUid: '',
            algorithmType: ''
        };

        const token = context.rootGetters["auth/getToken"] || sessionStorage.getItem('auth-token');

        const { response } = await api.post(`/${payload.type}`, component, {
            "content-type": "application/json",
            "Authorization": token
        });

        if(!response.ok) 
        {
            const error = new Error(`Could not create ${payload.type}!`);
            throw error;
        }
        else
        {
            context.commit('addReference', component);
        }
    },


    async addIdentification(context, payload) {
        let component = {
            uid: uuidv4(),
            name: payload.name,
            imageSourceUid: '',
            algorithmUid: '',
            algorithmType: '',
            referenceUid: ''
        };

        const token = context.rootGetters["auth/getToken"] || sessionStorage.getItem('auth-token');

        const { response } = await api.post(`/${payload.type}`, component, {
            "content-type": "application/json",
            "Authorization": token
        });

        if(!response.ok) 
        {
            const error = new Error(`Could not create ${payload.type}!`);
            throw error;
        }
        else
        {
            context.commit('addIdentification', component);
        }
    },

    setReferences(context, payload) {
        context.commit('setReferences', payload);
    },

    setIdentifications(context, payload) {
        context.commit('setIdentifications', payload);
    },
}