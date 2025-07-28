export default {
    async loadItacList(state, payload) {
        state.itacList = payload;
    },

    async deleteItac(state, payload) {
        const idx = state.itacList.findIndex(itac => itac.uid === payload.uid);
        state.itacList.splice(idx, 1);
    },

    async saveItac(state, payload) {
        state.itacList.push(payload);
    },

    async updateItac(state, payload) {
        const idx = state.itacList.findIndex(itac => itac.uid === payload.uid);
        state.itacList[idx] = payload;
    }
}