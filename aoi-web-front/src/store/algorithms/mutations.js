export default {
    setAlgorithms(state, payload) {
        state.algorithms = payload;
    },

    setBasicAlgorithms(state, payload) {
        state.basicAlgorithms = payload;
    },

    setReferenceAlgorithms(state, payload) {
        state.referenceAlgorithms = payload;
    },

    setCurrentAlgorithm(state, payload) {
        state.currentAlgorithm = payload;
    },

    setCurrentReferenceAlgorithm(state, payload) {
        state.currentReferenceAlgorithm = payload;
    },

    setConfiguredAlgorithms(state, payload) {
        state.configuredAlgorithms = payload;
    },

    setAlgorithmResult(state, payload) {
        state.algorithmResult = payload
    },

    removeAlgorithm(state, payload) {
        const algIndex = state.algorithms.findIndex(alg => alg.uid === payload.uid);
        state.algorithms.splice(algIndex, 1);
    },

    addAlgorithm(state, payload) {
        const algorithm = {
            uid: payload.uid,
            type: payload.type
        };

        state.algorithms.push(algorithm);
        state.currentAlgorithm = payload;
    },

    addConfiguredAlgorithm(state, payload){
        state.configuredAlgorithms.push({
            uid: payload.uid,
            name: payload.name
        });
    },

    setCurrentAlgorithmAttributes(state, payload) {
        state.currentAlgorithmAttributes = payload;
    },

    setCurrentReferenceAlgorithmAttributes(state, payload) {
        state.currentReferenceAlgorithmAttributes = payload;
    },

    updateCurrentAlgorithmGraphics(state, payload) {
        if(state.currentAlgorithm)
        {
            state.currentAlgorithm.parameters.graphics = payload;
        }
    },

    updateCurrentReferenceAlgorithmGraphics(state, payload) {
        if(state.currentReferenceAlgorithm)
        {
            state.currentReferenceAlgorithm.parameters.graphics = payload;
        }
    },

    updateCurrentAlgorithmProperty(state, payload) {
        state.currentAlgorithm.parameters[payload.name] = payload.value;
    },

    updateCurrentReferenceAlgorithmProperty(state, payload) {
        state.currentReferenceAlgorithm.parameters[payload.name] = payload.value;
    },

    deleteKeyFromAlgorithmAttributes(state, payload) {
        state.currentAlgorithmAttributes.splice(payload.key, 1);
    },

    deleteKeyFromReferenceAlgorithmAttributes(state, payload) {
        state.currentReferenceAlgorithmAttributes.splice(payload.key, 1);
    },

    updateCurrentAlgorithmAttributes(state, payload) {
        for(const key in state.currentAlgorithmAttributes)
        {
            if(state.currentAlgorithmAttributes[key].name === payload.name
                && !state.currentAlgorithmAttributes[key].values.includes(payload.value))
            {
                state.currentAlgorithmAttributes[key].values.push(payload.value);
                break;
            }
        }
    },

    updateCurrentReferenceAlgorithmAttributes(state, payload) {
        for(const key in state.currentReferenceAlgorithmAttributes)
        {
            if(state.currentReferenceAlgorithmAttributes[key].name === payload.name
                && !state.currentReferenceAlgorithmAttributes[key].values.includes(payload.value))
            {
                state.currentReferenceAlgorithmAttributes[key].values.push(payload.value);
                break;
            }
        }
    },

    deleteGraphicsFromAlgorithmAttributes(state) {
        for(const key in state.currentAlgorithmAttributes)
        {
            if(state.currentAlgorithmAttributes[key].name === 'graphics')
            {
                state.currentAlgorithmAttributes.splice(key, 1);
                break;
            }
        }
    },

    deleteGraphicsFromReferenceAlgorithmAttributes(state) {
        for(const key in state.currentReferenceAlgorithmAttributes)
        {
            if(state.currentReferenceAlgorithmAttributes[key].name === 'graphics')
            {
                state.currentReferenceAlgorithmAttributes.splice(key, 1);
                break;
            }
        }
    },

    addBasicAlgorithmAttributes(state, payload) {
        state.basicAlgorithmsAttributes.push(payload);
    },

    addCurrentBasicAlgorithm(state, payload) {
        state.currentBasicAlgorithms.push(payload);
    },

    resetBasicAlgorithmsAttributes(state, _) {
        state.basicAlgorithmsAttributes = []
    },

    resetCurrentBasicAlgorithms(state, _) {
        state.currentBasicAlgorithms = []
    },

    updateCurrentBasicAlgorithmProperty(state, payload) {
        state.currentBasicAlgorithms[payload.idx][payload.name] = payload.value;
    },

    deleteKeyFromBasicAlgorithmAttributes(state, payload) {
        state.basicAlgorithmsAttributes[payload.idx].splice(payload.key, 1);
    },

    deleteGraphicsFromBasicAlgorithmAttributes(state, payload) {
        for(const key in state.basicAlgorithmsAttributes[payload.idx])
        {
            if(state.basicAlgorithmsAttributes[payload.idx][key].name === 'graphics')
            {
                state.basicAlgorithmsAttributes[payload.idx].splice(key, 1);
                break;
            }
        }
    },

    updateCurrentBasicAlgorithmAttributes(state, payload) {
        for(const key in state.basicAlgorithmsAttributes[payload.idx])
        {
            if(state.basicAlgorithmsAttributes[key].name === payload.name
                && !state.basicAlgorithmsAttributes[key].values.includes(payload.value))
            {
                state.basicAlgorithmsAttributes[key].values.push(payload.value);
                break;
            }
        }
    }
}