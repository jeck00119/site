export default {
    setColumnNames(state, payload) {
        state.columnNames = payload;
    },

    setColumnTypes(state, payload) {
        state.columnTypes = payload;
    },

    setInspections(state, payload) {
        state.inspections = payload;
    }
}