let ipAddress = import.meta.env.VITE_API_BACKEND_IP || "localhost";

// Dynamic port discovery - check multiple ports where backend might be running
const POSSIBLE_PORTS = ["8000", "8001", "8002", "8003", "8004"];
let discoveredPort = null;

// Function to test if a port is responding
async function testPort(port) {
    try {
        const response = await fetch(`http://${ipAddress}:${port}/health`, {
            method: 'GET',
            signal: AbortSignal.timeout(2000) // 2 second timeout
        });
        return response.ok;
    } catch (error) {
        return false;
    }
}

// Function to discover the active backend port
async function discoverBackendPort() {
    if (discoveredPort) {
        return discoveredPort;
    }

    // Try ports in parallel for faster discovery
    const portTests = POSSIBLE_PORTS.map(async (port) => {
        const isActive = await testPort(port);
        return isActive ? port : null;
    });

    const results = await Promise.all(portTests);
    discoveredPort = results.find(port => port !== null) || "8000"; // fallback to 8000
    
    // Backend discovered on port: ${discoveredPort}
    return discoveredPort;
}

// Get the current port (with discovery)
async function getPort() {
    return await discoverBackendPort();
}

// Legacy sync export for backward compatibility
let port = "8000"; // Default fallback

// Initialize port discovery
discoverBackendPort().then(foundPort => {
    port = foundPort;
}).catch(() => {
    // Could not discover backend port, using default 8000
});

export { ipAddress, port, getPort, discoverBackendPort };
