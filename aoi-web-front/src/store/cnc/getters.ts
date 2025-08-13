export default {
    getPorts(state) {
        return state.ports;
    },

    getCNCs(state) {
        return state.cncs;
    },

    getCNC: (state) => (uid) => {
        return state.cncs.find(cnc => cnc.uid === uid);
    },

    getCNCTypes(state) {
        return state.cncTypes;
    },

    mPos: (state) => (id) => {
        return state.positionData[id] ? state.positionData[id].mPos : {'x': 0, 'y': 0, 'z': 0};
    },

    wPos: (state) => (id) => {
        return state.positionData[id] ? state.positionData[id].wPos : {'x': 0, 'y': 0, 'z': 0};
    },

    pos: (state) => (id) => {
        return state.positionData[id] ? state.positionData[id].pos : {'x': 0, 'y': 0, 'z': 0};
    },

    cncState: (state) => (id) => {
        return state.cncStates[id] ? state.cncStates[id] : null;
    },

    locations: (state) => {
        return state.locations;
    }
}