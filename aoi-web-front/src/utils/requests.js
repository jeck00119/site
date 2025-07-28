async function get(url, headers){
    headers = headers ? headers : {
        'content-type': 'application/json'
    };

    const response = await fetch(url, {
        method: 'GET',
        headers: headers
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
        body: JSON.stringify(payload)
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

    const response = await fetch(url, {
        method: 'POST',
        headers: headers,
        body: payload
    });

    return response;
}

async function update(url, payload, headers){
    headers = headers ? headers : {
        'content-type': 'application/json'
    };

    const response = await fetch(url, {
        method: 'PUT',
        headers: headers,
        body: JSON.stringify(payload)
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
        headers: headers
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
        body: JSON.stringify(payload)
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
