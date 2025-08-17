/**
 * Composable for dual persistence (localStorage + backend database)
 * Handles the common pattern of saving to localStorage immediately 
 * and syncing with backend database for permanent storage
 */

import { ref } from 'vue';
import api from '@/utils/api';
import { logger } from '@/utils/logger';

interface PersistenceOptions {
  localStoragePrefix?: string;
  defaultResourceId?: string;
  syncToBackend?: boolean;
}

export function useDualPersistence<T>(
  axisUid: string, 
  resourceType: 'sequences' | 'shortcuts',
  options: PersistenceOptions = {}
) {
  const {
    localStoragePrefix = 'cnc',
    defaultResourceId = 'default',
    syncToBackend = true
  } = options;

  const isLoading = ref(false);
  const error = ref<string | null>(null);

  // Generate consistent localStorage key
  const getStorageKey = () => `${localStoragePrefix}-${resourceType}-${axisUid}`;

  // Generate consistent backend resource data
  const createResourceData = (data: T, resourceId: string = defaultResourceId) => ({
    uid: `${resourceType}-${axisUid}-${resourceId}`,
    cncUid: axisUid,
    name: `Default ${resourceType.charAt(0).toUpperCase() + resourceType.slice(1)}`,
    items: data
  });

  /**
   * Save data to both localStorage and backend
   */
  const saveData = async (data: T, resourceId: string = defaultResourceId): Promise<void> => {
    const storageKey = getStorageKey();
    
    // Save to localStorage immediately for UI responsiveness
    try {
      localStorage.setItem(storageKey, JSON.stringify(data));
    } catch (err) {
      logger.error(`[${resourceType.toUpperCase()}] Failed to save to localStorage`, err);
    }

    // Save to backend if enabled
    if (syncToBackend) {
      try {
        const resourceData = createResourceData(data, resourceId);
        await api.post(`/cnc/${axisUid}/${resourceType}`, resourceData);
        logger.info(`[${resourceType.toUpperCase()}] Saved to backend successfully`);
        error.value = null;
      } catch (err) {
        logger.error(`[${resourceType.toUpperCase()}] Failed to save to backend`, err);
        error.value = `Failed to save ${resourceType} to database`;
        // Don't throw - localStorage save succeeded
      }
    }
  };

  /**
   * Load data from backend first, fallback to localStorage
   */
  const loadData = async (resourceId: string = defaultResourceId): Promise<T | null> => {
    const storageKey = getStorageKey();
    isLoading.value = true;
    error.value = null;

    logger.info(`[${resourceType.toUpperCase()}] Loading ${resourceType} for CNC`, { axisUid });

    // Try to load from backend first
    if (syncToBackend) {
      try {
        const response = await api.get(`/cnc/${axisUid}/${resourceType}`);
        logger.debug(`[${resourceType.toUpperCase()}] Backend response`, response.data);

        if (response.data && response.data.length > 0) {
          // Find the specific resource or take the first one
          const targetResource = response.data.find((r: any) => 
            r.uid === `${resourceType}-${axisUid}-${resourceId}`
          ) || response.data[0];
          
          logger.debug(`[${resourceType.toUpperCase()}] Found resource`, targetResource);

          if (targetResource && targetResource.items) {
            // Update localStorage with backend data
            localStorage.setItem(storageKey, JSON.stringify(targetResource.items));
            logger.info(`[${resourceType.toUpperCase()}] Loaded from backend successfully, items:`, 
              Array.isArray(targetResource.items) ? targetResource.items.length : 'N/A');
            
            isLoading.value = false;
            return targetResource.items as T;
          }
        }
        logger.debug(`[${resourceType.toUpperCase()}] No ${resourceType} found in backend`);
      } catch (err) {
        logger.error(`[${resourceType.toUpperCase()}] Failed to load from backend`, err);
        error.value = `Failed to load ${resourceType} from database`;
      }
    }

    // Fallback to localStorage
    const saved = localStorage.getItem(storageKey);
    logger.debug(`[${resourceType.toUpperCase()}] Checking localStorage, found`, { found: saved ? 'YES' : 'NO' });

    if (saved) {
      try {
        const parsedData = JSON.parse(saved) as T;
        logger.info(`[${resourceType.toUpperCase()}] Loaded from localStorage, items:`, 
          Array.isArray(parsedData) ? parsedData.length : 'N/A');

        // Try to sync localStorage data to backend if it has content
        if (syncToBackend && parsedData && 
            ((Array.isArray(parsedData) && parsedData.length > 0) || 
             (!Array.isArray(parsedData) && Object.keys(parsedData as any).length > 0))) {
          await saveData(parsedData, resourceId);
        }

        isLoading.value = false;
        return parsedData;
      } catch (err) {
        logger.error(`[${resourceType.toUpperCase()}] Failed to parse localStorage data`, err);
        error.value = `Failed to load ${resourceType} from local storage`;
      }
    }

    logger.debug(`[${resourceType.toUpperCase()}] No data found, returning null`);
    isLoading.value = false;
    return null;
  };

  /**
   * Clear data from both localStorage and backend
   */
  const clearData = async (resourceId: string = defaultResourceId): Promise<void> => {
    const storageKey = getStorageKey();
    
    // Clear localStorage
    localStorage.removeItem(storageKey);

    // Clear from backend if enabled
    if (syncToBackend) {
      try {
        await api.delete(`/cnc/${axisUid}/${resourceType}/${resourceType}-${axisUid}-${resourceId}`);
        logger.info(`[${resourceType.toUpperCase()}] Cleared from backend successfully`);
      } catch (err) {
        logger.error(`[${resourceType.toUpperCase()}] Failed to clear from backend`, err);
        error.value = `Failed to clear ${resourceType} from database`;
      }
    }
  };

  /**
   * Check if data exists in localStorage
   */
  const hasLocalData = (): boolean => {
    const storageKey = getStorageKey();
    const saved = localStorage.getItem(storageKey);
    return saved !== null && saved !== 'null' && saved !== '[]';
  };

  return {
    // Methods
    saveData,
    loadData,
    clearData,
    hasLocalData,
    
    // State
    isLoading,
    error,
    
    // Utilities
    getStorageKey,
    createResourceData
  };
}

export default useDualPersistence;