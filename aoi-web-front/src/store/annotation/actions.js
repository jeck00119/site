import { get, post, postStream } from "../../utils/requests";
import { ipAddress, port } from "../../url.js";

export default {
    async loadAvailableModels(context) {
        const { response, responseData } = await get(`http://${ipAddress}:${port}/annotation/models`);

        if(!response.ok)
        {
            const error = new Error(`Failed to load models!`);
            throw error;
        }
        else
        {
            context.commit('setModels', responseData);
        }
    },

    addModel(context, payload) {
        context.commit('addModel', payload);
    },

    async annotate(context, payload) {
        const token = context.rootGetters["auth/getToken"];

        const response = await postStream(`http://${ipAddress}:${port}/annotation/annotate`, payload, {
            'Authorization': token
        });

        console.log(response);

        if(!response.ok)
        {
            const error = new Error(`Failed to download files!`);
            throw error;
        }

        // Read the response as a blob
        const blob = await response.blob();

        // Extract filename from Content-Disposition header
        let filename = 'output.zip'; // Default filename
        const disposition = response.headers.get('Content-Disposition');
        if (disposition && disposition.indexOf('attachment') !== -1) {
            const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
            const matches = filenameRegex.exec(disposition);
            if (matches != null && matches[1]) { 
                filename = matches[1].replace(/['"]/g, '');
            }
        }

        // Create a temporary link to trigger the download
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;

        // Append to the DOM and trigger click
        document.body.appendChild(link);
        link.click();

        // Clean up
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    },

    async uploadModel(_, payload) {
        const response = await postStream(`http://${ipAddress}:${port}/annotation/upload_model`,
            payload, {}
        );

        if(!response.ok)
        {
            const error = new Error("Failed to load model!");
            throw error;
        }
    }
}