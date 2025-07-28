async function get(url, headers){
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

async function post(url, payload, headers){
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

async function postStream(url, payload, headers){
    headers = headers ? headers : {
        'Content-Type': 'multipart/form-data'
    };

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: headers,
            body: payload,
            signal: AbortSignal.timeout(30000) // 30 second timeout for file uploads
        });

        let responseData = null;
        try {
            responseData = await response.json();
        } catch (e) {
            // If response is not JSON, that's okay for some endpoints
            responseData = null;
        }

        return {
            response,
            responseData
        };
    } catch (error) {
        console.error('PostStream request failed:', error);
        throw error;
    }
}

async function update(url, payload, headers){
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

async function remove(url, headers){
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

async function patch(url, payload, headers){
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

async function put(url, payload, headers){
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

async function upload_image(url, payload){
    const response = await fetch(url, {
        method: 'POST',
        // headers: {
        //     'content-type': 'multipart/form-data; boundary=-----------------------------42216892372008170244666382721'
        // },
        body: payload
    });
    
    return response;
}

export {get, post, update, remove, patch, put, postStream, upload_image}
