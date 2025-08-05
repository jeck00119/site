export default {
    setEvents(state, payload) {
        // Handle both array and object responses
        // If payload is array of objects with 'name' property, extract just the names
        if (Array.isArray(payload)) {
            if (payload.length > 0 && typeof payload[0] === 'object' && payload[0].name) {
                state.events = payload.map(item => item.name);
            } else {
                state.events = payload;
            }
        } else {
            state.events = payload?.events || [];
        }
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