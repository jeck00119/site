<template>
  <div class="position-sequence">
    <div class="sequence-controls">
      <!-- Play/Pause Controls -->
        <button 
          class="control-button play-button"
          @click="playSequence"
          :disabled="!isConnected || sequenceList.length === 0 || isExecuting"
          v-if="!isPlaying"
        >
          <font-awesome-icon icon="play" />
        </button>
        <button 
          class="control-button pause-button"
          @click="pauseSequence"
          :disabled="!isConnected"
          v-else
        >
          <font-awesome-icon icon="pause" />
        </button>
        
        <button 
          class="control-button stop-button"
          @click="stopSequence"
          :disabled="!isConnected || (!isPlaying && !isPaused)"
        >
          <font-awesome-icon icon="stop" />
        </button>
        
        <span class="sequence-status" v-if="isExecuting">
          {{ currentStepIndex + 1 }}/{{ sequenceList.length }}
        </span>
    </div>

    <!-- Sequence List -->
    <div class="sequence-list">
      <div 
        v-for="(item, index) in sequenceList" 
        :key="`${item.locationUid}-${index}`"
        class="sequence-item"
        :class="{ 
          'current-step': isExecuting && currentStepIndex === index,
          'completed-step': isExecuting && currentStepIndex > index 
        }"
      >
        <div class="item-content">
          <div class="item-name">{{ item.name }}</div>
          <div class="item-coords">
            <span>X: {{ item.x?.toFixed(3) || '---' }}</span>
            <span>Y: {{ item.y?.toFixed(3) || '---' }}</span>
            <span>Z: {{ item.z?.toFixed(3) || '---' }}</span>
          </div>
        </div>
        <div class="item-actions">
          <button 
            class="action-button move-up"
            @click="moveItemUp(index)"
            :disabled="index === 0 || isExecuting"
            title="Move Up"
          >
            <font-awesome-icon icon="chevron-up" />
          </button>
          <button 
            class="action-button move-down"
            @click="moveItemDown(index)"
            :disabled="index === sequenceList.length - 1 || isExecuting"
            title="Move Down"
          >
            <font-awesome-icon icon="chevron-down" />
          </button>
          <button 
            class="action-button remove-item"
            @click="removeFromSequence(index)"
            :disabled="isExecuting"
            title="Remove"
          >
            <font-awesome-icon icon="trash" />
          </button>
        </div>
      </div>
      
      <!-- Empty state -->
      <div v-if="sequenceList.length === 0" class="empty-sequence">
        <div class="empty-message">
          <font-awesome-icon icon="list" class="empty-icon" />
          <p>No positions in sequence</p>
          <p class="empty-hint">Add saved positions to create a sequence</p>
        </div>
      </div>
    </div>

    <!-- Add Positions Section -->
    <div class="add-section">
      <div class="add-controls">
        <select 
          class="position-select"
          v-model="selectedLocationToAdd"
          :disabled="isExecuting"
        >
          <option value="">Select Position</option>
          <option 
            v-for="location in availableLocations" 
            :key="location.uid"
            :value="location"
          >
            {{ location.name }} ({{ location.x?.toFixed(2) }}, {{ location.y?.toFixed(2) }}, {{ location.z?.toFixed(2) }})
          </option>
        </select>
        <button 
          class="add-button"
          @click="addToSequence"
          :disabled="!selectedLocationToAdd || isExecuting"
        >
          <font-awesome-icon icon="plus" />
          Add
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch, nextTick } from "vue";
import { useCncStore } from '@/composables/useStore';
import useDualPersistence from '@/composables/useDualPersistence';
import useCncMovement from '@/composables/useCncMovement';

export default {
  name: "PositionSequence",
  props: {
    axisUid: {
      type: String,
      required: true
    },
    isConnected: {
      type: Boolean,
      default: false
    },
  },
  emits: ['sequence-executed', 'sequence-paused', 'sequence-stopped'],
  setup(props, { emit }) {
    const cncStore = useCncStore(props.axisUid);
    
    // Use centralized composables
    const persistence = useDualPersistence(props.axisUid, 'sequences');
    const movement = useCncMovement(props.axisUid);
    
    // Sequence state
    const sequenceList = ref([]);
    const selectedLocationToAdd = ref("");
    const isPlaying = ref(false);
    const isPaused = ref(false);
    const isExecuting = ref(false);
    const currentStepIndex = ref(0);
    
    // Get locations from the store
    const { locations } = cncStore;
    
    // Available locations (exclude ones already in sequence)
    const availableLocations = computed(() => {
      const sequenceLocationUids = sequenceList.value.map(item => item.locationUid);
      return locations.value.filter(loc => !sequenceLocationUids.includes(loc.uid));
    });
    
    // Sequence management functions
    function addToSequence() {
      if (selectedLocationToAdd.value) {
        sequenceList.value.push({
          locationUid: selectedLocationToAdd.value.uid,
          name: selectedLocationToAdd.value.name,
          x: selectedLocationToAdd.value.x,
          y: selectedLocationToAdd.value.y,
          z: selectedLocationToAdd.value.z,
          feedrate: selectedLocationToAdd.value.feedrate || 1500
        });
        selectedLocationToAdd.value = "";
        saveSequence();
      }
    }
    
    function removeFromSequence(index) {
      sequenceList.value.splice(index, 1);
      saveSequence();
    }
    
    function moveItemUp(index) {
      if (index > 0) {
        const item = sequenceList.value.splice(index, 1)[0];
        sequenceList.value.splice(index - 1, 0, item);
        saveSequence();
      }
    }
    
    function moveItemDown(index) {
      if (index < sequenceList.value.length - 1) {
        const item = sequenceList.value.splice(index, 1)[0];
        sequenceList.value.splice(index + 1, 0, item);
        saveSequence();
      }
    }
    
    // Playback functions
    async function playSequence() {
      if (sequenceList.value.length === 0) return;
      
      try {
        isPlaying.value = true;
        isExecuting.value = true;
        isPaused.value = false;
        
        // Start from paused position or beginning
        const startIndex = isPaused.value ? currentStepIndex.value : 0;
        currentStepIndex.value = startIndex;
        
        for (let i = startIndex; i < sequenceList.value.length; i++) {
          if (!isPlaying.value) break; // Stop if paused/stopped
          
          currentStepIndex.value = i;
          const position = sequenceList.value[i];
          
          // Execute movement using centralized composable
          await movement.executeMovementToPosition(position, {
            feedrate: position.feedrate || 1500,
            waitForIdle: true
          });
          
          // Quick pause between positions
          await new Promise(resolve => setTimeout(resolve, 200));
        }
        
        // Sequence completed
        if (isPlaying.value) {
          stopSequence();
          emit('sequence-executed', { completed: true, steps: sequenceList.value.length });
        }
        
      } catch (error) {
        console.error('[SEQUENCE] Error executing sequence:', error);
        stopSequence();
      }
    }
    
    function pauseSequence() {
      isPlaying.value = false;
      isPaused.value = true;
      emit('sequence-paused', { currentStep: currentStepIndex.value });
    }
    
    function stopSequence() {
      isPlaying.value = false;
      isPaused.value = false;
      isExecuting.value = false;
      currentStepIndex.value = 0;
      emit('sequence-stopped');
    }
    
    // Movement logic is now handled by useCncMovement composable
    
    // Centralized persistence functions
    async function saveSequence() {
      await persistence.saveData(sequenceList.value);
    }
    
    async function loadSequence() {
      const loadedData = await persistence.loadData();
      sequenceList.value = loadedData || [];
    }
    
    // Auto-scroll to current executing position
    watch(currentStepIndex, async (newIndex) => {
      if (isExecuting.value && sequenceList.value.length > 0) {
        await nextTick(); // Wait for DOM updates
        
        // Find the current step element
        const sequenceItems = document.querySelectorAll('.sequence-item');
        const currentItem = sequenceItems[newIndex];
        
        if (currentItem) {
          // Scroll the item into view with smooth animation
          currentItem.scrollIntoView({
            behavior: 'smooth',
            block: 'center' // Center the item in the visible area
          });
        }
      }
    });
    
    // Lifecycle
    onMounted(async () => {
      await loadSequence();
      // Fetch locations when component mounts
      try {
        await cncStore.fetchLocations(props.axisUid);
      } catch (error) {
        console.error("[SEQUENCE] Failed to fetch locations:", error);
      }
    });
    
    return {
      sequenceList,
      selectedLocationToAdd,
      availableLocations,
      isPlaying,
      isPaused,
      isExecuting,
      currentStepIndex,
      addToSequence,
      removeFromSequence,
      moveItemUp,
      moveItemDown,
      playSequence,
      pauseSequence,
      stopSequence
    };
  }
};
</script>

<style scoped>
.position-sequence {
  color: white;
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  min-height: 237px;
  min-width: 380px;  /* Increased from 320px for wider display */
  border-radius: 8px;
  padding: 0.5rem;
  overflow: visible; /* Changed from hidden to visible to prevent cutting off content */
  box-sizing: border-box;
}

/* Playback Controls */
.sequence-controls {
  margin-top: 0.4rem;  /* Added top margin to prevent overlap with tab navigation */
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.control-button {
  background: rgb(41, 41, 41);
  color: white;
  border: none;
  border-radius: 50%;
  width: 35px;
  height: 35px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.9rem;
}

.play-button:hover:not(:disabled) {
  background: rgb(76, 175, 80);
  transform: scale(1.1);
}

.pause-button:hover:not(:disabled) {
  background: rgb(255, 193, 7);
  transform: scale(1.1);
}

.stop-button:hover:not(:disabled) {
  background: rgb(244, 67, 54);
  transform: scale(1.1);
}

.control-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.sequence-status {
  font-size: 0.9rem;
  font-weight: bold;
  color: rgb(204, 161, 82);
  margin-left: 0.5rem;
}

/* Sequence List */
.sequence-list {
  flex: 1;
  overflow-y: auto; /* Re-enabled scrolling */
  margin-bottom: 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  min-height: 100px;
  max-height: 300px; /* Reasonable max height for scrolling */
}


.sequence-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background-color: rgba(255, 255, 255, 0.02);
  transition: all 0.2s ease;
}

.sequence-item:last-child {
  border-bottom: none;
}

.sequence-item.current-step {
  background-color: rgba(204, 161, 82, 0.3);
  border-left: 3px solid rgb(204, 161, 82);
  box-shadow: 0 0 10px rgba(204, 161, 82, 0.4);
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    background-color: rgba(204, 161, 82, 0.3);
  }
  50% {
    background-color: rgba(204, 161, 82, 0.4);
  }
}

.sequence-item.completed-step {
  background-color: rgba(76, 175, 80, 0.1);
  border-left: 3px solid rgb(76, 175, 80);
  opacity: 0.7;
}

.item-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.item-name {
  font-weight: bold;
  font-size: 0.9rem;
  color: rgb(204, 161, 82);
}

.item-coords {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.7);
  font-family: monospace;
  display: flex;
  gap: 1rem;
}

.item-coords span {
  white-space: nowrap;
}

.item-actions {
  display: flex;
  gap: 0.2rem;
}

.action-button {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: none;
  border-radius: 4px;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.7rem;
}

.action-button:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.1);
}

.action-button.remove-item:hover:not(:disabled) {
  background: rgba(244, 67, 54, 0.8);
}

.action-button:disabled {
  opacity: 0.3;
  cursor: not-allowed;
  transform: none;
}

/* Empty State */
.empty-sequence {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 120px;
  text-align: center;
}

.empty-message {
  color: rgba(255, 255, 255, 0.5);
}

.empty-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  opacity: 0.3;
}

.empty-message p {
  margin: 0.25rem 0;
  font-size: 0.9rem;
}

.empty-hint {
  font-size: 0.8rem !important;
  opacity: 0.7;
}

/* Add Section */
.add-section {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 0.5rem;
}

.add-controls {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.position-select {
  flex: 1;
  background-color: rgb(41, 41, 41);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  padding: 0.4rem;
  font-size: 0.8rem;
}

.position-select:focus {
  outline: 2px solid rgb(204, 161, 82);
  border-color: rgb(204, 161, 82);
}

.add-button {
  background: rgb(204, 161, 82);
  color: rgb(41, 41, 41);
  border: none;
  border-radius: 4px;
  padding: 0.4rem 0.8rem;
  cursor: pointer;
  font-weight: bold;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 0.3rem;
  transition: all 0.2s ease;
}

.add-button:hover:not(:disabled) {
  background: rgb(224, 181, 102);
  transform: scale(1.05);
}

.add-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* Scrollbar styling */
.sequence-list::-webkit-scrollbar {
  width: 6px;
}

.sequence-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.sequence-list::-webkit-scrollbar-thumb {
  background: rgba(204, 161, 82, 0.5);
  border-radius: 3px;
}

.sequence-list::-webkit-scrollbar-thumb:hover {
  background: rgba(204, 161, 82, 0.8);
}
</style>