import { uuid } from "vue3-uuid";
import { get, post, put, remove } from "../../utils/requests";
import { ipAddress, port } from "../../url.js";

export default {
    async loadPorts(context, _) {
        const { response, responseData } = await get(`http://${ipAddress}:${port}/cnc/check_ports`);

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
        const { response, responseData } = await get(`http://${ipAddress}:${port}/cnc`);

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
        const { response, responseData } = await get(`http://${ipAddress}:${port}/cnc/cnc_types`);

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

        const response = await post(`http://${ipAddress}:${port}/cnc/save`, cncs, {
            "content-type": "application/json",
            "Authorization": token
        });

        if(!response.ok)
        {
            const error = new Error(`Failed to save CNCs!`);
            throw error;
        }
    },

    updateCNCPort(context, payload) {
        context.commit('updateCNCPort', payload);
    },

    updateCNCType(context, payload) {
        context.commit('updateCNCType', payload);
    },

    async fetchLocations(context, payload){
        const {response, responseData} = await get(`http://${ipAddress}:${port}/location/axis/${payload}`);

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

        const {response, responseData} = await post (`http://${ipAddress}:${port}/location`, payload[0], {
            'content-type': 'application/json',
            'Authorization': token
        });
    },

    async loadLocations(context,_){
        const { response, responseData } = await get('http://localhost:8000/location');
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
            const { response, responseData } = await put(`http://${ipAddress}:${port}/location`, patchedLocation, {
                "content-type": "application/json",
                "Authorization": token
            });
        } catch (error) {
            patchedLocation.name = oldName;
        }
    },

    async deleteLocation(context, payload){
        const token = context.rootGetters["auth/getToken"];
        const { response, responseData } = await remove(`http://${ipAddress}:${port}/location/${payload}`, {
            "content-type": "application/json",
            "Authorization": token
        });
    },

    async api_moveToLocation(context, payload){
        const { response, responseData } = await get(`http://${ipAddress}:${port}/cnc/${payload.cncUid}/__API__/${payload.location}/move_to_location?block=${payload.block}&timeout=${payload.timeout}`);
    },

    async api_command(context, payload){
        const { response, responseData } = await get(`http://${ipAddress}:${port}/cnc/${payload.cncUid}/__API__/${payload.command}`);
    },

    async api_increaseAxis(context, payload){
        const { response, responseData } = await get(`http://${ipAddress}:${port}/cnc/${payload.cncUid}/__API__/${payload.axis}/plus?feed_rate=${payload.feedrate}&step=${payload.step}`);
    },

    async api_decreaseAxis(context, payload){
        const { response, responseData } = await get(`http://${ipAddress}:${port}/cnc/${payload.cncUid}/__API__/${payload.axis}/minus?feed_rate=${payload.feedrate}&step=${payload.step}`);
    },

    async api_terminal(context, payload){
        const {response, responseData} = await get(`http://${ipAddress}:${port}/cnc/${payload.cncUid}/__API__/terminal?command=${payload.command}`)
    },

    async closeStateSocket(_, payload) {
        const response = await post(`http://${ipAddress}:${port}/cnc/${payload.uid}/ws/close`);

        if(!response.ok)
        {
            const error = new Error(`Failed to close socket for CNC with ID ${payload.uid}!`);
            throw error;
        }
    },

    async initializeAllCNCs(context, _) {
        const { response, responseData } = await post(`http://${ipAddress}:${port}/cnc/initialize_all`);

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