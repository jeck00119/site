/**
 * Algorithm Property Validation Utilities
 * 
 * Centralized validation and sanitization for algorithm properties
 * to ensure data consistency and prevent errors.
 */

/**
 * Validate and sanitize algorithm property values
 * @param {string} key - Property name
 * @param {any} value - Property value
 * @returns {Object} - {valid: boolean, sanitizedValue: any, errorMessage: string}
 */
export function validateAlgorithmProperty(key, value) {
    try {
        // Specific validation rules for known properties
        const validators = {
            'golden_position': validateGoldenPosition,
            'graphics': validateGraphics,
            'model_path': validateModelPath,
            'confidence_threshold': validateConfidenceThreshold,
            'iou_threshold': validateIouThreshold,
            'reference_point_idx': validateReferencePointIdx,
        };

        const validator = validators[key] || validateGenericProperty;
        return validator(value);

    } catch (error) {
        return {
            valid: false,
            sanitizedValue: null,
            errorMessage: `Validation error for property '${key}': ${error.message}`
        };
    }
}

/**
 * Validate golden_position property
 */
function validateGoldenPosition(value) {
    // Must be an array of exactly 2 numeric values
    if (!Array.isArray(value) && !isArrayLike(value)) {
        return {
            valid: false,
            sanitizedValue: null,
            errorMessage: `golden_position must be an array, got ${typeof value}`
        };
    }

    // Convert array-like to array
    const arrayValue = Array.isArray(value) ? value : Array.from(value);

    if (arrayValue.length !== 2) {
        return {
            valid: false,
            sanitizedValue: null,
            errorMessage: `golden_position must have exactly 2 values, got ${arrayValue.length}`
        };
    }

    // Validate and convert to numbers
    try {
        const sanitized = arrayValue.map(val => {
            const num = Number(val);
            if (!isFinite(num)) {
                throw new Error(`Invalid numeric value: ${val}`);
            }
            return num;
        });

        return {
            valid: true,
            sanitizedValue: sanitized,
            errorMessage: null
        };
    } catch (error) {
        return {
            valid: false,
            sanitizedValue: null,
            errorMessage: `golden_position values must be numeric: ${error.message}`
        };
    }
}

/**
 * Validate graphics property
 */
function validateGraphics(value) {
    if (!Array.isArray(value)) {
        return {
            valid: false,
            sanitizedValue: null,
            errorMessage: `graphics must be an array, got ${typeof value}`
        };
    }

    // Validate each graphic object
    for (let i = 0; i < value.length; i++) {
        if (typeof value[i] !== 'object' || value[i] === null) {
            return {
                valid: false,
                sanitizedValue: null,
                errorMessage: `graphics[${i}] must be an object, got ${typeof value[i]}`
            };
        }
    }

    return {
        valid: true,
        sanitizedValue: value,
        errorMessage: null
    };
}

/**
 * Validate model_path property
 */
function validateModelPath(value) {
    if (typeof value !== 'string') {
        return {
            valid: false,
            sanitizedValue: null,
            errorMessage: `model_path must be a string, got ${typeof value}`
        };
    }

    // Basic sanitization - remove dangerous characters
    const sanitized = value.replace(/[<>"|*?]/g, '').trim();

    return {
        valid: true,
        sanitizedValue: sanitized,
        errorMessage: null
    };
}

/**
 * Validate confidence_threshold property
 */
function validateConfidenceThreshold(value) {
    const num = Number(value);
    
    if (!isFinite(num)) {
        return {
            valid: false,
            sanitizedValue: null,
            errorMessage: 'confidence_threshold must be a number'
        };
    }

    if (num < 0.0 || num > 1.0) {
        return {
            valid: false,
            sanitizedValue: null,
            errorMessage: 'confidence_threshold must be between 0.0 and 1.0'
        };
    }

    return {
        valid: true,
        sanitizedValue: num,
        errorMessage: null
    };
}

/**
 * Validate iou_threshold property
 */
function validateIouThreshold(value) {
    const num = Number(value);
    
    if (!isFinite(num)) {
        return {
            valid: false,
            sanitizedValue: null,
            errorMessage: 'iou_threshold must be a number'
        };
    }

    if (num < 0.0 || num > 1.0) {
        return {
            valid: false,
            sanitizedValue: null,
            errorMessage: 'iou_threshold must be between 0.0 and 1.0'
        };
    }

    return {
        valid: true,
        sanitizedValue: num,
        errorMessage: null
    };
}

/**
 * Validate reference_point_idx property
 */
function validateReferencePointIdx(value) {
    const num = Number(value);
    
    if (!Number.isInteger(num)) {
        return {
            valid: false,
            sanitizedValue: null,
            errorMessage: 'reference_point_idx must be an integer'
        };
    }

    if (num < 0) {
        return {
            valid: false,
            sanitizedValue: null,
            errorMessage: 'reference_point_idx must be non-negative'
        };
    }

    return {
        valid: true,
        sanitizedValue: num,
        errorMessage: null
    };
}

/**
 * Generic validation for unknown properties
 */
function validateGenericProperty(value) {
    // Basic security check for strings
    if (typeof value === 'string') {
        // Check for potentially dangerous content
        const dangerousPatterns = [
            /<script/i,
            /javascript:/i,
            /on\w+\s*=/i,
            /eval\s*\(/i,
        ];

        for (const pattern of dangerousPatterns) {
            if (pattern.test(value)) {
                return {
                    valid: false,
                    sanitizedValue: null,
                    errorMessage: 'Property contains potentially dangerous content'
                };
            }
        }

        // Basic HTML escaping for strings
        const sanitized = value
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#x27;');

        return {
            valid: true,
            sanitizedValue: sanitized,
            errorMessage: null
        };
    }

    // For non-string values, just pass through
    return {
        valid: true,
        sanitizedValue: value,
        errorMessage: null
    };
}

/**
 * Check if value is array-like (has length property and numeric indices)
 */
function isArrayLike(value) {
    return value != null && 
           typeof value === 'object' && 
           typeof value.length === 'number' && 
           value.length >= 0;
}

/**
 * Pre-validate algorithm property before sending to backend
 * This is a convenience function that logs validation errors
 */
export function preValidateAlgorithmProperty(key, value) {
    const result = validateAlgorithmProperty(key, value);
    
    if (!result.valid) {
        console.warn(`Frontend validation failed for property '${key}':`, result.errorMessage, {
            key,
            value,
            valueType: typeof value
        });
    }
    
    return result;
}

/**
 * Sanitize algorithm property value without strict validation
 * Use this when you want to clean data but still allow it through
 */
export function sanitizeAlgorithmProperty(key, value) {
    const result = validateAlgorithmProperty(key, value);
    return result.sanitizedValue !== null ? result.sanitizedValue : value;
}