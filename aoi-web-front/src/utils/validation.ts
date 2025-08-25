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
 * Validation result interface
 */
export interface ValidationResult {
    isValid: boolean;
    errors: string[];
}

/**
 * Form data interface for validation
 */
export interface FormData {
    email?: string;
    password?: string;
    [key: string]: any;
}

/**
 * Validate email format following existing patterns
 */
export function isValidEmailFormat(email: string): boolean {
    return EMAIL_REGEX.test(email);
}

/**
 * Validate @forvia domain requirement following existing patterns
 */
export function isForviaEmail(email: string): boolean {
    return email.toLowerCase().includes('@forvia');
}

/**
 * Comprehensive email validation following existing patterns
 */
export function validateEmail(email: string): ValidationResult {
    const result: ValidationResult = {
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
 */
export function validatePassword(password: string): ValidationResult {
    const result: ValidationResult = {
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
 */
export function sanitizeInput(input: string | null | undefined): string {
    if (!input || typeof input !== 'string') return '';
    return input.trim();
}

/**
 * Validate required field
 */
export function validateRequired(value: any, fieldName: string): ValidationResult {
    const result: ValidationResult = {
        isValid: true,
        errors: []
    };

    if (value === null || value === undefined || value === '' || 
        (Array.isArray(value) && value.length === 0) ||
        (typeof value === 'object' && Object.keys(value).length === 0)) {
        result.isValid = false;
        result.errors.push(`${fieldName} is required.`);
    }

    return result;
}

/**
 * Validate field length
 */
export function validateLength(
    value: string | null | undefined, 
    min: number | undefined, 
    max: number | undefined, 
    fieldName: string
): ValidationResult {
    const result: ValidationResult = {
        isValid: true,
        errors: []
    };

    if (value && typeof value === 'string') {
        if (min !== undefined && value.length < min) {
            result.isValid = false;
            result.errors.push(`${fieldName} must be at least ${min} characters long.`);
        }
        
        if (max !== undefined && value.length > max) {
            result.isValid = false;
            result.errors.push(`${fieldName} must not exceed ${max} characters.`);
        }
    }

    return result;
}

/**
 * Validate number within range
 */
export function validateNumber(
    value: any, 
    min: number | undefined, 
    max: number | undefined, 
    fieldName: string
): ValidationResult {
    const result: ValidationResult = {
        isValid: true,
        errors: []
    };

    const numValue = Number(value);
    
    if (value !== '' && value !== null && value !== undefined) {
        if (isNaN(numValue)) {
            result.isValid = false;
            result.errors.push(`${fieldName} must be a valid number.`);
            return result;
        }

        if (min !== undefined && numValue < min) {
            result.isValid = false;
            result.errors.push(`${fieldName} must be at least ${min}.`);
        }
        
        if (max !== undefined && numValue > max) {
            result.isValid = false;
            result.errors.push(`${fieldName} must not exceed ${max}.`);
        }
    }

    return result;
}

/**
 * Validate IP address format
 */
export function validateIP(ip: string): ValidationResult {
    const result: ValidationResult = {
        isValid: true,
        errors: []
    };

    const ipRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    
    if (ip && !ipRegex.test(ip)) {
        result.isValid = false;
        result.errors.push('Please enter a valid IP address.');
    }

    return result;
}

/**
 * Validate port number
 */
export function validatePort(port: any): ValidationResult {
    const result: ValidationResult = {
        isValid: true,
        errors: []
    };

    const portNum = Number(port);
    
    if (port !== '' && port !== null && port !== undefined) {
        if (isNaN(portNum) || portNum < 1 || portNum > 65535 || !Number.isInteger(portNum)) {
            result.isValid = false;
            result.errors.push('Port must be a number between 1 and 65535.');
        }
    }

    return result;
}

/**
 * Validate file extension
 */
export function validateFileExtension(filename: string, allowedExtensions: string[]): ValidationResult {
    const result: ValidationResult = {
        isValid: true,
        errors: []
    };

    if (filename) {
        const extension = filename.toLowerCase().split('.').pop();
        const normalizedExtensions = allowedExtensions.map(ext => ext.toLowerCase().replace('.', ''));
        
        if (extension && !normalizedExtensions.includes(extension)) {
            result.isValid = false;
            result.errors.push(`File must have one of the following extensions: ${allowedExtensions.join(', ')}`);
        }
    }

    return result;
}

/**
 * Precision Utilities for CNC coordinates
 */
export function formatPrecision(value: number): number {
    return parseFloat(value.toFixed(2));
}

export function formatCoordinate(value: number): string {
    return value.toFixed(2);
}

export interface Position {
    x: number;
    y: number;
    z: number;
}

export function formatPosition(position: Position): Position {
    return {
        x: formatPrecision(position.x),
        y: formatPrecision(position.y),
        z: formatPrecision(position.z)
    };
}

/**
 * CNC Working Zone Utilities
 */
export interface CncConfig {
    selectedAxes?: {
        x?: boolean;
        y?: boolean;
        z?: boolean;
    };
    workingZoneX?: number;
    workingZoneY?: number;
    workingZoneZ?: number;
    xAxisLength?: number;
    yAxisLength?: number;
    zAxisLength?: number;
}

export interface WorkingZoneBounds {
    x: number;
    y: number;
    z: number;
}

export function getWorkingZoneBounds(cncConfig: CncConfig | null | undefined, isTopView: boolean = false): WorkingZoneBounds {
    if (!cncConfig) {
        return { x: 0, y: 0, z: 0 };
    }

    // Always return the actual physical working zone bounds
    // Coordinate swapping is now handled at the click intersection level
    const workingX = cncConfig.selectedAxes?.x === true ? (cncConfig.workingZoneX || 0) : 0;
    const workingY = cncConfig.selectedAxes?.y === true ? (cncConfig.workingZoneY || 0) : 0;
    const workingZ = cncConfig.selectedAxes?.z === true ? (cncConfig.workingZoneZ || 0) : 0;

    return { x: workingX, y: workingY, z: workingZ };
}

export function isWithinWorkingZone(position: Position, cncConfig: CncConfig | null | undefined, isTopView: boolean = false, tolerance: number = 0.5): boolean {
    if (!cncConfig) {
        return true; // Allow movement when config is not available
    }

    const bounds = getWorkingZoneBounds(cncConfig, isTopView);
    let isValid = true;

    if (cncConfig.selectedAxes?.x === true) {
        const xValid = position.x >= -tolerance && position.x <= (bounds.x + tolerance);
        if (!xValid) isValid = false;
    }

    if (cncConfig.selectedAxes?.y === true) {
        const yValid = position.y >= -tolerance && position.y <= (bounds.y + tolerance);
        if (!yValid) isValid = false;
    }

    if (cncConfig.selectedAxes?.z === true) {
        const zValid = position.z >= -tolerance && position.z <= (bounds.z + tolerance);
        if (!zValid) isValid = false;
    }

    return isValid;
}

/**
 * CNC Movement Utilities
 */
export interface MovementCallbacks {
    onMoveTo?: (position: Position) => void;
    onTargetUpdate?: (position: Position | null) => void;
    onSimulateMoveTo?: (position: Position) => void;
}

export function setTargetForRealMovement(
    position: Position,
    callbacks: MovementCallbacks,
    targetPositionRef: { value: Position | null },
    targetArrivedRef: { value: boolean },
    logger: any
): void {
    const formattedPosition = formatPosition(position);
    
    targetPositionRef.value = formattedPosition;
    targetArrivedRef.value = false;
    
    if (callbacks.onMoveTo) {
        callbacks.onMoveTo(formattedPosition);
    }
    
    if (callbacks.onTargetUpdate) {
        callbacks.onTargetUpdate(formattedPosition);
    }
    
    logger.info(`Click-to-move: Target position (${formatCoordinate(formattedPosition.x)}, ${formatCoordinate(formattedPosition.y)}, ${formatCoordinate(formattedPosition.z)})`);
}

/**
 * Validate form data and return first error message following existing patterns
 */
export function getFirstValidationError(data: FormData): string | null {
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

/**
 * 3D CNC Configuration Validation
 */
export interface CncConfig3DValidation {
    isValid: boolean;
    errors: string[];
    missingFields: string[];
}

export function validateCnc3DConfig(config: CncConfig | null | undefined): CncConfig3DValidation {
    const result: CncConfig3DValidation = {
        isValid: true,
        errors: [],
        missingFields: []
    };

    if (!config) {
        result.isValid = false;
        result.errors.push('CNC configuration is missing.');
        result.missingFields.push('entire configuration');
        return result;
    }

    // Check if at least one axis is selected first
    const selectedAxes = config.selectedAxes;
    if (!selectedAxes || (!selectedAxes.x && !selectedAxes.y && !selectedAxes.z)) {
        result.isValid = false;
        result.errors.push('At least one axis must be selected.');
        result.missingFields.push('selectedAxes');
        return result; // Early return if no axes selected
    }

    // Check required axis lengths (must be > 0) - only for selected axes
    if (selectedAxes.x) {
        if (!config.xAxisLength || config.xAxisLength <= 0) {
            result.isValid = false;
            result.errors.push('X-Axis Length must be greater than 0.');
            result.missingFields.push('xAxisLength');
        }
        if (!config.workingZoneX || config.workingZoneX <= 0) {
            result.isValid = false;
            result.errors.push('Working Zone X must be greater than 0.');
            result.missingFields.push('workingZoneX');
        }
    }

    if (selectedAxes.y) {
        if (!config.yAxisLength || config.yAxisLength <= 0) {
            result.isValid = false;
            result.errors.push('Y-Axis Length must be greater than 0.');
            result.missingFields.push('yAxisLength');
        }
        if (!config.workingZoneY || config.workingZoneY <= 0) {
            result.isValid = false;
            result.errors.push('Working Zone Y must be greater than 0.');
            result.missingFields.push('workingZoneY');
        }
    }

    if (selectedAxes.z) {
        if (!config.zAxisLength || config.zAxisLength <= 0) {
            result.isValid = false;
            result.errors.push('Z-Axis Length must be greater than 0.');
            result.missingFields.push('zAxisLength');
        }
        if (!config.workingZoneZ || config.workingZoneZ <= 0) {
            result.isValid = false;
            result.errors.push('Working Zone Z must be greater than 0.');
            result.missingFields.push('workingZoneZ');
        }
    }

    // Validate working zone doesn't exceed axis length - only for selected axes
    if (selectedAxes.x && config.workingZoneX && config.xAxisLength && config.workingZoneX > config.xAxisLength) {
        result.isValid = false;
        result.errors.push('Working Zone X cannot exceed X-Axis Length.');
    }

    if (selectedAxes.y && config.workingZoneY && config.yAxisLength && config.workingZoneY > config.yAxisLength) {
        result.isValid = false;
        result.errors.push('Working Zone Y cannot exceed Y-Axis Length.');
    }

    if (selectedAxes.z && config.workingZoneZ && config.zAxisLength && config.workingZoneZ > config.zAxisLength) {
        result.isValid = false;
        result.errors.push('Working Zone Z cannot exceed Z-Axis Length.');
    }

    return result;
}

/**
 * Check if 3D configuration requires user setup
 */
export function requires3DSetup(config: CncConfig | null | undefined): boolean {
    const validation = validateCnc3DConfig(config);
    return !validation.isValid;
}

/**
 * Get user-friendly setup message for missing 3D config
 */
export function get3DSetupMessage(config: CncConfig | null | undefined): string {
    const validation = validateCnc3DConfig(config);
    
    if (validation.isValid) {
        return '';
    }

    if (validation.errors.length === 1) {
        return validation.errors[0];
    }

    if (validation.errors.length > 1) {
        return `Configuration issues: ${validation.errors.join(', ')}`;
    }

    return 'Please configure the 3D CNC dimensions and working zones before using the 3D viewer.';
}