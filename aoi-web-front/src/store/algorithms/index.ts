import actions from "./actions";
import getters from "./getters";
import mutations from "./mutations";

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
            currentAlgorithmAttributes: [],
            currentReferenceAlgorithmAttributes: [],
            algorithmResult: null,
            basicAlgorithmsAttributes: [],
            currentBasicAlgorithms: []
        };
    },

    getters: getters,
    mutations: mutations,
    actions: actions
}