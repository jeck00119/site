export default {
    loadItacList(state, payload) {
        state.itacList = payload;
    },

    deleteItac(state, payload) {
        const idx = state.itacList.findIndex(itac => itac.uid === payload.uid);
        if (idx !== -1) {
            state.itacList.splice(idx, 1);
        }
    },

    saveItac(state, payload) {
        state.itacList.push(payload);
    },

    updateItac(state, payload) {
        const idx = state.itacList.findIndex(itac => itac.uid === payload.uid);
        if (idx !== -1) {
            state.itacList[idx] = payload;
        }
    }
}