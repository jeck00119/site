export default {
    getImageSources(state) {
        return state.imageSources;
    },

    getCurrentImageSource(state) {
        return state.currentImageSource;
    },

    getImageGenerators(state) {
        return state.imageGenerators;
    },

    getImageGeneratorById: (state) => (id) => {
        let gen = state.imageGenerators.find(gen => gen.uid === id);
        if(gen)
            return gen

        return null
    },

    getCurrentImageGenerator(state) {
        return state.currentImageGenerator; 
    },

    getImageSourceById: (state) => (id) => {
        return state.imageSources.find(source => source.uid === id) || null;
    }
}