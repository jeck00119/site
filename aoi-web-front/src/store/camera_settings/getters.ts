export default {

    allCameras: (state) => {
        return state.cameraList;
    },
    
    allCameraSettings: (state) => {
        return state.cameraSettingsList;
    },
        
    getcameraControls: (state) => {
        return state.cameraControls;
    },

    getCurrentCameraSettings:(state)=>{
        return state.currentCameraSettings;
    },

    getCurrentCameraDefaultSettings(state) {
        return state.currentCameraDefaultSettings;
    },

    getCameraTypes:(state) => {
        return state.cameraTypesList;
    },

    getCurrentCamera:(state) => {
        return state.currentCamera;
    }
}