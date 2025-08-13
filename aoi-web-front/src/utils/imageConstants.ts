/**
 * Image Constants
 * Constants related to image handling and processing
 */

/**
 * Default image data URI prefix
 */
export const DEFAULT_IMAGE_DATA_URI_PREFIX = 'data:image/jpeg;base64,';

/**
 * Supported image formats
 */
export const SUPPORTED_IMAGE_FORMATS = [
    'jpg',
    'jpeg',
    'png',
    'gif',
    'bmp',
    'webp',
    'svg'
] as const;

export type SupportedImageFormat = typeof SUPPORTED_IMAGE_FORMATS[number];

/**
 * Image MIME types
 */
export const IMAGE_MIME_TYPES: Record<string, string> = {
    jpg: 'image/jpeg',
    jpeg: 'image/jpeg',
    png: 'image/png',
    gif: 'image/gif',
    bmp: 'image/bmp',
    webp: 'image/webp',
    svg: 'image/svg+xml'
};

/**
 * Maximum image dimensions
 */
export const MAX_IMAGE_DIMENSIONS = {
    width: 4096,
    height: 4096
} as const;

/**
 * Maximum file sizes (in bytes)
 */
export const MAX_FILE_SIZES = {
    image: 10 * 1024 * 1024, // 10MB
    thumbnail: 500 * 1024,    // 500KB
    icon: 100 * 1024         // 100KB
} as const;

/**
 * Default thumbnail dimensions
 */
export const THUMBNAIL_DIMENSIONS = {
    small: { width: 150, height: 150 },
    medium: { width: 300, height: 300 },
    large: { width: 600, height: 600 }
} as const;

/**
 * Canvas default settings
 */
export const CANVAS_DEFAULTS = {
    backgroundColor: '#ffffff',
    selectionColor: 'rgba(100, 100, 255, 0.3)',
    selectionBorderColor: 'rgba(255, 255, 255, 0.3)',
    selectionLineWidth: 1
} as const;

/**
 * Drawing tools
 */
export const DRAWING_TOOLS = {
    SELECT: 'select',
    RECTANGLE: 'rectangle',
    CIRCLE: 'circle',
    LINE: 'line',
    POLYGON: 'polygon',
    FREEHAND: 'freehand',
    TEXT: 'text',
    ARROW: 'arrow'
} as const;

export type DrawingTool = typeof DRAWING_TOOLS[keyof typeof DRAWING_TOOLS];

/**
 * Default colors for annotations
 */
export const ANNOTATION_COLORS = [
    '#FF0000', // Red
    '#00FF00', // Green
    '#0000FF', // Blue
    '#FFFF00', // Yellow
    '#FF00FF', // Magenta
    '#00FFFF', // Cyan
    '#FFA500', // Orange
    '#800080', // Purple
    '#FFC0CB', // Pink
    '#A52A2A'  // Brown
] as const;

/**
 * Image processing filters
 */
export const IMAGE_FILTERS = {
    NONE: 'none',
    GRAYSCALE: 'grayscale',
    SEPIA: 'sepia',
    INVERT: 'invert',
    BLUR: 'blur',
    BRIGHTNESS: 'brightness',
    CONTRAST: 'contrast',
    SATURATION: 'saturation'
} as const;

export type ImageFilter = typeof IMAGE_FILTERS[keyof typeof IMAGE_FILTERS];

/**
 * Zoom levels
 */
export const ZOOM_LEVELS = [
    0.1,  // 10%
    0.25, // 25%
    0.5,  // 50%
    0.75, // 75%
    1,    // 100%
    1.25, // 125%
    1.5,  // 150%
    2,    // 200%
    3,    // 300%
    4,    // 400%
    5     // 500%
] as const;

export const DEFAULT_ZOOM_LEVEL = 1;
export const MIN_ZOOM_LEVEL = 0.1;
export const MAX_ZOOM_LEVEL = 5;

/**
 * Image quality settings
 */
export const IMAGE_QUALITY = {
    LOW: 0.6,
    MEDIUM: 0.8,
    HIGH: 0.92,
    MAXIMUM: 1.0
} as const;

/**
 * Default image export settings
 */
export const EXPORT_DEFAULTS = {
    format: 'png' as SupportedImageFormat,
    quality: IMAGE_QUALITY.HIGH,
    includeAnnotations: true,
    backgroundColor: '#ffffff'
} as const;

/**
 * Helper function to check if a file is a supported image
 */
export function isSupportedImage(filename: string): boolean {
    const extension = filename.toLowerCase().split('.').pop();
    return extension ? SUPPORTED_IMAGE_FORMATS.includes(extension as SupportedImageFormat) : false;
}

/**
 * Helper function to get MIME type from filename
 */
export function getMimeType(filename: string): string | undefined {
    const extension = filename.toLowerCase().split('.').pop();
    return extension ? IMAGE_MIME_TYPES[extension] : undefined;
}

/**
 * Helper function to format file size
 */
export function formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Helper function to validate image dimensions
 */
export function validateImageDimensions(width: number, height: number): boolean {
    return width > 0 && 
           height > 0 && 
           width <= MAX_IMAGE_DIMENSIONS.width && 
           height <= MAX_IMAGE_DIMENSIONS.height;
}

/**
 * Image data utilities
 */
export const ImageDataUtils = {
    /**
     * Create a JPEG data URI from image data
     */
    createJpegDataURI(imageData: string): string {
        return DEFAULT_IMAGE_DATA_URI_PREFIX + imageData;
    },

    /**
     * Extract base64 data from data URI
     */
    extractBase64FromDataURI(dataUri: string): string {
        const parts = dataUri.split(',');
        return parts.length > 1 ? parts[1] : '';
    },

    /**
     * Check if string is a data URI
     */
    isDataURI(str: string): boolean {
        return str.startsWith('data:');
    }
};

export default {
    SUPPORTED_IMAGE_FORMATS,
    IMAGE_MIME_TYPES,
    MAX_IMAGE_DIMENSIONS,
    MAX_FILE_SIZES,
    THUMBNAIL_DIMENSIONS,
    CANVAS_DEFAULTS,
    DRAWING_TOOLS,
    ANNOTATION_COLORS,
    IMAGE_FILTERS,
    ZOOM_LEVELS,
    DEFAULT_ZOOM_LEVEL,
    MIN_ZOOM_LEVEL,
    MAX_ZOOM_LEVEL,
    IMAGE_QUALITY,
    EXPORT_DEFAULTS,
    DEFAULT_IMAGE_DATA_URI_PREFIX,
    ImageDataUtils,
    isSupportedImage,
    getMimeType,
    formatFileSize,
    validateImageDimensions
};