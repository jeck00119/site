import { CameraCalibrationState } from "./types";

export default {
    getCalibrationByCameraId: (state: CameraCalibrationState) => (cameraId: string) => {
        return state.calibrationData[cameraId] || null;
    },

    isCalibrating: (state: CameraCalibrationState) => {
        return state.isCalibrating;
    },

    hasCalibrationError: (state: CameraCalibrationState) => {
        return state.calibrationError !== null;
    },

    calibrationError: (state: CameraCalibrationState) => {
        return state.calibrationError;
    }
};