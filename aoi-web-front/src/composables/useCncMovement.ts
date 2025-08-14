/**
 * Composable for CNC movement operations
 * Handles position calculations, movement execution, and state monitoring
 */

import { ref } from 'vue';
import { useCncStore } from '@/composables/useStore';

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
    // Round to avoid floating point precision issues
    const deltaX = Math.round((targetPos.x - currentPos.x) * 1000) / 1000;
    const deltaY = Math.round((targetPos.y - currentPos.y) * 1000) / 1000;
    const deltaZ = Math.round((targetPos.z - currentPos.z) * 1000) / 1000;

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
          console.warn('[CNC-MOVEMENT] Timeout waiting for CNC to become idle, continuing anyway');
          resolve(); // Continue instead of rejecting to avoid stopping operations
          return;
        }

        // Check if CNC state is IDLE - access the computed ref directly
        const currentState = cncStore.cncState?.value;

        if (currentState && currentState.toLowerCase() === 'idle') {
          resolve();
          return;
        }

        // Check again in 50ms for faster response
        setTimeout(checkIdle, 50);
      };

      // Initial check
      checkIdle();
    });
  };

  /**
   * Execute movement for a single axis
   */
  const moveAxis = async (
    axis: 'x' | 'y' | 'z',
    delta: number,
    feedrate: number
  ): Promise<void> => {
    if (delta === 0) return;

    const movement = delta > 0 
      ? cncStore.increaseAxis({
          cncUid: axisUid,
          axis,
          step: Math.abs(delta),
          feedrate
        })
      : cncStore.decreaseAxis({
          cncUid: axisUid,
          axis,
          step: Math.abs(delta),
          feedrate
        });

    await movement;
  };

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

      // Calculate movement deltas
      const { deltaX, deltaY, deltaZ } = calculateMovementDeltas(currentPos, targetLocation);

      console.log(`[CNC-MOVEMENT] Moving to ${targetLocation.name || 'position'}:`, {
        from: currentPos,
        to: { x: targetLocation.x, y: targetLocation.y, z: targetLocation.z },
        deltas: { deltaX, deltaY, deltaZ },
        feedrate
      });

      // Execute movements for all axes simultaneously
      const movements: Promise<void>[] = [];

      if (deltaX !== 0) {
        movements.push(moveAxis('x', deltaX, feedrate));
      }

      if (deltaY !== 0) {
        movements.push(moveAxis('y', deltaY, feedrate));
      }

      if (deltaZ !== 0) {
        movements.push(moveAxis('z', deltaZ, feedrate));
      }

      // Wait for all movement commands to be sent
      if (movements.length > 0) {
        await Promise.all(movements);

        // Wait for CNC to complete all movements and return to idle
        if (waitForIdle) {
          await waitForCncIdle(timeout);
        }
      }

      console.log(`[CNC-MOVEMENT] Successfully moved to ${targetLocation.name || 'position'}`);
    } catch (err) {
      const errorMessage = `Error moving to position ${targetLocation.name || 'unknown'}: ${err}`;
      console.error('[CNC-MOVEMENT]', errorMessage);
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
        console.log(`[CNC-MOVEMENT] Executing sequence step ${i + 1}/${positions.length}:`, position.name);
        
        await executeMovementToPosition(position, options);
        
        // Quick pause between positions to allow for state updates
        if (i < positions.length - 1) {
          await new Promise(resolve => setTimeout(resolve, 200));
        }
      }
      
      console.log('[CNC-MOVEMENT] Sequence completed successfully');
    } catch (err) {
      console.error('[CNC-MOVEMENT] Sequence execution failed:', err);
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
      console.log('[CNC-MOVEMENT] Emergency stop executed');
    } catch (err) {
      console.error('[CNC-MOVEMENT] Failed to execute emergency stop:', err);
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