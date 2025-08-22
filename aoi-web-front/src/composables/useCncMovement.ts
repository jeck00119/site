/**
 * Composable for CNC movement operations
 * Handles position calculations, movement execution, and state monitoring
 */

import { ref } from 'vue';
import { useCncStore } from '@/composables/useStore';
import { logger } from '@/utils/logger';
import { formatPrecision } from '@/utils/validation';

interface Position {
  x: number;
  y: number;
  z: number;
}

interface LocationTarget extends Position {
  uid?: string;
  name?: string;
  feedrate?: number;
}

interface MovementOptions {
  feedrate?: number;
  timeout?: number;
  waitForIdle?: boolean;
}

export function useCncMovement(axisUid: string) {
  const cncStore = useCncStore(axisUid);
  const isMoving = ref(false);
  const error = ref<string | null>(null);

  /**
   * Calculate movement deltas between current and target positions
   */
  const calculateMovementDeltas = (currentPos: Position, targetPos: Position) => {
    // Round to 2 decimal places (0.01mm precision)
    const deltaX = Math.round((targetPos.x - currentPos.x) * 100) / 100;
    const deltaY = Math.round((targetPos.y - currentPos.y) * 100) / 100;
    const deltaZ = Math.round((targetPos.z - currentPos.z) * 100) / 100;

    return { deltaX, deltaY, deltaZ };
  };

  /**
   * Wait for CNC to reach idle state
   */
  const waitForCncIdle = (timeoutMs: number = 15000): Promise<void> => {
    return new Promise((resolve, reject) => {
      const startTime = Date.now();

      const checkIdle = () => {
        // Check if we've exceeded the timeout
        if (Date.now() - startTime > timeoutMs) {
          logger.warn('[CNC-MOVEMENT] Timeout waiting for CNC to become idle, continuing anyway');
          resolve(); // Continue instead of rejecting to avoid stopping operations
          return;
        }

        // Check if CNC state is IDLE - access the computed ref directly
        const currentState = cncStore.cncState?.value;

        if (currentState && currentState.toLowerCase() === 'idle') {
          resolve();
          return;
        }

        // Check again in 5ms for ultra-fast sequence response  
        setTimeout(checkIdle, 5);
      };

      // Initial check
      checkIdle();
    });
  };

  // Note: Individual axis movement is now handled by the simultaneous movement endpoint
  // The old moveAxis function has been removed in favor of moveRelative

  /**
   * Execute movement to a specific position
   */
  const executeMovementToPosition = async (
    targetLocation: LocationTarget,
    options: MovementOptions = {}
  ): Promise<void> => {
    const {
      feedrate = targetLocation.feedrate || 1500,
      timeout = 15000,
      waitForIdle = true
    } = options;

    if (isMoving.value) {
      throw new Error('CNC is already moving');
    }

    try {
      isMoving.value = true;
      error.value = null;

      // Get current position from CNC store
      const currentPos = cncStore.pos?.value || { x: 0, y: 0, z: 0 };
      
      console.log(`[DEBUG] Current position:`, currentPos);
      console.log(`[DEBUG] Current position values: x=${currentPos.x}, y=${currentPos.y}, z=${currentPos.z}`);
      console.log(`[DEBUG] Target location:`, targetLocation);

      // Calculate movement deltas
      const { deltaX, deltaY, deltaZ } = calculateMovementDeltas(currentPos, targetLocation);
      
      console.log(`[DEBUG] Calculated deltas: deltaX=${deltaX}, deltaY=${deltaY}, deltaZ=${deltaZ}`);

      logger.info(`[CNC-MOVEMENT] Moving to ${targetLocation.name || 'position'}`, {
        from: currentPos,
        to: { x: targetLocation.x, y: targetLocation.y, z: targetLocation.z },
        deltas: { deltaX, deltaY, deltaZ },
        feedrate
      });

      // Execute simultaneous movement using the new endpoint
      const hasMovement = deltaX !== 0 || deltaY !== 0 || deltaZ !== 0;
      
      if (hasMovement) {
        // Use the new moveRelative endpoint for simultaneous movement with 2 decimal precision
        await cncStore.moveRelative({
          cncUid: axisUid,
          x: formatPrecision(deltaX),
          y: formatPrecision(deltaY),
          z: formatPrecision(deltaZ),
          feedrate
        });

        // Wait for CNC to complete all movements and return to idle
        if (waitForIdle) {
          await waitForCncIdle(timeout);
        }
      }

      logger.info(`[CNC-MOVEMENT] Successfully moved to ${targetLocation.name || 'position'}`);
    } catch (err) {
      const errorMessage = `Error moving to position ${targetLocation.name || 'unknown'}: ${err}`;
      logger.error('[CNC-MOVEMENT]', errorMessage);
      error.value = errorMessage;
      throw new Error(errorMessage);
    } finally {
      isMoving.value = false;
    }
  };

  /**
   * Execute a sequence of movements
   */
  const executeMovementSequence = async (
    positions: LocationTarget[],
    options: MovementOptions = {}
  ): Promise<void> => {
    if (positions.length === 0) {
      throw new Error('No positions provided for sequence');
    }

    try {
      for (let i = 0; i < positions.length; i++) {
        const position = positions[i];
        logger.info(`[CNC-MOVEMENT] Executing sequence step ${i + 1}/${positions.length}`, { position: position.name });
        
        // Use more aggressive options for sequences
        const sequenceOptions = {
          ...options,
          timeout: 10000,  // Reduced timeout for sequences
          waitForIdle: true
        };
        
        await executeMovementToPosition(position, sequenceOptions);
        
        // No artificial delay - rely on immediate state detection
      }
      
      logger.info('[CNC-MOVEMENT] Sequence completed successfully');
    } catch (err) {
      logger.error('[CNC-MOVEMENT] Sequence execution failed', err);
      throw err;
    }
  };

  /**
   * Check if the CNC can execute movements (is connected and idle)
   */
  const canExecuteMovement = (): boolean => {
    const currentState = cncStore.cncState?.value;
    return currentState && currentState.toLowerCase() === 'idle' && !isMoving.value;
  };

  /**
   * Get current CNC position
   */
  const getCurrentPosition = (): Position => {
    return cncStore.pos?.value || { x: 0, y: 0, z: 0 };
  };

  /**
   * Stop all movements (emergency stop)
   */
  const emergencyStop = async (): Promise<void> => {
    try {
      await cncStore.abort({ cncUid: axisUid });
      isMoving.value = false;
      logger.info('[CNC-MOVEMENT] Emergency stop executed');
    } catch (err) {
      logger.error('[CNC-MOVEMENT] Failed to execute emergency stop', err);
      throw err;
    }
  };

  return {
    // Methods
    executeMovementToPosition,
    executeMovementSequence,
    waitForCncIdle,
    calculateMovementDeltas,
    emergencyStop,
    
    // Utilities
    canExecuteMovement,
    getCurrentPosition,
    
    // State
    isMoving,
    error
  };
}

export default useCncMovement;