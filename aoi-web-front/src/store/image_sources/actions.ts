import { ipAddress, port } from "../../url";
import { uuid } from "vue3-uuid";
import { get, post, update, remove, upload_image } from "../../utils/requests";


export default {
    async loadImageSources(context) {
        const token = context.rootGetters["auth/getToken"];
        const { response, responseData } = await get(`http://${ipAddress}:${port}/image_source`, {
            'content-type': 'application/json',
            'Authorization': token,
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        }); 

        if(!response.ok)
        {
            const error = new Error(responseData.detail || "Failed to fetch the image sources!");
            throw error;
        }
        else
        {
            const imageSources = [];

            for(const imageSourceData of responseData.message)
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
        console.log('Store loadCurrentImageSource called with payload:', payload);
        const { response, responseData } = await get(`http://${ipAddress}:${port}/image_source/${payload.uid}`);
        console.log('API response:', response.status, responseData);

        if(!response.ok)
        {
            const error = new Error(responseData.detail || `Failed to fetch the image source with id: ${payload.isid}!`);
            throw error;
        }
        else
        {
            console.log('Setting current image source:', responseData);
            context.commit('setCurrentImageSource', responseData.message);
            if(responseData.message.image_source_type === 'static' && responseData.message.image_generator_uid != ""){
                const gen = context.getters.getImageGeneratorById(responseData.message.image_generator_uid);
                context.commit('setCurrentImageGenerator', gen);
            }
        }
    },

    async addImageSource(context,payload){
        const newSource = {
            name: payload.name,
            image_source_type: payload.type,
            uid: uuid.v4(),
            camera_settings_uid: '',
            camera_uid: '',
            image_generator_uid: '',
            location_name: '',
            fps: 30,
            settle_time: 0.0,
            activate_location: false
        };

        const token = context.rootGetters["auth/getToken"];

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
        const token = context.rootGetters["auth/getToken"];

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
        const token = context.rootGetters["auth/getToken"];

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
            uid: uuid.v4(),
            dir_path: ""
        }

        const token = context.rootGetters["auth/getToken"];

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
        const token = context.rootGetters["auth/getToken"];

        const response = await upload_image (`http://${ipAddress}:${port}/image_generator/upload_image_generator`, payload);

        if(!response.ok) 
        {
            const error = new Error(`Could not upload images!`);
            throw error;
        }
    },

    async getAllImageGenerators(context){
        const token = context.rootGetters["auth/getToken"];
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