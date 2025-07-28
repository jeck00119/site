export default {

    setCamerasList(state, payload){
        state.cameraList = payload;
    },

    setCameraTypesList(state, payload){
        state.cameraTypesList = payload;
    },

    setcurrentCamera(state, payload){
        state.currentCamera = payload;
    },

    setCameraSettingsList(state, payload){
        state.cameraSettingsList = payload;
    },

    addCameraSettingsList(state, payload)
    {
        state.cameraSettingsList.push(payload);
    },

    setCameraControls(state, payload)
    {
        state.cameraControls = payload;
    },

    setCurrentCameraConfig(state, payload)
    {
        state.currentCameraSettings = payload;
    },

    setCurrentCameraDefaultSettings(state, payload) {
        state.currentCameraDefaultSettings = payload;
    },

    setCurrentCameraConfigName(state, payload) {
        state.currentCameraSettings["name"] = payload;
    },

    setCurrentCameraConfigCameraType(state, payload) {
        state.currentCameraSettings["cameraType"] = payload;
    },

    updateCurrentCameraSettings(state, payload)
    {
        state.currentCameraSettings[payload.name] = payload.value;
    },

    updateCameraSettingsListById(state, payload) {
        const foundIdx  = state.cameraSettingsList.findIndex(settings => settings.uid === payload.uid);
        state.cameraSettingsList[foundIdx] = payload;
    },

    removeCameraSettings(state, payload) {
        const foundIdx = state.cameraSettingsList.findIndex(settings => settings.uid === payload);
        state.cameraSettingsList.splice(foundIdx, 1);
    },

    addCamera(state, payload) {
        state.cameraList.push(payload);
    },

    removeCamera(state, payload) {
        const cameraIdx = state.cameraList.findIndex(camera => camera.uid === payload.uid);
        state.cameraList.splice(cameraIdx, 1);
    }
}