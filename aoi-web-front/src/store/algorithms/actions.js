import { uuid } from "vue3-uuid";
import { get, post, update, remove, postStream } from '../../utils/requests.js';
import { ipAddress, port } from "../../url.js";
import { GraphicsRect } from "../../utils/fabric_objects.js";

export default {
    async loadAlgorithms(context) {
        const { response, responseData } = await get(`http://${ipAddress}:${port}/algorithm/types`);

        if(!response.ok) 
        {
            const error = new Error(responseData.detail || "Failed to fetch the algorithms!");
            throw error;
        }
        else
        {
            const algorithms = []

            for (const key in responseData)
            {
                const algorithm = {
                    uid: uuid.v4(),
                    type: responseData[key]
                };

                algorithms.push(algorithm);
            }

            context.commit('setAlgorithms', algorithms);
        }
    },

    async loadBasicAlgorithms(context) {
        const { response, responseData } = await get(`http://${ipAddress}:${port}/algorithm/basic/types`);

        if(!response.ok) 
        {
            const error = new Error(responseData.detail || "Failed to fetch basic algorithms!");
            throw error;
        }
        else
        {
            context.commit('setBasicAlgorithms', responseData);
        }
    },

    async loadReferenceAlgorithms(context) {
        const { response, responseData } = await get(`http://${ipAddress}:${port}/algorithm/reference/types`);

        if(!response.ok) 
        {
            const error = new Error(responseData.detail || "Failed to fetch reference algorithms!");
            throw error;
        }
        else
        {
            const algorithms = []

            for (const key in responseData)
            {
                const algorithm = {
                    uid: uuid.v4(),
                    type: responseData[key]
                };

                algorithms.push(algorithm);
            }

            context.commit('setReferenceAlgorithms', algorithms);
        }
    },

    async loadConfiguredAlgorithms(context) {
        const token = context.rootGetters["auth/getToken"];

        const { response, responseData } = await get(`http://${ipAddress}:${port}/algorithm`, {
            'content-type': 'application/json',
            'Authorization': token
        });

        if(!response.ok) 
        {
            const error = new Error(responseData.detail || "Failed to fetch configured algorithms!");
            throw error;
        }
        else
        {
            const algorithms = []

            for (const key in responseData)
            {
                const algorithm = {
                    uid: responseData[key].uid,
                    type: responseData[key].type
                };

                algorithms.push(algorithm);
            }

            context.commit('setConfiguredAlgorithms', algorithms);
        }
    },

    async loadCurrentAlgorithm(context, payload) {
        const { response, responseData } = await get(`http://${ipAddress}:${port}/algorithm/${payload.uid}`);

        if(!response.ok)
        {
            const error = new Error(responseData.detail || "Failed to fetch selected algorithm!");
            throw error;
        }
        else
        {
            context.commit('setCurrentAlgorithm', responseData);

            let graphicItems = [];
            const graphics = responseData.parameters.graphics;

            for(const graphic of graphics)
            {
                const rect = new GraphicsRect({
                    left: graphic.rect[0],
                    top: graphic.rect[1],
                    fill: graphic.color,
                    width: graphic.rect[2],
                    height: graphic.rect[3],
                    objectCaching: false,
                    masks: graphic.masks,
                    masksColors: graphic.masksColors
                });

                rect.rotate(graphic.rotation);

                graphicItems.push(rect);
            }

            context.dispatch('graphics/setGraphicItems', {
                items: graphicItems
            }, { root: true });

            context.commit('deleteGraphicsFromAlgorithmAttributes');
        }
    },

    async loadCurrentReferenceAlgorithm(context, payload) {
        const { response, responseData } = await get(`http://${ipAddress}:${port}/algorithm/${payload.uid}`);

        if(!response.ok)
        {
            const error = new Error(responseData.detail || "Failed to fetch selected reference algorithm!");
            throw error;
        }
        else
        {
            context.commit('setCurrentReferenceAlgorithm', responseData);

            let graphicItems = [];
            const graphics = responseData.parameters.graphics;

            for(const graphic of graphics)
            {
                const rect = new GraphicsRect({
                    left: graphic.rect[0],
                    top: graphic.rect[1],
                    fill: graphic.color,
                    width: graphic.rect[2],
                    height: graphic.rect[3],
                    objectCaching: false
                });

                rect.rotate(graphic.rotation);

                graphicItems.push(rect);
            }

            context.dispatch('graphics/setReferenceGraphicItems', {
                items: graphicItems
            }, { root: true });

            context.commit('deleteGraphicsFromReferenceAlgorithmAttributes');
        }
    },

    async loadAlgorithm(context, payload) {
        const { response, responseData } = await get(`http://${ipAddress}:${port}/algorithm/types/${payload.type}`);

        if(!response.ok)
        {
            const error = new Error(responseData.detail || "Failed to fetch algorithm attributes!");
            throw error;
        }
        else
        {
            context.commit('setCurrentAlgorithmAttributes', responseData.parameters);
        }
    },

    async loadReferenceAlgorithm(context, payload) {
        const { response, responseData } = await get(`http://${ipAddress}:${port}/algorithm/reference/types/${payload.type}`);

        if(!response.ok)
        {
            const error = new Error(responseData.detail || "Failed to fetch reference algorithm attributes!");
            throw error;
        }
        else
        {
            context.commit('setCurrentReferenceAlgorithmAttributes', responseData.parameters);
        }
    },

    setAlgorithmResult(context, payload) {
        context.commit('setAlgorithmResult', payload);
    },

    loadCurrentAlgorithmFromParameters(context, payload) {
        const parameters = {}

        for(const key in payload.attributes)
        {
            if(payload.attributes[key].type === "fileloader")
                continue;

            parameters[payload.attributes[key].name] = payload.attributes[key].default;

            if(payload.attributes[key].type === "graphics")
            {
                const graphics = payload.attributes[key].default;

                let graphicItems = [];
        
                for(const graphic of graphics)
                {
                    const rect = new GraphicsRect({
                        left: graphic.rect[0],
                        top: graphic.rect[1],
                        fill: graphic.color,
                        width: graphic.rect[2],
                        height: graphic.rect[3],
                        objectCaching: false
                    });

                    rect.rotate(graphic.rotation);

                    graphicItems.push(rect);
                }

                context.dispatch('graphics/setGraphicItems', {
                    items: graphicItems
                }, { root: true });

                context.commit('deleteKeyFromAlgorithmAttributes', {
                    key: key
                });
            }
        }

        parameters['golden_position'] = [];

        const algorithm = {
            uid: uuid.v4(),
            type: payload.type,
            name: '',
            parameters: parameters
        }

        context.commit('setCurrentAlgorithm', algorithm);
    },

    loadCurrentReferenceAlgorithmFromParameters(context, payload) {
        const parameters = {}

        for(const key in payload.attributes)
        {
            if(payload.attributes[key].type === "fileloader")
                continue;
                
            parameters[payload.attributes[key].name] = payload.attributes[key].default;

            if(payload.attributes[key].type === "graphics")
            {
                const graphics = payload.attributes[key].default;

                let graphicItems = [];
        
                for(const graphic of graphics)
                {
                    const rect = new GraphicsRect({
                        left: graphic.rect[0],
                        top: graphic.rect[1],
                        fill: graphic.color,
                        width: graphic.rect[2],
                        height: graphic.rect[3],
                        objectCaching: false
                    });

                    rect.rotate(graphic.rotation);

                    graphicItems.push(rect);
                }

                context.dispatch('graphics/setReferenceGraphicItems', {
                    items: graphicItems
                }, { root: true });

                context.commit('deleteKeyFromReferenceAlgorithmAttributes', {
                    key: key
                });
            }
        }

        parameters['golden_position'] = [];

        const algorithm = {
            uid: uuid.v4(),
            type: payload.type,
            name: '',
            parameters: parameters
        }

        context.commit('setCurrentReferenceAlgorithm', algorithm);
    },

    setCurrentAlgorithm(context, payload) {
        context.commit('setCurrentAlgorithm', payload);
    },

    setCurrentReferenceAlgorithm(context, payload) {
        context.commit('setCurrentReferenceAlgorithm', payload);
    },

    setCurrentAlgorithmAttributes(context, payload) {
        context.commit('setCurrentAlgorithmAttributes', payload);
    },

    setCurrentReferenceAlgorithmAttributes(context, payload) {
        context.commit('setCurrentReferenceAlgorithmAttributes', payload);
    },

    async removeAlgorithm(context, payload) {
        const token = context.rootGetters["auth/getToken"];

        const response = await remove(`http://${ipAddress}:${port}/algorithm/${payload.uid}`, {
            'content-type': 'application/json',
            'Authorization': token
        });

        if(!response.ok)
        {
            const error = new Error("Failed to delete the algorithm!");
            throw error;
        }
        else
        {
            context.commit('removeAlgorithm', payload);
        }
    },

    async addAlgorithm(context, payload) {
        const token = context.rootGetters["auth/getToken"];

        const response = await post(`http://${ipAddress}:${port}/algorithm`, payload, {
            'content-type': 'application/json',
            'Authorization': token
        });

        if(!response.ok)
        {
            const error = new Error("Failed to add the algorithm!");
            throw error;
        }
        else
        {
            context.commit('addAlgorithm', payload);
        }
    },

    async updateConfiguredAlgorithm(context, payload) {
        const token = context.rootGetters["auth/getToken"];

        const response = await update(`http://${ipAddress}:${port}/algorithm/${payload.uid}`, payload, {
            'content-type': 'application/json',
            'Authorization': token
        });

        if(!response.ok)
        {
            const error = new Error("Failed to update the algorithm!");
            throw error;
        }
    },

    async addConfiguredAlgorithm(context, payload) {
        const token = context.rootGetters["auth/getToken"];

        const response = await post(`http://${ipAddress}:${port}/algorithm`, payload, {
            'content-type': 'application/json',
            'Authorization': token
        });

        if(!response.ok)
        {
            const error = new Error("Failed to update the algorithm!");
            throw error;
        }
        else
        {
            context.commit('addConfiguredAlgorithm', payload);
        }
    },

    updateCurrentAlgorithmGraphics(context, payload) {
        context.commit('updateCurrentAlgorithmGraphics', payload);
    },

    updateCurrentReferenceAlgorithmGraphics(context, payload) {
        context.commit('updateCurrentReferenceAlgorithmGraphics', payload);
    },

    async updateCurrentAlgorithmProperty(context, payload) {
        const response = await post(`http://${ipAddress}:${port}/algorithm/__API__/edit_live_algorithm`, {
            key: payload.name,
            value: payload.value
        });

        if(!response.ok)
        {
            const error = new Error("Failed to edit live algorithm graphics!");
            throw error;
        }
        else
        {
            context.commit('updateCurrentAlgorithmProperty', payload);
        }
    },

    async updateCurrentReferenceAlgorithmProperty(context, payload) {
        const response = await post(`http://${ipAddress}:${port}/algorithm/__API__/edit_reference_algorithm`, {
            key: payload.name,
            value: payload.value
        });

        if(!response.ok)
        {
            const error = new Error("Failed to edit live algorithm graphics!");
            throw error;
        }
        else
        {
            context.commit('updateCurrentReferenceAlgorithmProperty', payload);
        }
    },

    async uploadResource(_, payload) {
        const response = await postStream(`http://${ipAddress}:${port}/algorithm/__API__/upload_resource`,
            payload, {}
        );

        if(!response.ok)
        {
            const error = new Error("Failed to load resource!");
            throw error;
        }
    },

    async setLiveAlgorithm(_, payload) {
        const { response, _2 } = await get(`http://${ipAddress}:${port}/algorithm/__API__/set_live_algorithm/${payload.type}`);

        if(!response.ok)
        {
            const error = new Error("Failed to update live algorithm!");
            throw error;
        }
    },

    async setReferenceAlgorithm(_, payload) {
        const { response, _2 } = await get(`http://${ipAddress}:${port}/algorithm/__API__/set_reference_algorithm/${payload.type}`);

        if(!response.ok)
        {
            const error = new Error("Failed to update reference algorithm!");
            throw error;
        }
    },

    async setLiveAlgorithmReferenceRepository(_, payload) {
        const { response, _3 } = await get(`http://${ipAddress}:${port}/algorithm/__API__/set_live_algorithm_reference/${payload.id}`);

        if(!response.ok)
        {
            const error = new Error("Failed to update live algorithm reference!");
            throw error;
        }
    },

    async setLiveAlgorithmReferenceFromDict(_, payload) {
        const response = await post(`http://${ipAddress}:${port}/algorithm/__API__/set_live_algorithm_reference_dict`, payload);

        if(!response.ok)
        {
            const error = new Error("Failed to update live algorithm reference!");
            throw error;
        }
    },

    async setLiveAlgorithmReference() {
        const {response, _} = await get(`http://${ipAddress}:${port}/algorithm/__API__/set_live_algorithm_reference`);

        if(!response.ok)
        {
            const error = new Error("Failed to update live algorithm reference!");
            throw error;
        }
    },

    async resetLiveAlgorithmReference() {
        const {response, _} = await get(`http://${ipAddress}:${port}/algorithm/__API__/reset_live_algorithm_reference`);

        if(!response.ok)
        {
            const error = new Error("Failed to reset live algorithm reference!");
            throw error;
        }
    },

    async setLiveAlgorithmAttributes(context, payload) {
        const algorithmAttributes = context.getters.getCurrentAlgorithmAttributes;
        const currentAlgorithm = context.getters.getCurrentAlgorithm;

        for(const key in algorithmAttributes)
        {
            const data = {
                "key": algorithmAttributes[key].name,
                "value": currentAlgorithm.parameters[algorithmAttributes[key].name]
            };

            const response = await post(`http://${ipAddress}:${port}/algorithm/__API__/edit_live_algorithm`, data);

            if(!response.ok)
            {
                const error = new Error("Failed to edit live algorithm!");
                throw error;
            }
        }

        const data = {
            "key": "graphics",
            "value": payload
        }

        const response = await post(`http://${ipAddress}:${port}/algorithm/__API__/edit_live_algorithm`, data);

        if(!response.ok)
        {
            const error = new Error("Failed to edit live algorithm graphics!");
            throw error;
        }
    },

    updateCurrentAlgorithmAttributes(context, payload) {
        context.commit("updateCurrentAlgorithmAttributes", payload);
    },

    async setLiveReferenceAlgorithmAttributes(context, payload) {
        const algorithmAttributes = context.getters.getCurrentReferenceAlgorithmAttributes;
        const currentAlgorithm = context.getters.getCurrentReferenceAlgorithm;

        for(const key in algorithmAttributes)
        {
            const data = {
                "key": algorithmAttributes[key].name,
                "value": currentAlgorithm.parameters[algorithmAttributes[key].name]
            };

            const response = await post(`http://${ipAddress}:${port}/algorithm/__API__/edit_live_algorithm`, data);

            if(!response.ok)
            {
                const error = new Error("Failed to edit live algorithm!");
                throw error;
            }
        }

        const data = {
            "key": "graphics",
            "value": payload
        }

        const response = await post(`http://${ipAddress}:${port}/algorithm/__API__/edit_live_algorithm`, data);

        if(!response.ok)
        {
            const error = new Error("Failed to edit live algorithm graphics!");
            throw error;
        }
    },

    updateCurrentReferenceAlgorithmAttributes(context, payload) {
        context.commit("updateCurrentReferenceAlgorithmAttributes", payload);
    },

    loadCurrentAlgorithmFromObject(context, payload) {
        const currentAlgorithm = context.getters.getCurrentAlgorithm;

        for(const key in payload)
        {
            if(currentAlgorithm.parameters[key])
            {
                context.dispatch("updateCurrentAlgorithmProperty", {
                    name: key,
                    value: payload[key]
                });
            }

            if(key === "graphics")
            {
                const graphics = payload[key];

                let graphicItems = [];
        
                for(const graphic of graphics)
                {
                    const rect = new GraphicsRect({
                        left: graphic.rect[0],
                        top: graphic.rect[1],
                        fill: graphic.color,
                        width: graphic.rect[2],
                        height: graphic.rect[3],
                        objectCaching: false
                    });

                    rect.rotate(graphic.rotation);

                    graphicItems.push(rect);
                }

                context.dispatch('graphics/setGraphicItems', {
                    items: graphicItems
                }, { root: true });
            }
        }
    },

    loadCurrentReferenceAlgorithmFromObject(context, payload) {
        const currentAlgorithm = context.getters.getCurrentReferenceAlgorithm;

        for(const key in payload)
        {
            if(currentAlgorithm.parameters[key])
            {
                context.dispatch("updateCurrentAlgorithmProperty", {
                    name: key,
                    value: payload[key]
                });
            }
        }
    },

    async setBasicLiveAlgorithm(_, payload) {
        const response = await post(`http://${ipAddress}:${port}/algorithm/__API__/basic/set_live_algorithm`, payload);

        if(!response.ok)
        {
            const error = new Error("Failed to edit live algorithm graphics!", response.status);
            throw error;
        }
    },

    async loadSelectedBasicAlgorithmsAttributes(context, payload) {
        for(const type of payload.types)
        {
            const { response, responseData } = await get(`http://${ipAddress}:${port}/algorithm/basic/types/${type}`);

            if(!response.ok)
            {
                const error = new Error(responseData.detail || "Failed to fetch the algorithm!");
                throw error;
            }
            else
            {
                context.commit('addBasicAlgorithmAttributes', responseData.parameters);
            }
        }
    },

    loadCurrentBasicAlgorithmsFromAttributes(context, _) {
        const basicAlgorithmsAttributes = context.getters.getBasicAlgorithmsAttributes;

        for(const [idx, algAttributes] of basicAlgorithmsAttributes.entries())
        {
            const parameters = {};
            let graphicItems = [];

            for(const key in algAttributes)
            {
                if(algAttributes[key].name === 'graphics')
                {
                    const graphics = algAttributes[key].default;
                    for(const graphic of graphics)
                    {
                        const rect = new fabric.Rect({
                            left: graphic.rect[0],
                            top: graphic.rect[1],
                            fill: 'rgba(255, 165, 0, 0.5)',
                            width: graphic.rect[2],
                            height: graphic.rect[3],
                            objectCaching: false,
                            stroke: 'rgba(255, 165, 0, 1.0)',
                            strokeWidth: 0
                        });
            
                        rect.rotate(graphic.rotation);
            
                        graphicItems.push(rect);
                    }

                    context.commit("deleteGraphicsFromBasicAlgorithmAttributes", {
                        idx: idx
                    });
                }
                else
                {
                    parameters[algAttributes[key].name] = algAttributes[key].default;
                }
            }

            context.commit("graphics/addGraphicsToCompoundItems", graphicItems, {
                root: true
            });
            context.commit("addCurrentBasicAlgorithm", parameters);
        }
    },

    async updateCurrentBasicAlgorithmProperty(context, payload) {
        const response = await post(`http://${ipAddress}:${port}/algorithm/__API__/basic/edit_live_algorithm_field`, payload);

        if(!response.ok)
        {
            const error = new Error("Failed to edit live algorithm graphics!");
            throw error;
        }
        else
        {
            context.commit('updateCurrentBasicAlgorithmProperty', payload);
        }
    },

    updateCurrentBasicAlgorithmPropertyLocal(context, payload) {
        context.commit('updateCurrentBasicAlgorithmProperty', payload);
    },

    async updateCurrentBasicAlgorithmFromConfig(_, payload) {
        const {response, _2} = await get(`http://${ipAddress}:${port}/algorithm/__API__/basic/edit_live_algorithm/${payload}`);

        if(!response.ok)
        {
            const error = new Error("Failed to load algorithm from configuration!", response.status);
            throw error;
        }
    },

    async updateCurrentBasicAlgorithmFromDict(_, payload) {
        const response = await post(`http://${ipAddress}:${port}/algorithm/__API__/basic/edit_live_algorithm`, payload);

        if(!response.ok)
        {
            const error = new Error("Failed to load algorithm from configuration!", response.status);
            throw error;
        }
    },

    loadCurrentBasicAlgorithmFromConfig(context, payload) {
        for(const [idx, parameters] of payload.entries())
        {
            let graphicItems = [];

            if(parameters.graphics)
            {
                for(const graphic of parameters.graphics)
                {
                    const rect = new fabric.Rect({
                        left: graphic.rect[0],
                        top: graphic.rect[1],
                        fill: 'rgba(255, 165, 0, 0.5)',
                        width: graphic.rect[2],
                        height: graphic.rect[3],
                        objectCaching: false,
                        stroke: 'rgba(255, 165, 0, 1.0)',
                        strokeWidth: 0
                    });
        
                    rect.rotate(graphic.rotation);
        
                    graphicItems.push(rect);
                }

                context.commit("deleteGraphicsFromBasicAlgorithmAttributes", {
                    idx: idx
                });
            }

            context.commit('graphics/addGraphicsToCompoundItems', graphicItems, {
                root: true
            });
            context.commit("addCurrentBasicAlgorithm", parameters);
        }
    },

    updateCurrentBasicAlgorithmAttributes(context, payload) {
        context.commit('updateCurrentBasicAlgorithmAttributes', payload);
    },

    resetBasicAlgorithmsAttributes(context, _) {
        context.commit("resetBasicAlgorithmsAttributes");
    },

    resetCurrentBasicAlgorithms(context, _) {
        context.commit("resetCurrentBasicAlgorithms");
    },

    async singleProcessAlgorithm(context, payload) {
        const { response, responseData } = await get(payload.url);

        if(!response.ok)
        {
            let result = {
                frame: ''
            };

            context.dispatch('setAlgorithmResult', result);

            const error = new Error(responseData.detail || `Failed to process algorithm!`);
            throw error;
        }
        else
        {
            if(payload.type === "custom_component")
            {
                context.dispatch('setAlgorithmResult', {
                    frame: 'data:image/png;base64,' + responseData.frame,
                    results: responseData.results,
                    data: responseData.data
                });
            }
            else
            {
                let outputImages = [];
                for(const frame of responseData.frame)
                {
                    outputImages.push('data:image/png;base64,' + frame);
                }
                responseData.frame = outputImages;
                context.dispatch('setAlgorithmResult', responseData);
            }
        }
    },

    async singleProcessAlgorithmCamera(context, payload) {
        let url = null;
        if(payload.type === "custom_component")
        {
            url = `http://${ipAddress}:${port}/algorithm/__API__/basic/process_live_algorithm/${payload.uid}`;
        }
        else
        {
            url = `http://${ipAddress}:${port}/algorithm/__API__/process_live_algorithm/${payload.uid}`;
        }

        await context.dispatch('singleProcessAlgorithm', {
            url: url,
            type: payload.type
        });
    },

    async singleProcessAlgorithmStatic(context, payload) {
        let url = `http://${ipAddress}:${port}/algorithm/__API__/process_live_algorithm`;
        await context.dispatch('singleProcessAlgorithm', {
            url: url,
            type: payload.type
        });
    },

    async singleProcessReference(context, payload) {
        const { response, responseData } = await get(payload.url);

        if(!response.ok)
        {
            const error = new Error(responseData.detail || `Failed to process the ${payload.type}!`);
            throw error;
        }
        else
        {
            let outputImages = [];
            for(const frame of responseData.frame)
            {
                outputImages.push('data:image/png;base64,' + frame);
            }
            responseData.frame = outputImages;
            context.dispatch('setAlgorithmResult', responseData);
        }
    },

    async singleProcessReferenceCamera(context, payload) {
        let url = `http://${ipAddress}:${port}/algorithm/__API__/process_reference_algorithm/${payload.uid}`;
        
        await context.dispatch('singleProcessAlgorithm', {
            url: url,
            type: payload.type
        });
    },

    async singleProcessReferenceStatic(context, payload) {
        let url = `http://${ipAddress}:${port}/algorithm/__API__/process_reference_algorithm`;
        await context.dispatch('singleProcessAlgorithm', {
            url: url,
            type: payload.type
        });
    },

    async setStaticImage(_, payload) {
        const response = await post(`http://${ipAddress}:${port}/algorithm/__API__/set_static_image`, payload);

        if(!response.ok)
        {
            const error = new Error(`Failed to process the ${payload.type}!`);
            throw error;
        }
    }
}