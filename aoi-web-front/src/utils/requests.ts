// Type definitions for HTTP requests
type Headers = Record<string, string>;

interface RequestResponse<T = any> {
    response: Response;
    responseData: T;
}

async function get<T = any>(url: string, headers?: Headers): Promise<RequestResponse<T>> {
    headers = headers ? headers : {
        'content-type': 'application/json'
    };

    const response = await fetch(url, {
        method: 'GET',
        headers: headers,
        signal: AbortSignal.timeout(10000) // 10 second timeout
    });

    const responseData = await response.json();

    return {
        response,
        responseData
    }
}

async function post<T = any>(url: string, payload?: any, headers?: Headers): Promise<RequestResponse<T>> {
    headers = headers ? headers : {
        'content-type': 'application/json'
    };

    const response = await fetch(url, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(payload),
        signal: AbortSignal.timeout(15000) // 15 second timeout for POST requests
    });

    const responseData = await response.json();

    return {
        response,
        responseData
    };
}

async function postStream<T = any>(url: string, payload?: any, headers?: Headers): Promise<RequestResponse<T>> {
    try {
        headers = headers ? headers : {
            'content-type': 'application/json'
        };

        // Handle different payload types properly
        let body: string | URLSearchParams | FormData;
        if (payload instanceof URLSearchParams || payload instanceof FormData) {
            body = payload;
        } else {
            body = JSON.stringify(payload);
        }

        const response = await fetch(url, {
            method: 'POST',
            headers: headers,
            body: body,
            signal: AbortSignal.timeout(30000) // 30 second timeout for stream requests
        });

        const responseData = await response.json();

        return {
            response,
            responseData
        };
    } catch (error) {
        console.error('PostStream request failed:', error);
        throw error;
    }
}

async function update<T = any>(url: string, payload?: any, headers?: Headers): Promise<RequestResponse<T>> {
    headers = headers ? headers : {
        'content-type': 'application/json'
    };

    const response = await fetch(url, {
        method: 'PUT',
        headers: headers,
        body: JSON.stringify(payload),
        signal: AbortSignal.timeout(15000) // 15 second timeout for PUT requests
    });

    const responseData = await response.json();

    return {
        response,
        responseData
    };
}

async function remove<T = any>(url: string, headers?: Headers): Promise<RequestResponse<T>> {
    headers = headers ? headers : {
        'content-type': 'application/json'
    };

    const response = await fetch(url, {
        method: 'DELETE',
        headers: headers,
        signal: AbortSignal.timeout(10000) // 10 second timeout for DELETE requests
    });

    const responseData = await response.json();

    return {
        response,
        responseData
    };
}

async function patch(url: string, payload?: any, headers?: Headers): Promise<Response> {
    headers = headers ? headers : {
        'content-type': 'application/json'
    };

    const response = await fetch(url, {
        method: 'PATCH',
        headers: headers,
        body: JSON.stringify(payload),
        signal: AbortSignal.timeout(15000) // 15 second timeout for PATCH requests
    });

    return response;
}

async function put(url: string, payload?: any, headers?: Headers): Promise<Response> {
    headers = headers ? headers : {
        'content-type': 'application/json'
    };

    const response = await fetch(url, {
        method: 'PUT',
        headers: headers,
        body: JSON.stringify(payload)
    });

    return response;
}

async function upload_image(url: string, payload: FormData): Promise<Response> {
    const response = await fetch(url, {
        method: 'POST',
        // headers: {
        //     'content-type': 'multipart/form-data; boundary=-----------------------------42216892372008170244666382721'
        // },
        body: payload
    });
    
    return response;
}

export { get, post, update, remove, patch, put, postStream, upload_image };
export type { Headers, RequestResponse };

