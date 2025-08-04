let ipAddress = import.meta.env.VITE_API_BACKEND_IP || "localhost";

// Always use port 8000 for backend - no discovery needed
const port = "8000";

// Function to get the current port (always returns 8000)
function getPort() {
    return port;
}

// Legacy function for backward compatibility
function discoverBackendPort() {
    return Promise.resolve(port);
}

export { ipAddress, port, getPort, discoverBackendPort };
