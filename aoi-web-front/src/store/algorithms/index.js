import actions from "./actions.js";
import getters from "./getters.js";
import mutations from "./mutations.js";

export default {
    namespaced: true,
    state() {
        return {
            algorithms: [],
            basicAlgorithms: [],
            referenceAlgorithms: [],
            configuredAlgorithms: [],
            currentAlgorithm: null,
            currentReferenceAlgorithm: null,
            currentAlgorithmAttributes: null,
            currentReferenceAlgorithmAttributes: null,
            algorithmResult: null,
            basicAlgorithmsAttributes: [],
            currentBasicAlgorithms: []
        };
    },

    getters: getters,
    mutations: mutations,
    actions: actions
}