import api from "@/utils/api";
import { ActionContext } from "vuex";
import { CameraCalibrationState } from "./types";

type Context = ActionContext<CameraCalibrationState, any>;

export default {
    async fetchCalibrationData({ commit }: Context, cameraId: string) {
        try {
            const response = await api.get(`/camera-calibration/${cameraId}`);
            commit("SET_CALIBRATION_DATA", { cameraId, data: response.data });
            return response.data;
        } catch (error) {
            commit("SET_CALIBRATION_ERROR", error.message);
            throw error;
        }
    },

    async startCalibration({ commit }: Context, cameraId: string) {
        try {
            commit("SET_CALIBRATING", true);
            const response = await api.post(`/camera-calibration/${cameraId}/start`);
            return response.data;
        } catch (error) {
            commit("SET_CALIBRATION_ERROR", error.message);
            throw error;
        } finally {
            commit("SET_CALIBRATING", false);
        }
    },

    async saveCalibration({ commit }: Context, { cameraId, data }: any) {
        try {
            const response = await api.post(`/camera-calibration/${cameraId}`, data);
            commit("SET_CALIBRATION_DATA", { cameraId, data: response.data });
            return response.data;
        } catch (error) {
            commit("SET_CALIBRATION_ERROR", error.message);
            throw error;
        }
    },

    clearCalibrationError({ commit }: Context) {
        commit("SET_CALIBRATION_ERROR", null);
    }
};