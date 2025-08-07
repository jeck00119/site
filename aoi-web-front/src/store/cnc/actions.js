import { uuid } from "vue3-uuid";
import api from "../../utils/api.js";

export default {
    async loadPorts(context, _) {
        const { response, responseData } = await api.get('/cnc/check_ports');

        if(!response.ok)
        {
            const error = new Error(responseData.detail || `Failed to fetch the available ports!`);
            throw error;
        }
        else
        {
            context.commit('loadPorts', responseData);
        }
    },

    async loadCNCs(context, _) {
        const { response, responseData } = await api.get('/cnc');

        if(!response.ok)
        {
            const error = new Error(responseData.detail || `Failed to fetch CNCs!`);
            throw error;
        }
        else
        {
            context.commit('loadCNCs', responseData);
        }
    },

    async loadCNCTypes(context, _) {
        const { response, responseData } = await api.get('/cnc/cnc_types');

        if(!response.ok)
        {
            const error = new Error(responseData.detail || `Failed to fetch CNC types!`);
            throw error;
        }
        else
        {
            context.commit('loadCNCTypes', responseData);
        }
    },

    resetPorts(context, _) {
        context.commit('resetPorts');
    },

    resetCNCs(context, _) {
        context.commit('resetCNCs');
    },

    addCNC(context, payload) {
        const cnc = {
            uid: uuid.v4(),
            name: payload.name,
            type: payload.type,
            port: payload.port
        };

        context.commit('addCNC', cnc);
    },

    removeCNC(context, payload) {
        context.commit('removeCNC', payload);
    },

    async saveCNCs(context, _) {
        const cncs = context.getters.getCNCs;
        const token = context.rootGetters["auth/getToken"];

        try {
            const { response, data } = await api.post('/cnc/save', { cnc_list: cncs }, {
                "content-type": "application/json",
                "Authorization": token
            });

            if(!response.ok) {
                const errorMessage = data?.message || 'Failed to save CNCs - some CNCs may have connection issues';
                console.warn('CNC Save Warning:', errorMessage);
                // Don't throw error - allow operation to continue
                // The individual CNC connection errors will be handled via WebSocket callbacks
                return { success: false, message: errorMessage };
            }
            
            return { success: true };
        } catch (error) {
            console.error('CNC Save Error:', error);
            // Don't throw error - allow operation to continue gracefully
            return { success: false, message: error.message || 'Failed to save CNCs' };
        }
    },

    updateCNCPort(context, payload) {
        context.commit('updateCNCPort', payload);
    },

    updateCNCType(context, payload) {
        context.commit('updateCNCType', payload);
    },

    async fetchLocations(context, payload){
        const {response, responseData} = await api.get(`/location/axis/${payload}`);

        if (!response.ok)
        {
            const error = new Error(responseData.detail);
            throw error;
        }
        context.commit('locations',responseData);
    },

    async postLocation(context, payload){
        payload[0].uid = uuid.v4();
        const saveType = payload[1];

        switch(saveType){
            case 'x':
                payload[0].y = null
                payload[0].z = null
                break;
            case 'y':
                payload[0].x = null;
                payload[0].z = null
                break;
            case 'z':
                payload[0].x = null;
                payload[0].y = null
                break;
        }

        const token = context.rootGetters["auth/getToken"];

        const {response, responseData} = await api.post('/location', payload[0], {
            'content-type': 'application/json',
            'Authorization': token
        });
    },

    async loadLocations(context,_){
        const { response, responseData } = await api.get('/location');
        if(!response.ok)
        {
            const error = new Error(responseData.detail || `Failed to load Locations!`);
            throw error;
        }
        else
        {
            context.commit('locations', responseData);
        }
    },

    async patchLocation(context, payload){
        let patchedLocation = null
        for(const location of context.state.locations){
            if (location.uid == payload.locationUid){
                patchedLocation = location;
                break;
            }
        }
        const oldName = patchedLocation.name.slice();
        patchedLocation.name = payload.newName;
        try{
            const token = context.rootGetters["auth/getToken"];
            const { response, responseData } = await api.put('/location', patchedLocation, {
                "content-type": "application/json",
                "Authorization": token
            });
        } catch (error) {
            patchedLocation.name = oldName;
        }
    },

    async deleteLocation(context, payload){
        const token = context.rootGetters["auth/getToken"];
        const { response, responseData } = await api.delete(`/location/${payload}`, {
            "content-type": "application/json",
            "Authorization": token
        });
    },

    async api_moveToLocation(context, payload){
        try {
            const { response, responseData } = await api.get(`/cnc/${payload.cncUid}/__API__/${payload.location}/move_to_location?block=${payload.block}&timeout=${payload.timeout}`);
            if (!response.ok) {
                const error = new Error(responseData.detail || `Failed to move CNC ${payload.cncUid} to location ${payload.location}`);
                console.error('CNC Move to Location Error:', error.message);
                throw error;
            }
        } catch (error) {
            console.error('CNC Move to Location Exception:', error.message);
            throw error;
        }
    },

    async api_command(context, payload){
        try {
            const { response, responseData } = await api.get(`/cnc/${payload.cncUid}/__API__/${payload.command}`);
            if (!response.ok) {
                const error = new Error(responseData.detail || `Failed to execute command '${payload.command}' on CNC ${payload.cncUid}`);
                console.error('CNC Command Error:', error.message);
                throw error;
            }
        } catch (error) {
            console.error('CNC Command Exception:', error.message);
            throw error;
        }
    },

    async api_increaseAxis(context, payload){
        try {
            const { response, responseData } = await api.get(`/cnc/${payload.cncUid}/__API__/${payload.axis}/plus?feed_rate=${payload.feedrate}&step=${payload.step}`);
            if (!response.ok) {
                const error = new Error(responseData.detail || `Failed to move CNC ${payload.cncUid} axis ${payload.axis} plus by ${payload.step} steps`);
                console.error('CNC Axis Plus Error:', error.message);
                throw error;
            }
        } catch (error) {
            console.error('CNC Axis Plus Exception:', error.message);
            throw error;
        }
    },

    async api_decreaseAxis(context, payload){
        try {
            const { response, responseData } = await api.get(`/cnc/${payload.cncUid}/__API__/${payload.axis}/minus?feed_rate=${payload.feedrate}&step=${payload.step}`);
            if (!response.ok) {
                const error = new Error(responseData.detail || `Failed to move CNC ${payload.cncUid} axis ${payload.axis} minus by ${payload.step} steps`);
                console.error('CNC Axis Minus Error:', error.message);
                throw error;
            }
        } catch (error) {
            console.error('CNC Axis Minus Exception:', error.message);
            throw error;
        }
    },

    async api_terminal(context, payload){
        try {
            const {response, responseData} = await api.get(`/cnc/${payload.cncUid}/__API__/terminal?command=${payload.command}`);
            if (!response.ok) {
                const error = new Error(responseData.detail || `Failed to send terminal command '${payload.command}' to CNC ${payload.cncUid}`);
                console.error('CNC Terminal Error:', error.message);
                throw error;
            }
        } catch (error) {
            console.error('CNC Terminal Exception:', error.message);
            throw error;
        }
    },

    async initializeCNC(context, payload) {
        try {
            const { response, responseData } = await api.post(`/cnc/${payload.cncUid}/initialize`);
            if (!response.ok) {
                const error = new Error(responseData.detail || `Failed to initialize CNC ${payload.cncUid}`);
                console.error('CNC Initialize Error:', error.message);
                throw error;
            }
        } catch (error) {
            console.error('CNC Initialize Exception:', error.message);
            throw error;
        }
    },

    async deinitializeCNC(context, payload) {
        try {
            const { response, responseData } = await api.post(`/cnc/${payload.cncUid}/deinitialize`);
            if (!response.ok) {
                const error = new Error(responseData.detail || `Failed to deinitialize CNC ${payload.cncUid}`);
                console.error('CNC Deinitialize Error:', error.message);
                throw error;
            }
        } catch (error) {
            console.error('CNC Deinitialize Exception:', error.message);
            throw error;
        }
    },

    async closeStateSocket(_, payload) {
        try {
            const { response, responseData } = await api.post(`/cnc/${payload.uid}/ws/close`);
            if(!response.ok) {
                console.warn(`Socket for CNC ${payload.uid} may already be closed or doesn't exist:`, responseData?.detail || 'Unknown error');
            }
        } catch (error) {
            console.warn(`Error closing socket for CNC ${payload.uid}:`, error.message);
        }
    },

    async initializeAllCNCs(context, _) {
        const { response, responseData } = await api.post('/cnc/initialize_all');

        if(!response.ok)
        {
            const error = new Error(responseData.detail || `Failed to initialize CNCs!`);
            throw error;
        }
    },

    addPositionData(context, payload) {
        context.commit('addPositionData', payload);
    },

    updatePositionData(context, payload) {
        context.commit('setMPos', { uid: payload.uid, x: payload.mPos[0], y: payload.mPos[1], z: payload.mPos[2] });
        context.commit('setWPos', { uid: payload.uid, x: payload.wPos[0], y: payload.wPos[1], z: payload.wPos[2] });
        context.commit('setPos', { uid: payload.uid });
        if (payload.state) {
            context.commit('setCNCState', { uid: payload.uid, state: payload.state });
        }
    },

    setPos(context, payload) {
        context.commit('setPos', payload);
    },

    setWPos(context, payload) {
        context.commit('setWPos', payload);
    },

    setMPos(context, payload) {
        context.commit('setMPos', payload);
    },

    setCNCState(context, payload) {
        context.commit('setCNCState', payload);
    }
}