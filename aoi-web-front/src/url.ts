const ipAddress: string = import.meta.env.VITE_API_BACKEND_IP || "localhost";

// Always use port 8000 for backend - no discovery needed
const port: string = "8000";

// Function to get the current port (always returns 8000)
function getPort(): Promise<string> {
    return Promise.resolve(port);
}

// Legacy function for backward compatibility
function discoverBackendPort(): Promise<string> {
    return Promise.resolve(port);
}

export { ipAddress, port, getPort, discoverBackendPort };
