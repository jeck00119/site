import { post } from "../../utils/requests";
import { ipAddress, port } from "../../url";
import { logger } from "../../utils/logger";

export default {
    async closeDeviceStateSocket(_, payload) {
        try {
            const response = await post(`http://${ipAddress}:${port}/peripheral/${payload.uid}/ws/close`);

            if(!response.ok)
            {
                // Log warning but don't throw error - socket might already be closed
                logger.warn('Socket for device state may already be closed', { uid: payload.uid });
            }
        } catch (error) {
            // Don't throw error for socket cleanup - just log it
            logger.warn('Error closing socket for device state', { uid: payload.uid, error: (error as Error).message });
        }
    }
}