import actions from "./actions.js";
import getters from "./getters.js";
import mutations from "./mutations.js";

export default {
    namespaced: true,
    state() {
        return {
            imageSources:[],
            currentImageSource: null,
            currentImageGenerator: null,
            imageGenerators:[]
        };
    },

    getters: getters,
    actions: actions,
    mutations: mutations
}