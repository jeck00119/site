import { post } from "../../utils/requests";
import { ipAddress, port } from "../../url.js";

export default {
    async closeDeviceStateSocket(_, payload) {
        const response = await post(`http://${ipAddress}:${port}/peripheral/${payload.uid}/ws/close`);

        if(!response.ok)
        {
            const error = new Error(`Failed to close socket for device state with ID ${payload.uid}!`);
            throw error;
        }
    }
}