import actions from "./actions";
import getters from "./getters";
import mutations from "./mutations";

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