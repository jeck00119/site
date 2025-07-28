import { post } from '../../utils/requests.js';
import { ipAddress, port } from "../../url.js";

export default {
    async setCalibrationParameters(context, payload) {
        const token = context.rootGetters["auth/getToken"];

        const response = await post(`http://${ipAddress}:${port}/camera_calibration`, payload, {
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
        const response = await post(`http://${ipAddress}:${port}/camera_calibration/${payload.uid}/ws/close`);

        if(!response.ok)
        {
            const error = new Error(`Failed to close socket for calibration with ID ${payload.uid}!`);
            throw error;
        }
    }
}