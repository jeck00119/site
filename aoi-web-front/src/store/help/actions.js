import { get } from "../../utils/requests";
import { ipAddress, port } from "../../url.js";

export default {
    async loadHelpDocument(context) {
        const { response, responseData } = await get(`http://${ipAddress}:${port}/help`);

        if(!response.ok)
        {
            const error = new Error(`Failed to load help document!`);
            throw error;
        }
        else
        {
            context.commit('setHelpDocument', responseData);
        }
    },

    setHelpDocument(context, payload) {
        context.commit('setHelpDocument', payload);
    }
}