/**
 * Centralized Error Handling Utility
 * 
 * Provides consistent error processing following existing codebase patterns
 */

import { v4 as uuidv4 } from "uuid";
import type { Store } from "vuex";

interface ErrorDetails {
    detail?: string;
    message?: string;
    [key: string]: any;
}

interface ApiResponse {
    ok: boolean;
    status: number;
    statusText: string;
}

interface ErrorObject {
    id: string;
    title: string;
    description: string;
}

/**
 * Extract error message from API response following existing patterns
 * @param responseData - API response data
 * @param response - Fetch response object
 * @param fallbackMessage - Default message if no specific error found
 * @returns Extracted or fallback error message
 */
export function extractErrorMessage(
    responseData: ErrorDetails | null,
    response: ApiResponse | null,
    fallbackMessage: string = "Something went wrong. Please try again."
): string {
    // Follow existing pattern: try responseData.detail first, then fallback
    if (responseData?.detail) {
        return responseData.detail;
    }
    
    // Try message field as backup
    if (responseData?.message) {
        return responseData.message;
    }
    
    // If no detail, use fallback message
    return fallbackMessage;
}

/**
 * Create standardized error object following existing patterns
 * @param responseData - API response data  
 * @param response - Fetch response object
 * @param operation - Description of operation that failed
 * @returns Standardized error object
 */
export function createStandardError(
    responseData: ErrorDetails | null,
    response: ApiResponse | null,
    operation: string = "Operation"
): Error {
    const message = extractErrorMessage(responseData, response, `${operation} failed!`);
    const error = new Error(message);
    
    // Add status code if available
    if (response?.status) {
        (error as any).statusCode = response.status;
    }
    
    return error;
}

/**
 * Add error to centralized error store following existing patterns
 * @param store - Vuex store instance
 * @param title - Error title
 * @param error - Error message or Error object
 * @param type - Error type (error, warning, info)
 */
export function addErrorToStore(
    store: Store<any>,
    title: string,
    error: string | Error,
    type: 'error' | 'warning' | 'info' = 'error'
): void {
    const errorMessage = error instanceof Error ? error.message : error;
    const fullMessage = title ? `${title}: ${errorMessage}` : errorMessage;
    
    store.dispatch("errors/addError", {
        id: uuidv4(),
        message: fullMessage,
        type: type,
        timestamp: Date.now(),
        details: error instanceof Error ? { 
            name: error.name, 
            stack: error.stack,
            statusCode: (error as any).statusCode 
        } : { originalTitle: title }
    });
}

/**
 * Handle API response errors following existing codebase patterns
 * @param response - Fetch response object
 * @param responseData - Parsed response data
 * @param operation - Operation description for error messages
 * @throws Throws standardized error if response is not ok
 */
export function handleApiError(
    response: ApiResponse | null,
    responseData: ErrorDetails | null,
    operation: string = "Operation"
): void {
    if (!response || !response.ok) {
        throw createStandardError(responseData, response, operation);
    }
}

/**
 * Authentication-specific error messages based on existing patterns
 * @param responseData - API response data
 * @param response - Fetch response object
 * @returns Authentication-specific error message
 */
export function getAuthErrorMessage(
    responseData: ErrorDetails | null,
    response: ApiResponse | null
): string {
    // Use backend's detail message if available (existing pattern)
    if (responseData?.detail) {
        return responseData.detail;
    }
    
    // Fallback for authentication errors
    return "Failed to login! Please check your credentials.";
}

/**
 * Network-specific error handler
 * @param error - Network error
 * @param operation - Operation that failed
 * @returns User-friendly error message
 */
export function handleNetworkError(error: any, operation: string = "Operation"): string {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
        return `Network error: Unable to connect to server during ${operation.toLowerCase()}`;
    }
    
    if (error.code === 'ECONNREFUSED') {
        return `Connection refused: Server is not responding during ${operation.toLowerCase()}`;
    }
    
    return `Network error occurred during ${operation.toLowerCase()}`;
}

/**
 * Validation error formatter
 * @param validationErrors - Array of validation error messages
 * @param fieldName - Field name that failed validation
 * @returns Formatted error message
 */
export function formatValidationError(
    validationErrors: string[],
    fieldName?: string
): string {
    if (validationErrors.length === 0) {
        return '';
    }
    
    if (validationErrors.length === 1) {
        return validationErrors[0];
    }
    
    const prefix = fieldName ? `${fieldName}: ` : '';
    return `${prefix}${validationErrors.join(', ')}`;
}

export default {
    extractErrorMessage,
    createStandardError,
    addErrorToStore,
    handleApiError,
    getAuthErrorMessage,
    handleNetworkError,
    formatValidationError
};