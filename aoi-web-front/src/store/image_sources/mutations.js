export default {
    setImageSources(state, payload) {
        state.imageSources = payload
    },

    setCurrentImageSource(state, payload) {
        state.currentImageSource = payload
    },

    setCurrentImageSourceProp(state, payload) {
        state.currentImageSource[payload.key] = payload.value;
    },

    setImageGenerators(state, payload) {
        state.imageGenerators = payload
    },

    setCurrentImageGenerator(state, payload) {
        state.currentImageGenerator = payload
    },

    setCurrentImageGeneratorProp(state, payload) {
        state.currentImageGenerator[payload.key] = payload.value;
    },

    addImageSource(state,payload) {
        state.imageSources.push(payload);
    },

    addImageGenerator(state,payload) {
        state.imageGenerators.push(payload);
    },

    removeImageSource(state,payload) {
        const imageSourceIndex = state.imageSources.findIndex(imageSource => imageSource.uid === payload);
        state.imageSources.splice(imageSourceIndex, 1);
    },

    updateImageSource(state,payload) {
        const imageSourceIndex = state.imageSources.findIndex(imageSource => imageSource.uid === payload.uid);
        state.imageSources[imageSourceIndex].name = payload.name;

        state.currentImageSource = payload;
    }

}