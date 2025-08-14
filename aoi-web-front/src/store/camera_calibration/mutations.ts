import { CameraCalibrationState, CalibrationPayload } from "./types";

export default {
    SET_CALIBRATION_DATA(state: CameraCalibrationState, payload: CalibrationPayload) {
        state.calibrationData[payload.cameraId] = payload.data;
    },

    SET_CALIBRATING(state: CameraCalibrationState, value: boolean) {
        state.isCalibrating = value;
    },

    SET_CALIBRATION_ERROR(state: CameraCalibrationState, error: string | null) {
        state.calibrationError = error;
    },

    CLEAR_CALIBRATION_DATA(state: CameraCalibrationState) {
        state.calibrationData = {};
        state.calibrationError = null;
    }
};