import { ipAddress, port } from "../../url";
import { v4 as uuidv4 } from "uuid";
import { get, post, update, remove, upload_image } from "../../utils/requests";
import { logger } from "../../utils/logger";


export default {
    async loadImageSources(context) {
        const token = context.rootGetters["auth/getToken"] || sessionStorage.getItem('auth-token');
        // Use longer timeout for image sources loading to prevent timeout errors
        const { response, responseData } = await get(`http://${ipAddress}:${port}/image_source`, {
            'content-type': 'application/json',
            'Authorization': token,
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        }, 15000); // 15 second timeout instead of default 10 seconds 

        if(!response.ok)
        {
            const error = new Error(responseData.detail || "Failed to fetch the image sources!");
            throw error;
        }
        else
        {
            const imageSources = [];

            // Handle both wrapped ({message: []}) and direct array responses
            const sourceData = responseData.message || responseData;

            for(const imageSourceData of sourceData)
            {
                const imageSource = {
                    uid: imageSourceData.uid,
                    name: imageSourceData.name
                };

                imageSources.push(imageSource);
            }

            context.commit('setImageSources', imageSources);
        }
    },

    async loadCurrentImageSource(context, payload) {
        logger.debug('Store loadCurrentImageSource called', { payload });
        const { response, responseData } = await get(`http://${ipAddress}:${port}/image_source/${payload.uid}`);
        logger.debug('API response received', { status: response.status, responseData });

        if(!response.ok)
        {
            const error = new Error(responseData.detail || `Failed to fetch the image source with id: ${payload.isid}!`);
            throw error;
        }
        else
        {
            logger.debug('Setting current image source', { responseData });
            // Handle both wrapped ({message: data}) and direct object responses
            const sourceData = responseData.message || responseData;
            
            context.commit('setCurrentImageSource', sourceData);
            if(sourceData.image_source_type === 'static' && sourceData.image_generator_uid != ""){
                const gen = context.getters.getImageGeneratorById(sourceData.image_generator_uid);
                context.commit('setCurrentImageGenerator', gen);
            }
        }
    },

    async addImageSource(context,payload){
        const newSource = {
            name: payload.name,
            image_source_type: payload.type,
            uid: uuidv4(),
            camera_settings_uid: '',
            camera_uid: '',
            image_generator_uid: '',
            location_name: '',
            fps: 30,
            settle_time: 0.0,
            activate_location: false
        };

        const token = context.rootGetters["auth/getToken"] || sessionStorage.getItem('auth-token');

        const { response, responseData } = await post(`http://${ipAddress}:${port}/image_source`, newSource, {
            "content-type": "application/json",
            "Authorization": token
        });

        if(!response.ok) 
        {
            const error = new Error(responseData.detail || `Could not create ${newSource.image_source_type}!`);
            throw error;
        }
        else
        {
            context.commit('addImageSource', newSource);
        }
    },

    setCurrentImageSource(context, payload) {
        context.commit("setCurrentImageSource", payload);
    },

    setCurrentImageSourceProp(context, payload) {
        context.commit("setCurrentImageSourceProp", payload);
    },

    async removeImageSource(context,payload){
        const token = context.rootGetters["auth/getToken"] || sessionStorage.getItem('auth-token');

        const { response, responseData } = await remove(`http://${ipAddress}:${port}/image_source/${payload.uid}`, {
            "content-type": "application/json",
            "Authorization": token
        });

        if(!response.ok) 
        {
            const error = new Error(responseData.detail || `Could not remove image source with ID ${payload.uid}!`);
            throw error;
        }
        else
        {
            context.commit('removeImageSource', payload);
        }
    },

    async updateImageSource(context,payload){
        const token = context.rootGetters["auth/getToken"] || sessionStorage.getItem('auth-token');

        const { response, responseData } = await update(`http://${ipAddress}:${port}/image_source/${payload.uid}`, payload, {
            "content-type": "application/json",
            "Authorization": token
        });
        
        if(!response.ok) 
        {
            const error = new Error(responseData.detail || `Could not update ${payload.name}!`);
            throw error;
        }
        else
        {
            context.commit('updateImageSource', payload);
            if(payload.image_source_type === 'static' && payload.image_generator_uid != ""){
                const gen = context.getters.getImageGeneratorById(payload.image_generator_uid);
                context.commit('setCurrentImageGenerator', gen);
            }
        }
    },

    async addImageGenerator(context){

        const newGenerator = {
            uid: uuidv4(),
            dir_path: ""
        }

        const token = context.rootGetters["auth/getToken"] || sessionStorage.getItem('auth-token');

        const { response, responseData } = await post(`http://${ipAddress}:${port}/image_generator`, newGenerator, {
            "content-type": "application/json",
            "Authorization": token
        });
    
        if(!response.ok) 
        {
            const error = new Error(responseData.detail || `Could not create image generator!`);
            throw error;
        }
        else
        {
            context.commit('addImageGenerator', newGenerator);
            
            const gen = context.getters.getImageGeneratorById(newGenerator.uid);
            context.commit('setCurrentImageGenerator', gen);
        }
    },

    async uploadImagesFromGenerator(context, payload){
        const token = context.rootGetters["auth/getToken"] || sessionStorage.getItem('auth-token');

        const response = await upload_image (`http://${ipAddress}:${port}/image_generator/upload_image_generator`, payload);

        if(!response.ok) 
        {
            const error = new Error(`Could not upload images!`);
            throw error;
        }
    },

    async getAllImageGenerators(context){
        const token = context.rootGetters["auth/getToken"] || sessionStorage.getItem('auth-token');
        const { response, responseData } = await get(`http://${ipAddress}:${port}/image_generator`, {
            'content-type': 'application/json',
            'Authorization': token,
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        });
    
        if(!response.ok)
        {
            const error = new Error(responseData.detail || `Failed to fetch the image generators!`);
            throw error;
        }
        else
        {
            context.commit('setImageGenerators', responseData);
        }
    },

    setCurrentImageGenerator(context, payload) {
        context.commit('setCurrentImageGenerator', payload);
    },

    setCurrentImageGeneratorProp(context, payload) {
        context.commit('setCurrentImageGeneratorProp', payload);
    },

    async loadImageGeneratorAsCurrent(context, payload) {
        const { response, responseData } = await get(`http://${ipAddress}:${port}/image_generator/${payload.uid}`);

        if(!response.ok)
        {
            const error = new Error(responseData.detail || `Failed to fetch the image generator!`);
            throw error;
        }
        else
        {
            context.commit('setCurrentImageGenerator', responseData);
        }
    },

    async closeImageSourceSocket(_, payload) {
        const { response, responseData } = await post(`http://${ipAddress}:${port}/image_source/${payload.uid}/ws/close`);

        if(!response.ok)
        {
            const error = new Error(responseData.detail || `Failed to close socket for image source with ID ${payload.uid}!`);
            throw error;
        }
    }
}