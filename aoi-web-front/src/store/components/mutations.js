export default {
    addComponent(state, payload) {
        state.components.push(payload);
    },

    removeComponent(state, payload) {
        const componentIndex = state.components.findIndex(component => component.uid === payload);
        state.components.splice(componentIndex, 1);
    },

    setComponents(state, payload) {
        state.components = payload;
    },

    setCurrentComponent(state, payload) {
        state.currentComponent = payload;
    },

    updateComponent(state, payload) {
        const componentIndex = state.components.findIndex(component => component.uid === payload.uid);
        state.components[componentIndex].name = payload.name;

        state.currentComponent = payload;
    },

    addReference(state, payload) {
        state.references.push(payload);
    },

    removeReference(state, payload) {
        const referenceIndex = state.references.findIndex(references => references.uid === payload);
        state.references.splice(referenceIndex, 1);
    },

    setReferences(state, payload) {
        state.references = payload;
    },

    updateReference(state, payload) {
        const referenceIndex = state.references.findIndex(reference => reference.uid === payload.uid);
        state.references[referenceIndex].name = payload.name;

        state.currentComponent = payload;
    },

    addIdentification(state, payload) {
        state.identifications.push(payload);
    },

    removeIdentification(state, payload) {
        const identificationIndex = state.identifications.findIndex(identification => identification.uid === payload);
        state.identifications.splice(identificationIndex, 1);
    },

    setIdentifications(state, payload) {
        state.identifications = payload;
    },

    updateIdentification(state, payload) {
        const identificationIndex = state.identifications.findIndex(identification => identification.uid === payload.uid);
        state.identifications[identificationIndex].name = payload.name;

        state.currentComponent = payload;
    }
}