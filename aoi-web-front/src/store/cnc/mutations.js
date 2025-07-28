export default {
    loadPorts(state, payload) {
        state.ports = payload;
    },

    loadCNCs(state, payload) {
        state.cncs = payload;
    },

    loadCNCTypes(state, payload) {
        state.cncTypes = payload;
    },

    resetPorts(state) {
        state.ports = [];
    },

    resetCNCs(state) {
        state.cncs = [];
    },

    addCNC(state, payload) {
        state.cncs.push(payload);
    },

    removeCNC(state, payload) {
        const idx = state.cncs.findIndex(cnc => cnc.uid === payload.uid);
        state.cncs.splice(idx, 1);
    },

    updateCNCPort(state, payload) {
        const idx = state.cncs.findIndex(cnc => cnc.uid === payload.uid);
        state.cncs[idx].port = payload.port;
    },

    updateCNCType(state, payload) {
        const idx = state.cncs.findIndex(cnc => cnc.uid === payload.uid);
        state.cncs[idx].type = payload.type;
    },

    locations(state, payload){
        state.locations = payload
    },

    addPositionData(state, payload) {
        state.positionData[payload.uid] = {};
        state.positionData[payload.uid].pos = {'x': 0, 'y': 0, 'z': 0};
        state.positionData[payload.uid].mPos = {'x': 0, 'y': 0, 'z': 0};
        state.positionData[payload.uid].wPos = {'x': 0, 'y': 0, 'z': 0};
    },

    setMPos(state, payload){
        state.positionData[payload.uid].mPos.x = (payload.x);
        state.positionData[payload.uid].mPos.y = (payload.y);
        state.positionData[payload.uid].mPos.z = (payload.z);
    },

    setWPos(state, payload){
        state.positionData[payload.uid].wPos.x = (payload.x);
        state.positionData[payload.uid].wPos.y = (payload.y);
        state.positionData[payload.uid].wPos.z = (payload.z);
    },

    setPos(state, payload){
        state.positionData[payload.uid].pos.x = state.positionData[payload.uid].mPos.x - state.positionData[payload.uid].wPos.x;
        state.positionData[payload.uid].pos.y = state.positionData[payload.uid].mPos.y - state.positionData[payload.uid].wPos.y
        state.positionData[payload.uid].pos.z = state.positionData[payload.uid].mPos.z - state.positionData[payload.uid].wPos.z
    },

    setCNCState(state, payload){
        state.cncStates[payload.uid] = payload.state;
    }
}