export default {
    setEvents(state, payload) {
        // Handle both array and object responses
        state.events = Array.isArray(payload) ? payload : (payload?.events || []);
    },

    setChannels(state, payload) {
        // Handle both array and object responses
        state.channels = Array.isArray(payload) ? payload : (payload?.channels || []);
    },

    setFiles(state, payload) {
        // Handle both array and object responses
        state.files = Array.isArray(payload) ? payload : (payload?.files || []);
    },

    addChannel(state) {
        // Handle both array and object state
        let currentChannels = Array.isArray(state.channels) ? state.channels : (state.channels?.channels || []);
        let channelNumber = currentChannels.length;
        if (Array.isArray(state.channels)) {
            state.channels.push(channelNumber);
        } else {
            state.channels.channels.push(channelNumber);
        }
    }
}