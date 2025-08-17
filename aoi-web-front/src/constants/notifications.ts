/**
 * Centralized Notification Messages and Constants
 * 
 * This file contains all notification messages used throughout the application.
 * Messages are organized by feature area and type for easy maintenance.
 */

// Notification Types
export enum NotificationType {
  SUCCESS = 'success',
  ERROR = 'error',
  WARNING = 'warning',
  INFO = 'info',
  LOADING = 'loading'
}

// Notification Icons (FontAwesome)
export const NotificationIcons = {
  [NotificationType.SUCCESS]: 'check-circle',
  [NotificationType.ERROR]: 'times-circle',
  [NotificationType.WARNING]: 'exclamation-triangle',
  [NotificationType.INFO]: 'info-circle',
  [NotificationType.LOADING]: 'spinner'
} as const;

// Notification Colors
export const NotificationColors = {
  [NotificationType.SUCCESS]: 'green',
  [NotificationType.ERROR]: 'red',
  [NotificationType.WARNING]: 'orange',
  [NotificationType.INFO]: 'blue',
  [NotificationType.LOADING]: 'blue'
} as const;

// ============================================
// CONFIGURATION MESSAGES
// ============================================
export const ConfigurationMessages = {
  // Loading states
  LOADING: 'Loading configuration. Please wait.',
  LOADING_ALL: 'Loading all configurations. Please wait.',
  SWITCHING: 'Switching configuration. Please wait.',
  
  // Success messages
  ADDED: (name: string) => `Configuration "${name}" added successfully.`,
  REMOVED: (name: string) => `Configuration "${name}" removed successfully.`,
  UPDATED: (name: string) => `Configuration "${name}" updated successfully.`,
  SELECTED: (name: string) => `Configuration "${name}" selected.`,
  SAVED: 'Configuration saved successfully.',
  
  // Error messages
  ADD_FAILED: (name: string) => `Could not add configuration "${name}".`,
  REMOVE_FAILED: 'Could not remove current configuration.',
  UPDATE_FAILED: 'Failed to update configuration.',
  LOAD_FAILED: 'Failed to load configuration.',
  SELECT_FAILED: 'Failed to select configuration.',
  NOT_FOUND: 'Configuration not found.',
  ALREADY_EXISTS: (name: string) => `Configuration "${name}" already exists.`,
  
  // Validation messages
  NAME_REQUIRED: 'Please enter a configuration name.',
  INVALID_NAME: 'Configuration name contains invalid characters.',
  SELECT_REQUIRED: 'Please select a configuration first.'
} as const;

// ============================================
// AUTHENTICATION MESSAGES
// ============================================
export const AuthMessages = {
  // Success messages
  LOGIN_SUCCESS: 'Login successful.',
  LOGOUT_SUCCESS: 'Logout successful.',
  SIGNUP_SUCCESS: 'Account created successfully.',
  PASSWORD_CHANGED: 'Password changed successfully.',
  
  // Error messages
  LOGIN_FAILED: 'Invalid username or password.',
  SIGNUP_FAILED: 'Failed to create account.',
  UNAUTHORIZED: 'You are not authorized to access this resource.',
  SESSION_EXPIRED: 'Your session has expired. Please login again.',
  
  // Validation messages
  USERNAME_REQUIRED: 'Please enter your username.',
  PASSWORD_REQUIRED: 'Please enter your password.',
  PASSWORD_MISMATCH: 'Passwords do not match.',
  INVALID_EMAIL: 'Please enter a valid email address.'
} as const;

// ============================================
// CAMERA MESSAGES
// ============================================
export const CameraMessages = {
  // Loading states
  INITIALIZING: 'Initializing camera. Please wait.',
  CONNECTING: 'Connecting to camera feed.',
  CALIBRATING: 'Calibrating camera. Please wait.',
  
  // Success messages
  CONNECTED: 'Camera connected successfully.',
  CALIBRATED: 'Camera calibrated successfully.',
  SNAPSHOT_SAVED: 'Snapshot saved successfully.',
  SETTINGS_UPDATED: 'Camera settings updated.',
  
  // Error messages
  CONNECTION_FAILED: 'Failed to connect to camera feed.',
  CALIBRATION_FAILED: 'Camera calibration failed.',
  NOT_AVAILABLE: 'Camera not available.',
  PERMISSION_DENIED: 'Camera permission denied.',
  
  // Info messages
  WARMUP: 'Camera warming up...',
  FPS_CHANGED: (fps: number) => `Camera FPS set to ${fps}.`
} as const;

// ============================================
// ALGORITHM MESSAGES
// ============================================
export const AlgorithmMessages = {
  // Loading states
  LOADING: 'Loading algorithm. Please wait.',
  PROCESSING: 'Processing algorithm. Please wait.',
  MODEL_LOADING: 'Detection model is being loaded. Please wait.',
  
  // Success messages
  LOADED: 'Algorithm loaded successfully.',
  SAVED: 'Algorithm saved successfully.',
  EXECUTED: 'Algorithm executed successfully.',
  REFERENCE_SET: 'Algorithm reference set successfully.',
  
  // Error messages
  LOAD_FAILED: 'Failed to load algorithm.',
  SAVE_FAILED: 'Failed to save algorithm.',
  EXECUTION_FAILED: 'Algorithm execution failed.',
  REFERENCE_FAILED: 'Failed to set algorithm reference.',
  NOT_FOUND: 'Algorithm not found.',
  
  // Validation messages
  NAME_REQUIRED: 'Please enter an algorithm name.',
  TYPE_REQUIRED: 'Please select an algorithm type.',
  PARAMETERS_INVALID: 'Invalid algorithm parameters.'
} as const;

// ============================================
// COMPONENT MESSAGES
// ============================================
export const ComponentMessages = {
  // Success messages
  ADDED: 'Component added successfully.',
  UPDATED: 'Component updated successfully.',
  REMOVED: 'Component removed successfully.',
  LOADED: 'Components loaded successfully.',
  
  // Error messages
  ADD_FAILED: 'Failed to add component.',
  UPDATE_FAILED: 'Failed to update component.',
  REMOVE_FAILED: 'Failed to remove component.',
  LOAD_FAILED: 'Failed to load components.',
  
  // Validation messages
  NAME_REQUIRED: 'Please enter a component name.',
  TYPE_REQUIRED: 'Please select a component type.',
  DUPLICATE_NAME: 'A component with this name already exists.'
} as const;

// ============================================
// FILE OPERATION MESSAGES
// ============================================
export const FileMessages = {
  // Success messages
  UPLOADED: (filename: string) => `File "${filename}" uploaded successfully.`,
  DOWNLOADED: (filename: string) => `File "${filename}" downloaded successfully.`,
  DELETED: (filename: string) => `File "${filename}" deleted successfully.`,
  IMPORTED: 'File imported successfully.',
  EXPORTED: 'File exported successfully.',
  
  // Error messages
  UPLOAD_FAILED: (filename: string) => `Failed to upload "${filename}".`,
  DOWNLOAD_FAILED: 'Failed to download file.',
  DELETE_FAILED: 'Failed to delete file.',
  NOT_FOUND: 'File not found.',
  
  // Validation messages
  INVALID_TYPE: (filename: string) => `"${filename}" is not a valid file type.`,
  TOO_LARGE: (filename: string, maxSize: string) => `"${filename}" exceeds maximum size of ${maxSize}.`,
  NOT_IMAGE: (filename: string) => `"${filename}" is not an image.`,
  EMPTY_FOLDER: 'The chosen folder is empty.',
  SELECT_FILE: 'Please select a file.'
} as const;

// ============================================
// ITAC MESSAGES
// ============================================
export const ItacMessages = {
  // Success messages
  UPDATED: 'ITAC configuration updated.',
  SAVED: 'ITAC configuration saved.',
  CONNECTED: 'Connected to ITAC server.',
  
  // Error messages
  UPDATE_FAILED: 'Error while updating ITAC.',
  CONNECTION_FAILED: 'Failed to connect to ITAC server.',
  VALIDATION_FAILED: 'ITAC validation failed.',
  
  // Info messages
  CHECKING: 'Checking ITAC connection...',
  SYNCING: 'Syncing with ITAC server...'
} as const;

// ============================================
// VALIDATION MESSAGES
// ============================================
export const ValidationMessages = {
  // Generic validation
  REQUIRED_FIELD: 'This field is required.',
  INVALID_FORMAT: 'Invalid format.',
  MIN_LENGTH: (min: number) => `Minimum length is ${min} characters.`,
  MAX_LENGTH: (max: number) => `Maximum length is ${max} characters.`,
  MIN_VALUE: (min: number) => `Minimum value is ${min}.`,
  MAX_VALUE: (max: number) => `Maximum value is ${max}.`,
  
  // Specific validations
  EVENT_NAME_REQUIRED: 'Please choose an event name before saving.',
  AUDIO_FILE_REQUIRED: 'Please choose an audio file before saving.',
  IMAGE_SOURCE_REQUIRED: 'Please select an image source.',
  REFERENCE_REQUIRED: 'Please select a reference.'
} as const;

// ============================================
// GENERAL MESSAGES
// ============================================
export const GeneralMessages = {
  // Success messages
  SAVED: 'Changes saved successfully.',
  UPDATED: 'Updated successfully.',
  DELETED: 'Deleted successfully.',
  COPIED: 'Copied to clipboard.',
  
  // Error messages
  ERROR_OCCURRED: 'An error occurred. Please try again.',
  NETWORK_ERROR: 'Network error. Please check your connection.',
  SERVER_ERROR: 'Server error. Please try again later.',
  TIMEOUT: 'Request timed out. Please try again.',
  
  // Info messages
  LOADING: 'Loading. Please wait.',
  PROCESSING: 'Processing. Please wait.',
  NO_DATA: 'No data available.',
  NO_CHANGES: 'No changes to save.',
  
  // Confirmation messages
  CONFIRM_DELETE: 'Are you sure you want to delete this item?',
  UNSAVED_CHANGES: 'You have unsaved changes. Do you want to continue?'
} as const;

// ============================================
// WEBSOCKET MESSAGES
// ============================================
export const WebSocketMessages = {
  CONNECTING: 'Connecting to server...',
  CONNECTED: 'Connected to server.',
  DISCONNECTED: 'Disconnected from server.',
  RECONNECTING: 'Reconnecting to server...',
  CONNECTION_LOST: 'Connection lost. Attempting to reconnect...',
  CONNECTION_FAILED: 'Failed to connect to server.'
} as const;

// ============================================
// HELPER FUNCTIONS
// ============================================

/**
 * Get notification config based on type
 */
export function getNotificationConfig(type: NotificationType) {
  return {
    icon: NotificationIcons[type],
    color: NotificationColors[type],
    timeout: type === NotificationType.LOADING ? 0 : 5000
  };
}

/**
 * Format error message with details
 */
export function formatErrorMessage(error: any): string {
  if (typeof error === 'string') return error;
  if (error?.message) return error.message;
  if (error?.detail) return error.detail;
  return GeneralMessages.ERROR_OCCURRED;
}

/**
 * Create a notification object
 */
export interface NotificationOptions {
  message: string;
  type?: NotificationType;
  timeout?: number;
  icon?: string;
  color?: string;
}

export function createNotification(
  message: string, 
  type: NotificationType = NotificationType.INFO
): NotificationOptions {
  const config = getNotificationConfig(type);
  return {
    message,
    type,
    ...config
  };
}

// Export all messages as a single object for easy access
export const Messages = {
  Configuration: ConfigurationMessages,
  Auth: AuthMessages,
  Camera: CameraMessages,
  Algorithm: AlgorithmMessages,
  Component: ComponentMessages,
  File: FileMessages,
  Itac: ItacMessages,
  Validation: ValidationMessages,
  General: GeneralMessages,
  WebSocket: WebSocketMessages
} as const;

export default Messages;