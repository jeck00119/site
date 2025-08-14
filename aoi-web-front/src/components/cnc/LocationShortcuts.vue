<template>
  <div class="locations-grid">
    <div class="actions-container">
      <div class="flex-row" v-for="row in 3" :key="row">
        <button
          v-for="col in 3" 
          :key="`${row}-${col}`"
          @click.right="openShortcutDialog($event)"
          @click="executeLocationShortcut($event)"
          @contextmenu.prevent
          class="button-wide custom-loc-button"
          type="button"
          :data-shortcut-index="`${(row-1)*3 + col-1}`"
          :disabled="!isConnected"
        >
          {{ shortcuts[(row-1)*3 + col-1]?.name || '' }}
        </button>
      </div>
    </div>

    <!-- Shortcut Configuration Dialog -->
    <base-dialog
      title="Choose CNC Location:"
      :show="showShortcutDialog"
      @close="closeShortcutDialog"
    >
      <template #default>
        <div class="form-control-dialog">
          <select class="dropdown" v-model="selectedLocation">
            <option
              v-for="loc in locations"
              :key="loc.uid"
              :value="loc"
            >
              {{ loc.name }}
            </option>
          </select>
          <label>New Location Name: </label>
          <input type="text" class="location-name" v-model="renamedLocation" />
        </div>
      </template>
      <template #actions>
        <div class="action-control">
          <base-button width="7vw" mode="flat" @click="attachLocation">
            Attach
          </base-button>
          <base-button width="7vw" mode="flat" @click="renameLocation">
            Rename
          </base-button>
          <base-button width="7vw" mode="flat" @click="clearLocation">
            Clear
          </base-button>
        </div>
      </template>
    </base-dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted } from "vue";
import { useCncStore } from '@/composables/useStore';

export default {
  name: "LocationShortcuts",
  props: {
    axisUid: {
      type: String,
      required: true
    },
    isConnected: {
      type: Boolean,
      default: false
    }
  },
  emits: ['shortcut-executed', 'shortcut-configured'],
  setup(props, { emit }) {
    const cncStore = useCncStore(props.axisUid);
    
    const showShortcutDialog = ref(false);
    const selectedLocation = ref(null);
    const renamedLocation = ref("");
    const shortcuts = ref(Array(9).fill(null));
    const currentShortcutIndex = ref(null);
    const currentShortcutButton = ref(null);

    // Get locations from the composable - this is already a computed ref
    const { locations } = cncStore;
    

    onMounted(async () => {
      loadShortcuts();
      // Fetch locations when component mounts to ensure they're available
      try {
        await cncStore.fetchLocations(props.axisUid);
      } catch (error) {
        console.error("[SHORTCUT DEBUG] Failed to fetch locations:", error);
        // Fallback: try loading all locations
        try {
          await cncStore.loadLocations();
        } catch (loadError) {
          console.error("[SHORTCUT DEBUG] Failed to load locations:", loadError);
        }
      }
    });

    function loadShortcuts() {
      // Load shortcuts from localStorage or store
      const savedShortcuts = localStorage.getItem(`cnc-shortcuts-${props.axisUid}`);
      if (savedShortcuts) {
        try {
          shortcuts.value = JSON.parse(savedShortcuts);
        } catch (error) {
          console.error("Failed to load shortcuts:", error);
          shortcuts.value = Array(9).fill(null);
        }
      }
    }

    function saveShortcuts() {
      localStorage.setItem(`cnc-shortcuts-${props.axisUid}`, JSON.stringify(shortcuts.value));
    }

    async function openShortcutDialog(event) {
      // Only allow configuration when connected
      if (!props.isConnected) {
        return;
      }
      
      // Fetch fresh locations for this axis right before opening the dialog
      try {
        await cncStore.fetchLocations(props.axisUid);
      } catch (error) {
        console.error("[SHORTCUT] Failed to fetch locations:", error);
      }
      
      currentShortcutButton.value = event.target;
      currentShortcutIndex.value = parseInt(event.target.dataset.shortcutIndex);
      renamedLocation.value = '';
      showShortcutDialog.value = true;
    }

    function closeShortcutDialog() {
      showShortcutDialog.value = false;
      currentShortcutButton.value = null;
      currentShortcutIndex.value = null;
      selectedLocation.value = null;
      renamedLocation.value = '';
    }

    async function executeLocationShortcut(event) {
      const shortcutIndex = parseInt(event.target.dataset.shortcutIndex);
      const shortcut = shortcuts.value[shortcutIndex];
      
      // Only execute if connected and shortcut exists
      if (props.isConnected && shortcut && shortcut.locationUid) {
        try {
          // Get fresh locations to find the target location
          await cncStore.fetchLocations(props.axisUid);
          const targetLocation = locations.value.find(loc => loc.uid === shortcut.locationUid);
          
          if (!targetLocation) {
            console.error('Target location not found:', shortcut.locationUid);
            return;
          }
          
          // Get current position from CNC store
          const currentPos = cncStore.pos?.value || { x: 0, y: 0, z: 0 };
          // Calculate movement steps needed for each axis (round to avoid floating point issues)
          const deltaX = Math.round((targetLocation.x - currentPos.x) * 1000) / 1000;
          const deltaY = Math.round((targetLocation.y - currentPos.y) * 1000) / 1000;
          const deltaZ = Math.round((targetLocation.z - currentPos.z) * 1000) / 1000;
          
          // Move each axis using the same logic as movement buttons
          const feedrate = targetLocation.feedrate || 1500;
          
          if (deltaX !== 0) {
            if (deltaX > 0) {
              await cncStore.increaseAxis({
                cncUid: props.axisUid,
                axis: 'x',
                step: Math.abs(deltaX),
                feedrate: feedrate
              });
            } else {
              await cncStore.decreaseAxis({
                cncUid: props.axisUid,
                axis: 'x',
                step: Math.abs(deltaX),
                feedrate: feedrate
              });
            }
          }
          
          if (deltaY !== 0) {
            if (deltaY > 0) {
              await cncStore.increaseAxis({
                cncUid: props.axisUid,
                axis: 'y',
                step: Math.abs(deltaY),
                feedrate: feedrate
              });
            } else {
              await cncStore.decreaseAxis({
                cncUid: props.axisUid,
                axis: 'y',
                step: Math.abs(deltaY),
                feedrate: feedrate
              });
            }
          }
          
          if (deltaZ !== 0) {
            if (deltaZ > 0) {
              await cncStore.increaseAxis({
                cncUid: props.axisUid,
                axis: 'z',
                step: Math.abs(deltaZ),
                feedrate: feedrate
              });
            } else {
              await cncStore.decreaseAxis({
                cncUid: props.axisUid,
                axis: 'z',
                step: Math.abs(deltaZ),
                feedrate: feedrate
              });
            }
          }
          
          emit('shortcut-executed', { 
            shortcut, 
            index: shortcutIndex,
            targetLocation,
            movements: { deltaX, deltaY, deltaZ }
          });
          
        } catch (error) {
          console.error('[SHORTCUT] Error executing shortcut:', error);
        }
      }
    }

    function attachLocation() {
      if (selectedLocation.value && currentShortcutIndex.value !== null) {
        shortcuts.value[currentShortcutIndex.value] = {
          name: selectedLocation.value.name,
          locationUid: selectedLocation.value.uid
        };
        
        saveShortcuts();
        
        emit('shortcut-configured', {
          action: 'attach',
          index: currentShortcutIndex.value,
          location: selectedLocation.value
        });
        
        closeShortcutDialog();
      }
    }

    async function renameLocation() {
      if (renamedLocation.value.trim() !== "" && selectedLocation.value) {
        try {
          await cncStore.patchLocation({
            locationUid: selectedLocation.value.uid, 
            newName: renamedLocation.value
          });
          
          // Refresh locations after rename
          setTimeout(() => {
            cncStore.fetchLocations(props.axisUid);
          }, 300);
          
          emit('shortcut-configured', {
            action: 'rename',
            location: selectedLocation.value,
            newName: renamedLocation.value
          });
          
        } catch (error) {
          console.error("Failed to rename location:", error);
        }
      }
    }

    function clearLocation() {
      if (currentShortcutIndex.value !== null) {
        shortcuts.value[currentShortcutIndex.value] = null;
        saveShortcuts();
        
        emit('shortcut-configured', {
          action: 'clear',
          index: currentShortcutIndex.value
        });
        
        closeShortcutDialog();
      }
    }

    return {
      shortcuts,
      showShortcutDialog,
      selectedLocation,
      renamedLocation,
      locations,
      openShortcutDialog,
      closeShortcutDialog,
      executeLocationShortcut,
      attachLocation,
      renameLocation,
      clearLocation
    };
  }
};
</script>

<style scoped>
.locations-grid {
  color: white;
  display: flex;
  flex-direction: column;
  height: 237px;
  width: 320px;
  border-radius: 8px;
  padding: 0.5rem;
  overflow: hidden;
  box-sizing: border-box;
}


.actions-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  gap: 0.5rem;
  flex: 1;
  justify-content: center;
  margin-top: 1rem;
  margin-bottom: 1rem;
}

.flex-row {
  display: flex;
  gap: 0.3rem;
  justify-content: space-between;
}

.button-wide {
  background: rgb(41, 41, 41);
  color: #ffffff;
  border-radius: 20px;
  box-shadow: rgb(41, 41, 41) 0 3px 5px -3px;
  box-sizing: border-box;
  cursor: pointer;
  border: 0;
  font-size: 0.8rem;
  height: 100%;
  margin: 3px;
  transition: all 0.2s ease;
}

.button-wide:hover:not(:disabled) {
  box-shadow: rgba(255, 255, 255, 0.2) 0 3px 15px inset,
    rgba(0, 0, 0, 0.1) 0 3px 5px, rgba(0, 0, 0, 0.1) 0 10px 13px;
  transform: scale(1.05);
}

.button-wide:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.custom-loc-button {
  width: 33%;
  height: 3.5vh;
  min-height: 40px;
  font-size: 0.7rem;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding: 0.25rem;
}

.form-control-dialog {
  display: flex;
  background-color: inherit;
  border: none;
  color: white;
  justify-content: center;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.dropdown {
  width: 60%;
  height: 30px;
  margin-bottom: 10px;
  background-color: rgb(204, 161, 82);
  color: rgb(0, 0, 0);
  border-radius: 4px;
  border: none;
  padding: 0.25rem;
}

.location-name {
  width: 60%;
  height: 30px;
  margin-top: 10px;
  background-color: rgb(41, 41, 41);
  border: none;
  color: white;
  text-align: center;
  border-radius: 4px;
  padding: 0.25rem;
}

.action-control {
  display: flex;
  gap: 1rem;
  justify-content: center;
}
</style>

