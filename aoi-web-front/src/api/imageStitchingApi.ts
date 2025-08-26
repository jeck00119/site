/**
 * Image Stitching API Client
 * 
 * Provides functions to interact with the backend image stitching service
 */

import { logger } from '@/utils/logger';
import { post, get, remove } from '@/utils/requests';

const API_BASE_URL = '/api/image_stitching';

export interface StitchingConfig {
  uid: string;
  step_size_x: number;
  step_size_y: number;
  z_height: number;
  overlap_percent: number;
  pattern: 'zigzag' | 'raster';
  working_area_x: number;
  working_area_y: number;
  camera_uid: string;
}

export interface CapturePosition {
  x: number;
  y: number;
  z: number;
  sequence_index: number;
}

export interface StitchingSession {
  uid: string;
  config: StitchingConfig;
  status: 'idle' | 'capturing' | 'processing' | 'completed' | 'failed';
  captured_images: Array<any>;
  total_positions: number;
  completed_positions: number;
  result_image_path?: string;
  error_message?: string;
  created_at: number;
  started_at?: number;
  completed_at?: number;
}

export interface StitchingProgress {
  session_uid: string;
  status: 'idle' | 'capturing' | 'processing' | 'completed' | 'failed';
  progress_percent: number;
  current_position?: CapturePosition;
  completed_positions: number;
  total_positions: number;
  message: string;
  error_message?: string;
}

export interface StitchingResult {
  session_uid: string;
  success: boolean;
  result_image_path?: string;
  result_image_url?: string;
  captured_image_count: number;
  processing_time_seconds?: number;
  image_dimensions?: [number, number];
  error_message?: string;
}

/**
 * Create a new stitching session
 */
export async function createStitchingSession(config: StitchingConfig): Promise<StitchingSession> {
  try {
    const response = await post(`${API_BASE_URL}/session`, config);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.responseData?.detail || 'Unknown error'}`);
    }
    
    logger.info(`Created stitching session ${config.uid}`);
    return response.responseData;
  } catch (error) {
    logger.error('Failed to create stitching session:', error);
    throw new Error(`Failed to create stitching session: ${error.message}`);
  }
}

/**
 * Get stitching session information
 */
export async function getStitchingSession(sessionUid: string): Promise<StitchingSession> {
  try {
    const response = await get(`${API_BASE_URL}/session/${sessionUid}`);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.responseData?.detail || 'Unknown error'}`);
    }
    
    return response.responseData;
  } catch (error) {
    logger.error(`Failed to get stitching session ${sessionUid}:`, error);
    throw new Error(`Failed to get stitching session: ${error.message}`);
  }
}

/**
 * Get stitching progress
 */
export async function getStitchingProgress(sessionUid: string): Promise<StitchingProgress> {
  try {
    const response = await get(`${API_BASE_URL}/session/${sessionUid}/progress`);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.responseData?.detail || 'Unknown error'}`);
    }
    
    return response.responseData;
  } catch (error) {
    logger.error(`Failed to get stitching progress ${sessionUid}:`, error);
    throw new Error(`Failed to get stitching progress: ${error.message}`);
  }
}

/**
 * Capture image at position
 */
export async function captureImageAtPosition(sessionUid: string, position: CapturePosition): Promise<any> {
  try {
    const response = await post(`${API_BASE_URL}/session/${sessionUid}/capture`, position);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.responseData?.detail || 'Unknown error'}`);
    }
    
    logger.debug(`Captured image at position (${position.x}, ${position.y}) for session ${sessionUid}`);
    return response.responseData;
  } catch (error) {
    logger.error(`Failed to capture image at position (${position.x}, ${position.y}):`, error);
    throw new Error(`Failed to capture image: ${error.message}`);
  }
}

/**
 * Start stitching process
 */
export async function startStitchingProcess(sessionUid: string): Promise<StitchingResult> {
  try {
    const response = await post(`${API_BASE_URL}/session/${sessionUid}/stitch`, {});
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.responseData?.detail || 'Unknown error'}`);
    }
    
    logger.info(`Stitching process completed for session ${sessionUid}`);
    return response.responseData;
  } catch (error) {
    logger.error(`Failed to stitch images for session ${sessionUid}:`, error);
    throw new Error(`Failed to stitch images: ${error.message}`);
  }
}

/**
 * Download stitching result
 */
export async function downloadStitchingResult(sessionUid: string): Promise<Blob> {
  try {
    const response = await get(`${API_BASE_URL}/session/${sessionUid}/result`);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.responseData?.detail || 'Unknown error'}`);
    }
    
    const blob = await response.blob?.();
    if (!blob) {
      throw new Error('Failed to get blob response');
    }
    
    logger.info(`Downloaded stitching result for session ${sessionUid}`);
    return blob;
  } catch (error) {
    logger.error(`Failed to download stitching result for session ${sessionUid}:`, error);
    throw new Error(`Failed to download result: ${error.message}`);
  }
}

/**
 * Get stitching result URL for direct access
 */
export function getStitchingResultUrl(sessionUid: string): string {
  return `${API_BASE_URL}/session/${sessionUid}/result`;
}

/**
 * Delete stitching session
 */
export async function deleteStitchingSession(sessionUid: string): Promise<boolean> {
  try {
    const response = await remove(`${API_BASE_URL}/session/${sessionUid}`);
    
    if (!response.ok) {
      logger.error(`Failed to delete stitching session ${sessionUid}: HTTP ${response.status}`);
      return false;
    }
    
    logger.info(`Deleted stitching session ${sessionUid}`);
    return true;
  } catch (error) {
    logger.error(`Failed to delete stitching session ${sessionUid}:`, error);
    return false;
  }
}

/**
 * List all stitching sessions
 */
export async function listStitchingSessions(): Promise<StitchingSession[]> {
  try {
    const response = await get(`${API_BASE_URL}/sessions`);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.responseData?.detail || 'Unknown error'}`);
    }
    
    return response.responseData;
  } catch (error) {
    logger.error('Failed to list stitching sessions:', error);
    throw new Error(`Failed to list sessions: ${error.message}`);
  }
}

/**
 * Generate a unique session ID
 */
export function generateSessionId(): string {
  return `stitching_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}