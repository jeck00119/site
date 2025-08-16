import { post } from "../../utils/requests";
import { ipAddress, port } from "../../url";

export default {
    async setCalibrationParameters(context, payload) {
        const token = context.rootGetters["auth/getToken"] || sessionStorage.getItem('auth-token');

        const response = await post(`http://${ipAddress}:${port}/stereo_calibration`, payload, {
            "content-type": "application/json",
            "Authorization": token
        });

        if(!response.ok)
        {
            const error = new Error(`Failed to start calibration!`);
            throw error;
        }
    },

    async closeCalibrationSocket(_, payload) {
        const response = await post(`http://${ipAddress}:${port}/stereo_calibration/${payload.uid}/ws/close`);

        if(!response.ok)
        {
            const error = new Error(`Failed to close socket for calibration with ID ${payload.uid}!`);
            throw error;
        }
    }
}