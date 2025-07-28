export default {
    setEvents(state, payload) {
        state.events = payload;
    },

    setChannels(state, payload) {
        state.channels = payload;
    },

    setFiles(state, payload) {
        state.files = payload;
    },

    addChannel(state) {
        let channelNumber = state.channels.length;
        state.channels.push(channelNumber);
    }
}