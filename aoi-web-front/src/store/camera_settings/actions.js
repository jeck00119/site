
import { get, post, update, remove, patch } from '../../utils/requests.js';
import { uuid } from "vue3-uuid";
import { ipAddress, port } from "../../url.js";


export default {

    async addCamera(context, payload) {
        let camera = {
                uid: uuid.v4(),
                name: payload.name,
                opencv_index_id: payload.openCvIndexId,
                camera_type: payload.cameraType
            }

        const token = context.rootGetters["auth/getToken"];

        const response = await post(`http://${ipAddress}:${port}/cameras`, camera, {
            "content-type": "application/json",
            "Authorization": token
        });

        if(!response.ok) 
        {
            const error = new Error(`Could not create ${payload.cameraType}!`);
            throw error;
        }
        else
        {
            context.commit('addCamera', camera);
        }
    },

    async removeCamera(context, payload) {
        const token = context.rootGetters["auth/getToken"];

        const response = await remove(`http://${ipAddress}:${port}/cameras/${payload.uid}`, {
            "content-type": "application/json",
            "Authorization": token
        });

        if(!response.ok) 
        {
            const error = new Error(`Failed to remove camera with ID ${payload.uid}!`);
            throw error;
        }
        else
        {
            context.commit('removeCamera', payload);
        }
    },

    async fetchCamerasList(context) {
        const { response, responseData } = await get(`http://${ipAddress}:${port}/cameras`); 
        if(!response.ok)
        {
            const error = new Error(responseData.detail);
            throw error;
        }

        context.commit('setCamerasList', responseData);
    },

    async fetchCamera(context, payload) {
        const { response, responseData } = await get(`http://${ipAddress}:${port}/cameras/${payload}`);
        if(!response.ok)
        {
            const error = new Error(responseData.detail);
            throw error;
        }
        context.commit('setcurrentCamera', responseData['camera']);
        context.commit('setCameraControls', responseData['controls'])
        context.commit('setCurrentCameraConfig',responseData['default_settings']);
        context.commit('setCurrentCameraDefaultSettings', responseData['default_settings']);
    },

    async fetchCameraByUid(context, payloadUid) {
        const { response, responseData } = await get(`http://${ipAddress}:${port}/cameras/${payloadUid.value}`);
        if(!response.ok)
        {
            const error = new Error(responseData.detail);
            throw error;
        }
        context.commit('setcurrentCamera', responseData['camera']);
        context.commit('setCameraControls', responseData['controls']);
        context.commit('setCurrentCameraConfig',responseData['default_settings']);
        context.commit('setCurrentCameraDefaultSettings', responseData['default_settings']);
    },

    async fetchAllCameraSettings(context) { 
        const { response, responseData } = await get(`http://${ipAddress}:${port}/camera_settings`);
        context.commit('setCameraSettingsList', responseData);
    },

    async fetchCameraSettingsList(context, payload) {
        const { response, responseData } = await get(`http://${ipAddress}:${port}/cameras/${payload}/settings`);

        if(!response.ok)
        {
            const error = new Error(responseData.detail);
            throw error;
        }
        context.commit('setCameraSettingsList', responseData);
    },

    async fetchCameraSettings(context, payload)
    {
        const { response, responseData } = await get(`http://${ipAddress}:${port}/camera_settings/${payload}`);
        context.commit('setCurrentCameraConfig', responseData);
    },

    async loadCameraSettingsToCamera(_, payload)
    {   
        const { response, responseData } = await get(`http://${ipAddress}:${port}/cameras/${payload.cameraUid}/settings/${payload.cameraSettingUid}`);
    },

    async loadCameraSettingsFromObject(_, payload) {
        const response = await post(`http://${ipAddress}:${port}/cameras/${payload.cameraUid}/settings`, payload.settings);
    },

    async readCameraTypes(context)
    {
        const { response, responseData } = await get(`http://${ipAddress}:${port}/cameras/camera_types`);
        
        if(!response.ok)
        {
            const error = new Error(responseData.detail);
            throw error;
        }
        context.commit('setCameraTypesList', responseData);
        
    },

    async patchCameraSetting(context, payload)
    {
        context.commit("updateCurrentCameraSettings", {
            name: payload.name,
            value: payload.value
        })
        const { response, responseData } = await patch(`http://${ipAddress}:${port}/cameras/_API_/${payload.cameraUid}`, {
            name: payload.name,
            value: payload.value
        });
    },

    setCurrentCameraConfig(context, payload) {
        context.commit('setCurrentCameraConfig', payload);
    },

    setCurrentCameraConfigName(context, payload) {
        context.commit("setCurrentCameraConfigName", payload);
    },

    setCurrentCameraConfigCameraType(context, payload) {
        context.commit("setCurrentCameraConfigCameraType", payload);
    },

    async postCameraSettings(context, payload)
    {
        context.commit("updateCurrentCameraSettings", {"name":"name", "value": payload.name});
        context.commit("updateCurrentCameraSettings", {"name":"uid", "value": uuid.v4()});

        const token = context.rootGetters["auth/getToken"];

        const response = await post(`http://${ipAddress}:${port}/camera_settings`, payload, {
            'content-type': 'application/json',
            'Authorization': token
        });

        if(response.ok)
        {
            context.commit("addCameraSettingsList", payload);
        }
    },

    updateCameraSettingsListById(context, payload) {
        context.commit("updateCameraSettingsListById", payload);
    },

    async putCameraSettings(context, payload)
    {
        const token = context.rootGetters["auth/getToken"];

        const response = await update(`http://${ipAddress}:${port}/camera_settings/${payload.uid}`, payload, {
            'content-type': 'application/json',
            'Authorization': token
        });

        if(response.ok)
        {
            context.commit("updateCameraSettingsListById", payload);
        }
    },


    async removeCameraSettings(context, payload)
    {
        const token = context.rootGetters["auth/getToken"];

        const response = await remove(`http://${ipAddress}:${port}/camera_settings/${payload}`, {
            'content-type': 'application/json',
            'Authorization': token
        });

        if(response.ok)
        {
            context.commit("removeCameraSettings", payload);
        }
    }
}
 