import actions from "./actions";
import mutations from "./mutations";
import getters from "./getters";
import { CameraCalibrationState } from "./types";

const state: CameraCalibrationState = {
    calibrationData: {},
    isCalibrating: false,
    calibrationError: null
};

export default {
    namespaced: true,
    state,
    actions,
    mutations,
    getters
}