/**
 * Validation Utilities
 * 
 * Centralized validation functions following existing codebase patterns
 */

/**
 * Email validation regex (extracted from existing UserLogin.vue pattern)
 */
export const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/**
 * Validate email format following existing patterns
 * @param {string} email - Email to validate
 * @returns {boolean} - True if valid email format
 */
export function isValidEmailFormat(email) {
    return EMAIL_REGEX.test(email);
}

/**
 * Validate @forvia domain requirement following existing patterns
 * @param {string} email - Email to validate
 * @returns {boolean} - True if contains @forvia
 */
export function isForviaEmail(email) {
    return email.toLowerCase().includes('@forvia');
}

/**
 * Comprehensive email validation following existing patterns
 * @param {string} email - Email to validate
 * @returns {Object} - Validation result object
 */
export function validateEmail(email) {
    const result = {
        isValid: true,
        errors: []
    };

    // Empty check (existing pattern)
    if (!email || email === '') {
        result.isValid = false;
        result.errors.push('Email field cannot be empty.');
        return result;
    }

    // Format validation (existing pattern)
    if (!isValidEmailFormat(email)) {
        result.isValid = false;
        result.errors.push('Please enter a valid email address.');
    }

    // Length validation (existing pattern)
    if (email.length > 254) {
        result.isValid = false;
        result.errors.push('Email address is too long.');
    }

    // Domain validation (existing pattern)
    if (!isForviaEmail(email)) {
        result.isValid = false;
        result.errors.push('Only @forvia email addresses are allowed.');
    }

    return result;
}

/**
 * Validate password following existing patterns
 * @param {string} password - Password to validate
 * @returns {Object} - Validation result object
 */
export function validatePassword(password) {
    const result = {
        isValid: true,
        errors: []
    };

    // Empty check (existing pattern)
    if (!password || password === '') {
        result.isValid = false;
        result.errors.push('Please enter your password.');
        return result;
    }

    // Length validation (existing pattern)
    if (password.length < 3) {
        result.isValid = false;
        result.errors.push('Password must be at least 3 characters long.');
    }

    if (password.length > 128) {
        result.isValid = false;
        result.errors.push('Password is too long.');
    }

    return result;
}

/**
 * Sanitize input following existing patterns
 * @param {string} input - Input to sanitize
 * @returns {string} - Sanitized input
 */
export function sanitizeInput(input) {
    return input.trim().toLowerCase();
}

/**
 * Validate form data and return first error message following existing patterns
 * @param {Object} data - Form data to validate
 * @returns {string|null} - First error message or null if valid
 */
export function getFirstValidationError(data) {
    if (data.email !== undefined) {
        const emailValidation = validateEmail(data.email);
        if (!emailValidation.isValid) {
            return emailValidation.errors[0];
        }
    }

    if (data.password !== undefined) {
        const passwordValidation = validatePassword(data.password);
        if (!passwordValidation.isValid) {
            return passwordValidation.errors[0];
        }
    }

    return null; // All valid
}