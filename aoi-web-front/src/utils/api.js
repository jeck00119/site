import { ipAddress, getPort } from '../url.js';
import { get, post, update, remove, patch, put, postStream, upload_image } from './requests.js';

/**
 * Enhanced API utility that automatically discovers backend port
 */

// Build URL with dynamic port discovery
async function buildApiUrl(endpoint) {
    const port = await getPort();
    const baseUrl = `http://${ipAddress}:${port}`;
    return endpoint.startsWith('/') ? `${baseUrl}${endpoint}` : `${baseUrl}/${endpoint}`;
}

// Enhanced API methods with automatic port discovery
export const api = {
    async get(endpoint, headers) {
        const url = await buildApiUrl(endpoint);
        return get(url, headers);
    },

    async post(endpoint, payload, headers) {
        const url = await buildApiUrl(endpoint);
        return post(url, payload, headers);
    },

    async put(endpoint, payload, headers) {
        const url = await buildApiUrl(endpoint);
        return put(url, payload, headers);
    },

    async update(endpoint, payload, headers) {
        const url = await buildApiUrl(endpoint);
        return update(url, payload, headers);
    },

    async delete(endpoint, headers) {
        const url = await buildApiUrl(endpoint);
        return remove(url, headers);
    },

    async patch(endpoint, payload, headers) {
        const url = await buildApiUrl(endpoint);
        return patch(url, payload, headers);
    },

    async postStream(endpoint, payload, headers) {
        const url = await buildApiUrl(endpoint);
        return postStream(url, payload, headers);
    },

    async uploadImage(endpoint, payload) {
        const url = await buildApiUrl(endpoint);
        return upload_image(url, payload);
    },

    // Helper method to get full URL for cases like WebSocket connections
    async getFullUrl(endpoint) {
        return await buildApiUrl(endpoint);
    }
};

// Backward compatibility - create URLs with the old pattern
export async function createApiUrl(endpoint) {
    return await buildApiUrl(endpoint);
}

export default api;