export default {
    getComponentsNameId(_, getters) {
        const components = getters.getAllComponents;

        const componentsNameId = components.map(function(component) {
            return {
                id: component.id,
                name: component.name
            }
        });

        return componentsNameId;
    },

    getComponent: (state) => (id) => {
        return state.components.find(component => component.id === id);
    },

    getAllComponents(state) {
        return state.components;
    },

    getCurrentComponent(state) {
        return state.currentComponent;
    },

    getReferences(state) {
        return state.references;
    },

    getReferenceById: (state) => (id) => {
        return state.references.find(reference => reference.uid === id);
    },

    getIdentifications(state) {
        return state.identifications;
    },

    getIdentificationById: (state) => (id) => {
        return state.identifications.find(identification => identification.uid === id);
    }
}