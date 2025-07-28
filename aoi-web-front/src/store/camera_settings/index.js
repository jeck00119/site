import settingsGetters from "./getters.js";
import mutations from "./mutations.js";
import actions from "./actions.js";

export default {
    namespaced: true,
    state(){
        return {
           cameraList: null,
           cameraSettingsList: [],
           cameraControls: null,
           currentCamera: null,
           currentCameraSettings: {},
           currentCameraDefaultSettings: {},
           cameraTypesList: []
        };
    },

    getters: settingsGetters,
    mutations: mutations,
    actions: actions
}