<template>
  <div class="location-management">
    <div class="save-grid">
      <div class="action-general">
        <button
          class="button-save"
          @click="openDeleteDialog"
          title="Delete Location"
        >
          <div class="button-container">
            <div class="button-icon">
              <font-awesome-icon icon="trash" />
            </div>
          </div>
        </button>
        
        <button
          class="button-save"
          @click="openSaveDialog('all')"
          title="Save All Axes"
        >
          <div class="button-container">
            <div class="button-icon">
              <font-awesome-icon icon="floppy-disk" />
            </div>
          </div>
        </button>
      </div>
      
      <div class="action-axis">
        <button
          class="button-save"
          @click="openSaveDialog('x')"
          title="Save X Position"
        >
          <div class="button-container">
            <div class="button-icon">
              <font-awesome-icon icon="floppy-disk" />
            </div>
            <div class="button-text">X</div>
          </div>
        </button>
        
        <button
          class="button-save"
          @click="openSaveDialog('y')"
          title="Save Y Position"
        >
          <div class="button-container">
            <div class="button-icon">
              <font-awesome-icon icon="floppy-disk" />
            </div>
            <div class="button-text">Y</div>
          </div>
        </button>
        
        <button
          class="button-save"
          @click="openSaveDialog('z')"
          title="Save Z Position"
        >
          <div class="button-container">
            <div class="button-icon">
              <font-awesome-icon icon="floppy-disk" />
            </div>
            <div class="button-text">Z</div>
          </div>
        </button>
      </div>
    </div>

    <!-- Save Location Dialog -->
    <base-dialog
      title="Save new location"
      :show="showSaveDialog"
      @close="closeSaveDialog"
    >
      <template #default>
        <div class="dialog-content">
          <div class="input-group">
            <label>Name:</label>
            <input 
              type="text" 
              v-model.trim="newLocationName"
              @keyup.enter="saveLocation"
              placeholder="Enter location name"
              maxlength="50"
            />
          </div>
          
          <p>New position coordinates ({{ saveType }})</p>
          
          <table class="coordinates-table">
            <thead>
              <tr>
                <th>X</th>
                <th>Y</th>
                <th>Z</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>
                  <div class="boxed">{{ currentPosition.x.toFixed(3) }}</div>
                </td>
                <td>
                  <div class="boxed">{{ currentPosition.y.toFixed(3) }}</div>
                </td>
                <td>
                  <div class="boxed">{{ currentPosition.z.toFixed(3) }}</div>
                </td>
              </tr>
            </tbody>
          </table>
          
          <div class="save-type-info">
            <span v-if="saveType === 'all'">All axes will be saved</span>
            <span v-else>Only {{ saveType.toUpperCase() }} axis will be saved</span>
          </div>
        </div>
      </template>
      
      <template #actions>
        <base-button @click="saveLocation" :disabled="!newLocationName.trim() || isSaving">
          {{ isSaving ? 'Saving...' : 'Save' }}
        </base-button>
        <base-button @click="closeSaveDialog">Cancel</base-button>
      </template>
    </base-dialog>

    <!-- Delete Location Dialog -->
    <base-dialog
      title="Delete CNC Location:"
      :show="showDeleteDialog"
      @close="closeDeleteDialog"
    >
      <template #default>
        <div class="dialog-content">
          <div class="input-group">
            <label>Select location to delete:</label>
            <select class="dropdown" v-model="selectedLocationForDelete">
              <option value="">-- Select Location --</option>
              <option 
                v-for="loc in locations" 
                :key="loc.uid" 
                :value="loc.uid"
              >
                {{ loc.name }}
              </option>
            </select>
          </div>
          
          <div v-if="selectedLocationForDelete" class="warning-message">
            <font-awesome-icon icon="exclamation-triangle" />
            This action cannot be undone!
          </div>
        </div>
      </template>
      
      <template #actions>
        <base-button 
          @click="deleteLocation" 
          :disabled="!selectedLocationForDelete || isDeleting"
          mode="danger"
        >
          {{ isDeleting ? 'Deleting...' : 'Delete' }}
        </base-button>
        <base-button @click="closeDeleteDialog">Cancel</base-button>
      </template>
    </base-dialog>
  </div>
</template>

<script>
import { ref, computed } from "vue";
import { useCncStore, useLoadingState } from '@/composables/useStore';

export default {
  name: "LocationManagement",
  props: {
    axisUid: {
      type: String,
      required: true
    },
    currentPosition: {
      type: Object,
      required: true
    },
    selectedFeedrate: {
      type: [String, Number],
      required: true
    }
  },
  emits: ['location-saved', 'location-deleted'],
  setup(props, { emit }) {
    const cncStore = useCncStore(props.axisUid);
    const { withLoading } = useLoadingState();
    
    const showSaveDialog = ref(false);
    const showDeleteDialog = ref(false);
    const newLocationName = ref("");
    const selectedLocationForDelete = ref("");
    const saveType = ref("all");
    const isSaving = ref(false);
    const isDeleting = ref(false);

    const locations = computed(() => cncStore.store.getters['cnc/locations']);

    function openSaveDialog(type) {
      saveType.value = type;
      newLocationName.value = "";
      showSaveDialog.value = true;
    }

    function closeSaveDialog() {
      showSaveDialog.value = false;
      newLocationName.value = "";
      saveType.value = "all";
    }

    function openDeleteDialog() {
      selectedLocationForDelete.value = "";
      showDeleteDialog.value = true;
    }

    function closeDeleteDialog() {
      showDeleteDialog.value = false;
      selectedLocationForDelete.value = "";
    }

    async function saveLocation() {
      if (!newLocationName.value.trim() || isSaving.value) return;
      
      await withLoading(async () => {
        isSaving.value = true;
        try {
        
        const locationData = {
          uid: "str", // This will be generated by the backend
          axisUid: props.axisUid,
          degreeInStep: "deg",
          feedrate: props.selectedFeedrate,
          name: newLocationName.value.trim(),
          x: props.currentPosition.x,
          y: props.currentPosition.y,
          z: props.currentPosition.z,
        };
        
        console.log("Attempting to save location with data:", locationData);
        console.log("Save type:", saveType.value);
        
        await cncStore.dispatch('cnc/postLocation', [
          locationData,
          saveType.value,
          props.axisUid
        ]);
        
        emit('location-saved', {
          name: newLocationName.value.trim(),
          type: saveType.value,
          position: props.currentPosition
        });
        
        // Refresh locations list using composable
        setTimeout(() => {
          cncStore.dispatch('cnc/fetchLocations', props.axisUid);
        }, 200);
        
          closeSaveDialog();
        
        } catch (error) {
          console.error("Failed to save location:", error);
          console.error("Error details:", {
            message: error.message,
            stack: error.stack,
            locationData: locationData,
            saveType: saveType.value
          });
          
          // Show error to user instead of silent failure
          alert(`Failed to save location: ${error.message}`);
          
        } finally {
          isSaving.value = false;
        }
      });
    }

    async function deleteLocation() {
      if (!selectedLocationForDelete.value || isDeleting.value) return;
      
      await withLoading(async () => {
        isDeleting.value = true;
        try {
        
        await cncStore.dispatch('cnc/deleteLocation', selectedLocationForDelete.value);
        
        emit('location-deleted', {
          locationUid: selectedLocationForDelete.value
        });
        
        // Refresh locations list using composable
        setTimeout(() => {
          cncStore.dispatch('cnc/fetchLocations', props.axisUid);
        }, 300);
        
          closeDeleteDialog();
          
        } catch (error) {
          console.error("Failed to delete location:", error);
          
        } finally {
          isDeleting.value = false;
        }
      });
    }

    return {
      showSaveDialog,
      showDeleteDialog,
      newLocationName,
      selectedLocationForDelete,
      saveType,
      isSaving,
      isDeleting,
      locations,
      openSaveDialog,
      closeSaveDialog,
      openDeleteDialog,
      closeDeleteDialog,
      saveLocation,
      deleteLocation
    };
  }
};
</script>

<style scoped>
.location-management {
  width: 100%;
}

.save-grid {
  color: white;
  justify-content: space-evenly;
  align-items: center;
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  border-radius: 8px;
  padding: 0.5rem;
}

.action-general {
  display: flex;
  width: 100%;
  justify-content: space-around;
  margin-bottom: 0.5rem;
  gap: 0.5rem;
}

.action-axis {
  width: 100%;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-around;
  gap: 0.3rem;
}

.button-save {
  background: rgb(41, 41, 41);
  color: #ffffff;
  width: 45%;
  height: 60px;
  margin-bottom: 2%;
  border-radius: 8px;
  box-shadow: rgb(41, 41, 41) 0 3px 5px -3px;
  box-sizing: border-box;
  cursor: pointer;
  border: 0;
  transition: all 0.2s ease;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.button-save:hover {
  box-shadow: rgba(255, 255, 255, 0.2) 0 3px 15px inset,
    rgba(0, 0, 0, 0.1) 0 3px 5px, rgba(0, 0, 0, 0.1) 0 10px 13px;
  transform: scale(1.05);
  border: 1px solid rgb(61, 59, 59);
}

.button-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.2rem;
  height: 100%;
  width: 100%;
}

.button-icon {
  font-size: 1.4rem;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.button-text {
  font-size: 0.7rem;
  font-weight: bold;
  text-align: center;
  line-height: 1;
  display: block;
  width: 100%;
}

.dialog-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  color: white;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.input-group label {
  font-weight: bold;
}

.input-group input,
.dropdown {
  background-color: rgb(41, 41, 41);
  border: none;
  color: white;
  padding: 0.5rem;
  border-radius: 4px;
  font-size: 1rem;
}

.input-group input:focus,
.dropdown:focus {
  outline: 2px solid rgb(204, 161, 82);
  background-color: rgb(51, 51, 51);
}

.dropdown {
  background-color: rgb(204, 161, 82);
  color: rgb(0, 0, 0);
}

.coordinates-table {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
}

.coordinates-table th,
.coordinates-table td {
  padding: 0.5rem;
  text-align: center;
  border: 1px solid rgb(61, 61, 61);
}

.coordinates-table th {
  background-color: rgb(41, 41, 41);
  font-weight: bold;
}

.boxed {
  background-color: rgb(41, 41, 41);
  padding: 0.5rem;
  border-radius: 4px;
  font-family: monospace;
  font-weight: bold;
}

.save-type-info {
  font-style: italic;
  color: rgb(204, 161, 82);
  text-align: center;
}

.warning-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #ff6b6b;
  background-color: rgba(255, 107, 107, 0.1);
  padding: 0.5rem;
  border-radius: 4px;
  border-left: 4px solid #ff6b6b;
}
</style>

