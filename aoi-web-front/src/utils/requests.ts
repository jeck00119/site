// Type definitions for HTTP requests
type Headers = Record<string, string>;

interface RequestResponse<T = any> {
    response: Response;
    responseData: T;
    ok: boolean;
    status: number;
    data?: T;
    _?: any;
    _2?: any;
    blob?: () => Promise<Blob>;
    headers?: Headers;
}

// Helper function to get Authorization header
function getAuthHeaders(): Headers {
    const token = sessionStorage.getItem('auth-token');
    return token ? { 'Authorization': token } : {};
}

// Helper function to merge headers with auth
function mergeWithAuthHeaders(headers?: Headers): Headers {
    const authHeaders = getAuthHeaders();
    const defaultHeaders = { 'content-type': 'application/json' };
    // Put custom headers last so they can override defaults and auth
    return { ...defaultHeaders, ...authHeaders, ...headers };
}

// Global 401 handler
function handle401Unauthorized(url: string) {
    // Don't handle 401 for login/auth endpoints
    if (url.includes('/auth/login') || url.includes('/auth/users') || url.includes('/auth/create_user') || url.includes('/authentication/')) {
        return false; // Let the auth flow handle these
    }
    
    console.warn('401 Unauthorized for URL:', url);
    console.warn('Token expired or invalid, logging out automatically');
    
    // Clear session immediately
    sessionStorage.removeItem('auth-token');
    sessionStorage.removeItem('user');
    sessionStorage.removeItem('expiration-date');
    sessionStorage.removeItem('level');
    
    // Force redirect to login page
    window.location.href = '/login';
    
    // Also dispatch logout action for state cleanup (non-blocking)
    import('../store/index.js').then(({ default: store }) => {
        store.dispatch('auth/logout').catch(() => {});
    }).catch(() => {});
    
    return true; // Handled
}

// Enhanced response handler with 401 check
async function handleResponse<T>(response: Response, url: string): Promise<RequestResponse<T>> {
    // Check for 401 Unauthorized
    if (response.status === 401) {
        const handled = handle401Unauthorized(url);
        if (handled) {
            // Throw error to stop further processing
            throw new Error('Unauthorized - Redirecting to login');
        }
        // For auth endpoints, let them handle the 401 themselves
    }
    
    const responseData = await response.json();
    
    return {
        response,
        responseData,
        ok: response.ok,
        status: response.status,
        data: responseData,
        _: responseData,
        _2: responseData,
        blob: () => response.blob(),
        headers: response.headers as any
    };
}

async function get<T = any>(url: string, headers?: Headers): Promise<RequestResponse<T>> {
    const mergedHeaders = mergeWithAuthHeaders(headers);

    const response = await fetch(url, {
        method: 'GET',
        headers: mergedHeaders,
        signal: AbortSignal.timeout(10000) // 10 second timeout
    });

    return handleResponse<T>(response, url);
}

async function post<T = any>(url: string, payload?: any, headers?: Headers, timeout?: number): Promise<RequestResponse<T>> {
    const mergedHeaders = mergeWithAuthHeaders(headers);

    const response = await fetch(url, {
        method: 'POST',
        headers: mergedHeaders,
        body: JSON.stringify(payload),
        signal: AbortSignal.timeout(timeout || 15000) // Custom timeout or default 15 seconds
    });

    return handleResponse<T>(response, url);
}

async function postStream<T = any>(url: string, payload?: any, headers?: Headers): Promise<RequestResponse<T>> {
    try {
        let finalHeaders = { ...getAuthHeaders() };
        let body: string | URLSearchParams | FormData;
        
        // Handle different payload types properly
        if (payload instanceof URLSearchParams) {
            body = payload;
            // For URLSearchParams, set the correct content-type
            finalHeaders['Content-Type'] = 'application/x-www-form-urlencoded';
        } else if (payload instanceof FormData) {
            body = payload;
            // For FormData, let browser set the content-type (includes boundary)
            // Don't set Content-Type header
        } else {
            body = JSON.stringify(payload);
            finalHeaders['Content-Type'] = 'application/json';
        }
        
        // Merge with provided headers (allowing override)
        if (headers) {
            finalHeaders = { ...finalHeaders, ...headers };
        }


        const response = await fetch(url, {
            method: 'POST',
            headers: finalHeaders,
            body: body,
            signal: AbortSignal.timeout(30000) // 30 second timeout for stream requests
        });

        return handleResponse<T>(response, url);
    } catch (error) {
        console.error('PostStream request failed:', error);
        throw error;
    }
}

async function update<T = any>(url: string, payload?: any, headers?: Headers): Promise<RequestResponse<T>> {
    const mergedHeaders = mergeWithAuthHeaders(headers);

    const response = await fetch(url, {
        method: 'PUT',
        headers: mergedHeaders,
        body: JSON.stringify(payload),
        signal: AbortSignal.timeout(15000) // 15 second timeout for PUT requests
    });

    return handleResponse<T>(response, url);
}

async function remove<T = any>(url: string, headers?: Headers): Promise<RequestResponse<T>> {
    const mergedHeaders = mergeWithAuthHeaders(headers);

    const response = await fetch(url, {
        method: 'DELETE',
        headers: mergedHeaders,
        signal: AbortSignal.timeout(10000) // 10 second timeout for DELETE requests
    });

    return handleResponse<T>(response, url);
}

async function patch(url: string, payload?: any, headers?: Headers): Promise<Response> {
    const mergedHeaders = mergeWithAuthHeaders(headers);

    const response = await fetch(url, {
        method: 'PATCH',
        headers: mergedHeaders,
        body: JSON.stringify(payload),
        signal: AbortSignal.timeout(15000) // 15 second timeout for PATCH requests
    });

    return response;
}

async function put(url: string, payload?: any, headers?: Headers): Promise<Response> {
    const mergedHeaders = mergeWithAuthHeaders(headers);

    const response = await fetch(url, {
        method: 'PUT',
        headers: mergedHeaders,
        body: JSON.stringify(payload)
    });

    return response;
}

async function upload_image(url: string, payload: FormData): Promise<Response> {
    // For FormData, we need to get auth headers but not set content-type (browser sets it automatically)
    const authHeaders = getAuthHeaders();
    
    const response = await fetch(url, {
        method: 'POST',
        headers: authHeaders, // Don't set content-type for FormData
        body: payload
    });
    
    return response;
}

export { get, post, update, remove, patch, put, postStream, upload_image };
export type { Headers, RequestResponse };

