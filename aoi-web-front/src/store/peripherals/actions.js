import { post } from "../../utils/requests";
import { ipAddress, port } from "../../url.js";

export default {
    async closeDeviceStateSocket(_, payload) {
        try {
            const response = await post(`http://${ipAddress}:${port}/peripheral/${payload.uid}/ws/close`);

            if(!response.ok)
            {
                // Log warning but don't throw error - socket might already be closed
                console.warn(`Socket for device state with ID ${payload.uid} may already be closed or doesn't exist`);
            }
        } catch (error) {
            // Don't throw error for socket cleanup - just log it
            console.warn(`Error closing socket for device state with ID ${payload.uid}:`, error.message);
        }
    }
}