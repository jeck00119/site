import { ipAddress, getPort } from '../url.ts';
import { get, post, update, remove, patch, put, postStream, upload_image } from './requests.ts';
import type { ApiResponse } from '../types/api';

/**
 * Enhanced API utility that automatically discovers backend port
 */

// Build URL with dynamic port discovery
async function buildApiUrl(endpoint: string): Promise<string> {
    const port = await getPort();
    const baseUrl = `http://${ipAddress}:${port}`;
    return endpoint.startsWith('/') ? `${baseUrl}${endpoint}` : `${baseUrl}/${endpoint}`;
}

// Type for HTTP headers
type Headers = Record<string, string>;

// Helper function to normalize response format
async function normalizeResponse<T>(responsePromise: Promise<any>): Promise<ApiResponse<T>> {
    const result = await responsePromise;
    
    // If result has response and responseData properties, it's already in the correct format
    if (result && typeof result === 'object' && 'response' in result && 'responseData' in result) {
        return result as ApiResponse<T>;
    }
    
    // If result is a Response object, we need to extract the data
    if (result instanceof Response) {
        const responseData = await result.json();
        return {
            response: result,
            responseData
        } as ApiResponse<T>;
    }
    
    // Fallback - shouldn't happen but just in case
    return result as ApiResponse<T>;
}

// Enhanced API methods with automatic port discovery and TypeScript support
export const api = {
    async get<T = any>(endpoint: string, headers?: Headers): Promise<ApiResponse<T>> {
        const url = await buildApiUrl(endpoint);
        return normalizeResponse<T>(get(url, headers));
    },

    async post<T = any>(endpoint: string, payload?: any, headers?: Headers): Promise<ApiResponse<T>> {
        const url = await buildApiUrl(endpoint);
        return normalizeResponse<T>(post(url, payload, headers));
    },

    async put<T = any>(endpoint: string, payload?: any, headers?: Headers): Promise<ApiResponse<T>> {
        const url = await buildApiUrl(endpoint);
        return normalizeResponse<T>(put(url, payload, headers));
    },

    async update<T = any>(endpoint: string, payload?: any, headers?: Headers): Promise<ApiResponse<T>> {
        const url = await buildApiUrl(endpoint);
        return normalizeResponse<T>(update(url, payload, headers));
    },

    async delete<T = any>(endpoint: string, headers?: Headers): Promise<ApiResponse<T>> {
        const url = await buildApiUrl(endpoint);
        return normalizeResponse<T>(remove(url, headers));
    },

    async patch<T = any>(endpoint: string, payload?: any, headers?: Headers): Promise<ApiResponse<T>> {
        const url = await buildApiUrl(endpoint);
        return normalizeResponse<T>(patch(url, payload, headers));
    },

    async postStream<T = any>(endpoint: string, payload?: any, headers?: Headers): Promise<ApiResponse<T>> {
        const url = await buildApiUrl(endpoint);
        return normalizeResponse<T>(postStream(url, payload, headers));
    },

    async uploadImage<T = any>(endpoint: string, payload: FormData): Promise<ApiResponse<T>> {
        const url = await buildApiUrl(endpoint);
        return normalizeResponse<T>(upload_image(url, payload));
    },

    // Helper method to get full URL for cases like WebSocket connections
    async getFullUrl(endpoint: string): Promise<string> {
        return await buildApiUrl(endpoint);
    }
};

// Backward compatibility - create URLs with the old pattern
export async function createApiUrl(endpoint: string): Promise<string> {
    return await buildApiUrl(endpoint);
}

export default api;

