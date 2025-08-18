import { v4 as uuidv4 } from "uuid";
import api from "../../utils/api";
import logger from "../../utils/logger";

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
        logger.debug('CNC Store: loadCNCs action called');
        try {
            const token = context.rootGetters["auth/getToken"] || sessionStorage.getItem('auth-token');
            logger.debug('CNC Store: Token retrieved', { tokenPresent: !!token });
            
            const { response, responseData } = await api.get('/cnc', {
                "Authorization": token
            });
            
            logger.debug('CNC Store: API response status', { status: response.status, ok: response.ok });
            logger.debug('CNC Store: Response data', responseData);

            if(!response.ok)
            {
                const error = new Error(responseData.detail || `Failed to fetch CNCs! Status: ${response.status}`);
                logger.error('CNC Store: API call failed', error);
                throw error;
            }
            else
            {
                logger.debug('CNC Store: Committing CNCs to store', responseData);
                context.commit('loadCNCs', responseData);
            }
        } catch (error) {
            logger.error('CNC Store: Exception in loadCNCs', error);
            throw error;
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
            uid: uuidv4(),
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
        const token = context.rootGetters["auth/getToken"] || sessionStorage.getItem('auth-token');

        try {
            const { response, data } = await api.post('/cnc/save', { cnc_list: cncs }, {
                "content-type": "application/json",
                "Authorization": token
            });

            if(!response.ok) {
                const errorMessage = data?.message || 'Failed to save CNCs - some CNCs may have connection issues';
                logger.warn('CNC Save Warning', { message: errorMessage });
                // Don't throw error - allow operation to continue
                // The individual CNC connection errors will be handled via WebSocket callbacks
                return { success: false, message: errorMessage };
            }
            
            return { success: true };
        } catch (error) {
            logger.error('CNC Save Error', error);
            // Don't throw error - allow operation to continue gracefully
            return { success: false, message: (error as Error).message || 'Failed to save CNCs' };
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
        payload[0].uid = uuidv4();
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

        const token = context.rootGetters["auth/getToken"] || sessionStorage.getItem('auth-token');
        
        logger.debug('CNC postLocation - token', { tokenPresent: !!token });
        logger.debug('CNC postLocation - payload', payload[0]);

        const {response, responseData} = await api.post('/location', payload[0], {
            'content-type': 'application/json',
            'Authorization': token
        });
        
        logger.debug('CNC postLocation - response', { status: response.status, ok: response.ok });
        logger.debug('CNC postLocation - responseData', responseData);
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
            const token = context.rootGetters["auth/getToken"] || sessionStorage.getItem('auth-token');
            const { response, responseData } = await api.put('/location', patchedLocation, {
                "content-type": "application/json",
                "Authorization": token
            });
        } catch (error) {
            patchedLocation.name = oldName;
        }
    },

    async patchLocationWithCoordinates(context, payload){
        let patchedLocation = null
        for(const location of context.state.locations){
            if (location.uid == payload.locationUid){
                patchedLocation = location;
                break;
            }
        }
        if (!patchedLocation) {
            throw new Error('Location not found');
        }
        
        // Store old values for rollback
        const oldValues = {
            name: patchedLocation.name,
            x: patchedLocation.x,
            y: patchedLocation.y,
            z: patchedLocation.z,
            feedrate: patchedLocation.feedrate
        };
        
        // Update location with new values
        patchedLocation.name = payload.name;
        patchedLocation.x = payload.x;
        patchedLocation.y = payload.y;
        patchedLocation.z = payload.z;
        patchedLocation.feedrate = payload.feedrate;
        
        try{
            const token = context.rootGetters["auth/getToken"] || sessionStorage.getItem('auth-token');
            const { response, responseData } = await api.put('/location', patchedLocation, {
                "content-type": "application/json",
                "Authorization": token
            });
            if (!response.ok) {
                throw new Error(responseData.detail || 'Failed to update location');
            }
        } catch (error) {
            // Rollback changes on error
            patchedLocation.name = oldValues.name;
            patchedLocation.x = oldValues.x;
            patchedLocation.y = oldValues.y;
            patchedLocation.z = oldValues.z;
            patchedLocation.feedrate = oldValues.feedrate;
            throw error;
        }
    },

    async deleteLocation(context, payload){
        const token = context.rootGetters["auth/getToken"] || sessionStorage.getItem('auth-token');
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
                logger.error('CNC Move to Location Error', error);
                throw error;
            }
        } catch (error) {
            logger.error('CNC Move to Location Exception', error);
            throw error;
        }
    },

    async api_command(context, payload){
        try {
            const { response, responseData } = await api.get(`/cnc/${payload.cncUid}/__API__/${payload.command}`);
            if (!response.ok) {
                const error = new Error(responseData.detail || `Failed to execute command '${payload.command}' on CNC ${payload.cncUid}`);
                logger.error('CNC Command Error', error);
                throw error;
            }
            
            // Log important commands for monitoring
            if (payload.command === 'home' || payload.command.includes('G28')) {
                logger.info(`Homing command executed on CNC ${payload.cncUid}`);
            }
            
        } catch (error) {
            logger.error('CNC Command Exception', error);
            throw error;
        }
    },

    async api_increaseAxis(context, payload){
        try {
            const { response, responseData } = await api.get(`/cnc/${payload.cncUid}/__API__/${payload.axis}/plus?feed_rate=${payload.feedrate}&step=${payload.step}`);
            if (!response.ok) {
                const error = new Error(responseData.detail || `Failed to move CNC ${payload.cncUid} axis ${payload.axis} plus by ${payload.step} steps`);
                logger.error('CNC Axis Plus Error', error);
                throw error;
            }
        } catch (error) {
            logger.error('CNC Axis Plus Exception', error);
            throw error;
        }
    },

    async api_decreaseAxis(context, payload){
        try {
            const { response, responseData } = await api.get(`/cnc/${payload.cncUid}/__API__/${payload.axis}/minus?feed_rate=${payload.feedrate}&step=${payload.step}`);
            if (!response.ok) {
                const error = new Error(responseData.detail || `Failed to move CNC ${payload.cncUid} axis ${payload.axis} minus by ${payload.step} steps`);
                logger.error('CNC Axis Minus Error', error);
                throw error;
            }
        } catch (error) {
            logger.error('CNC Axis Minus Exception', error);
            throw error;
        }
    },

    async api_terminal(context, payload){
        try {
            const {response, responseData} = await api.get(`/cnc/${payload.cncUid}/__API__/terminal?command=${payload.command}`);
            if (!response.ok) {
                const error = new Error(responseData.detail || `Failed to send terminal command '${payload.command}' to CNC ${payload.cncUid}`);
                logger.error('CNC Terminal Error', error);
                throw error;
            }
        } catch (error) {
            logger.error('CNC Terminal Exception', error);
            throw error;
        }
    },

    async initializeCNC(context, payload) {
        try {
            const { response, responseData } = await api.post(`/cnc/${payload.cncUid}/initialize`);
            if (!response.ok) {
                // Extract detailed error message from backend response
                const errorMessage = responseData?.detail || responseData?.message || `Failed to initialize CNC ${payload.cncUid}`;
                const error = new Error(errorMessage);
                logger.error('CNC Initialize Error', error);
                throw error;
            }
        } catch (error) {
            logger.error('CNC Initialize Exception', error);
            throw error;
        }
    },

    async deinitializeCNC(context, payload) {
        try {
            const { response, responseData } = await api.post(`/cnc/${payload.cncUid}/deinitialize`);
            if (!response.ok) {
                const error = new Error(responseData.detail || `Failed to deinitialize CNC ${payload.cncUid}`);
                logger.error('CNC Deinitialize Error', error);
                throw error;
            }
        } catch (error) {
            logger.error('CNC Deinitialize Exception', error);
            throw error;
        }
    },

    async closeStateSocket(_, payload) {
        try {
            const { response, responseData } = await api.post(`/cnc/${payload.uid}/ws/close`);
            if(!response.ok) {
                logger.warn(`Socket for CNC ${payload.uid} may already be closed or doesn't exist`, { detail: responseData?.detail || 'Unknown error' });
            }
        } catch (error) {
            logger.warn(`Error closing socket for CNC ${payload.uid}`, error);
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
        // Use optimized single mutation instead of 3-4 separate commits
        context.commit('updateAllPositions', payload);
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
    },

}