/**
 * Centralized Error Handling Utility
 * 
 * Provides consistent error processing following existing codebase patterns
 */

import { uuid } from "vue3-uuid";

/**
 * Extract error message from API response following existing patterns
 * @param {Object} responseData - API response data
 * @param {Response} response - Fetch response object
 * @param {string} fallbackMessage - Default message if no specific error found
 * @returns {string} - Extracted or fallback error message
 */
export function extractErrorMessage(responseData, response, fallbackMessage = "Something went wrong. Please try again.") {
    // Follow existing pattern: try responseData.detail first, then fallback
    if (responseData?.detail) {
        return responseData.detail;
    }
    
    // If no detail, use fallback message
    return fallbackMessage;
}

/**
 * Create standardized error object following existing patterns
 * @param {Object} responseData - API response data  
 * @param {Response} response - Fetch response object
 * @param {string} operation - Description of operation that failed
 * @returns {Error} - Standardized error object
 */
export function createStandardError(responseData, response, operation = "Operation") {
    const message = extractErrorMessage(responseData, response, `${operation} failed!`);
    const error = new Error(message);
    error.statusCode = response?.status;
    return error;
}

/**
 * Add error to centralized error store following existing patterns
 * @param {Object} store - Vuex store instance
 * @param {string} title - Error title
 * @param {string|Error} error - Error message or Error object
 */
export function addErrorToStore(store, title, error) {
    const errorMessage = error instanceof Error ? error.message : error;
    
    store.dispatch("errors/addError", {
        id: uuid.v4(),
        title: title,
        description: errorMessage
    });
}

/**
 * Handle API response errors following existing codebase patterns
 * @param {Object} response - Fetch response object
 * @param {Object} responseData - Parsed response data
 * @param {string} operation - Operation description for error messages
 * @throws {Error} - Throws standardized error if response is not ok
 */
export function handleApiError(response, responseData, operation = "Operation") {
    if (!response || !response.ok) {
        throw createStandardError(responseData, response, operation);
    }
}

/**
 * Authentication-specific error messages based on existing patterns
 * @param {Object} responseData - API response data
 * @param {Response} response - Fetch response object
 * @returns {string} - Authentication-specific error message
 */
export function getAuthErrorMessage(responseData, response) {
    // Use backend's detail message if available (existing pattern)
    if (responseData?.detail) {
        return responseData.detail;
    }
    
    // Fallback for authentication errors
    return "Failed to login! Please check your credentials.";
}