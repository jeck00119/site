import settingsGetters from "./getters";
import mutations from "./mutations";
import actions from "./actions";

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