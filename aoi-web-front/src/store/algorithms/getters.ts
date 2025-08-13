export default {
    getAlgorithms(state) {
        return state.algorithms || [];
    },

    getBasicAlgorithms(state) {
        return state.basicAlgorithms || [];
    },

    getReferenceAlgorithms(state) {
        return state.referenceAlgorithms || [];
    },

    getConfiguredAlgorithms(state) {
        return state.configuredAlgorithms || [];
    },

    getConfiguredAlgorithmById: (state) => (id) => {
        return state.configuredAlgorithms.find(algorithm => algorithm.uid === id);
    },

    getCurrentAlgorithm(state) {
        return state.currentAlgorithm;
    },

    getCurrentReferenceAlgorithm(state) {
        return state.currentReferenceAlgorithm;
    },

    getAlgorithmResult(state) {
        return state.algorithmResult;
    },

    getAlgorithmById: (state) => (id) => {
        return state.algorithms.find(alg => alg.uid === id);
    },

    getAlgorithmByType: (state) => (type) => {
        return state.algorithms.find(alg => alg.type === type);
    },

    getReferenceAlgorithmById: (state) => (id) => {
        return state.referenceAlgorithms.find(alg => alg.uid === id);
    },

    getReferenceAlgorithmByType: (state) => (type) => {
        return state.referenceAlgorithms.find(alg => alg.type === type);
    },

    getCurrentAlgorithmAttributes(state) {
        return state.currentAlgorithmAttributes || [];
    },

    getCurrentReferenceAlgorithmAttributes(state) {
        return state.currentReferenceAlgorithmAttributes || [];
    },

    getBasicAlgorithmsAttributes(state) {
        return state.basicAlgorithmsAttributes || [];
    },

    getBasicAlgorithmAttributesAtIndex: (state) => (idx) => {
        return state.basicAlgorithmsAttributes[idx];
    },

    getCurrentBasicAlgorithms(state) {
        return state.currentBasicAlgorithms || [];
    },

    getCurrentBasicAlgorithmAtIndex: (state) => (idx) => {
        return state.currentBasicAlgorithms[idx];
    }
}