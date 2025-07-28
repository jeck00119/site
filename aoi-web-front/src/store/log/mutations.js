export default {
    setEvents(state, payload) {
        state.events = payload;
    },

    addEvent(state, payload) {
        state.events.push(payload);
    },

    removeEvent(state, payload) {
        const eventId = state.events.findIndex(event => event.id === payload.uid);
        state.events.splice(eventId, 1);
    }
}