<template>
  <div class="location-tabs">
    <!-- Tab Header with Navigation -->
    <div class="tab-header">
      <div class="tab-navigation">
        <button 
          class="nav-arrow"
          @click="switchTab('prev')"
          :disabled="currentTab === 0"
        >
          <font-awesome-icon icon="chevron-left" />
        </button>
        
        <div class="tab-indicator">
          <div class="tab-title">{{ currentTabName }}</div>
          <div class="tab-counter">{{ currentTab + 1 }} / {{ tabs.length }}</div>
        </div>
        
        <button 
          class="nav-arrow"
          @click="switchTab('next')"
          :disabled="currentTab === tabs.length - 1"
        >
          <font-awesome-icon icon="chevron-right" />
        </button>
      </div>
    </div>

    <!-- Tab Content -->
    <div class="tab-content">
      <!-- Shortcuts Tab -->
      <div v-if="currentTab === 0" class="tab-pane">
        <LocationShortcuts
          :axis-uid="axisUid"
          :is-connected="isConnected"
          @shortcut-executed="onShortcutExecuted"
          @shortcut-configured="onShortcutConfigured"
        />
      </div>
      
      <!-- Sequence Tab -->
      <div v-if="currentTab === 1" class="tab-pane">
        <PositionSequence
          :axis-uid="axisUid"
          :is-connected="isConnected"
          @sequence-executed="onSequenceExecuted"
          @sequence-paused="onSequencePaused"
          @sequence-stopped="onSequenceStopped"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from "vue";
import LocationShortcuts from "./LocationShortcuts.vue";
import PositionSequence from "./PositionSequence.vue";

export default {
  name: "LocationTabs",
  components: {
    LocationShortcuts,
    PositionSequence
  },
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
  emits: [
    'shortcut-executed', 
    'shortcut-configured',
    'sequence-executed', 
    'sequence-paused', 
    'sequence-stopped',
    'tab-changed'
  ],
  setup(props, { emit }) {
    const currentTab = ref(0);
    
    
    const tabs = [
      { name: "Shortcuts (Macros)", key: "shortcuts" },
      { name: "Position Sequence", key: "sequence" }
    ];
    
    const currentTabName = computed(() => tabs[currentTab.value].name);
    
    // Tab switching
    function switchTab(direction) {
      if (direction === 'next' && currentTab.value < tabs.length - 1) {
        currentTab.value++;
      } else if (direction === 'prev' && currentTab.value > 0) {
        currentTab.value--;
      }
      saveTabState();
      emit('tab-changed', currentTab.value);
    }
    
    // Persistence
    function saveTabState() {
      const tabKey = `cnc-location-tab-${props.axisUid}`;
      localStorage.setItem(tabKey, currentTab.value.toString());
    }
    
    function loadTabState() {
      const tabKey = `cnc-location-tab-${props.axisUid}`;
      const savedTab = localStorage.getItem(tabKey);
      if (savedTab !== null) {
        const tabIndex = parseInt(savedTab);
        if (tabIndex >= 0 && tabIndex < tabs.length) {
          currentTab.value = tabIndex;
        }
      }
    }
    
    // Event forwarding
    function onShortcutExecuted(data) {
      emit('shortcut-executed', data);
    }
    
    function onShortcutConfigured(data) {
      emit('shortcut-configured', data);
    }
    
    function onSequenceExecuted(data) {
      emit('sequence-executed', data);
    }
    
    function onSequencePaused(data) {
      emit('sequence-paused', data);
    }
    
    function onSequenceStopped() {
      emit('sequence-stopped');
    }
    
    // Lifecycle
    onMounted(() => {
      loadTabState();
      emit('tab-changed', currentTab.value);
    });
    
    return {
      currentTab,
      tabs,
      currentTabName,
      switchTab,
      onShortcutExecuted,
      onShortcutConfigured,
      onSequenceExecuted,
      onSequencePaused,
      onSequenceStopped
    };
  }
};
</script>

<style scoped>
.location-tabs {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  min-height: 280px;
  min-width: 380px;  /* Increased from 320px to match container */
  color: white;
  overflow: hidden;
  box-sizing: border-box;
}

/* Tab Header */
.tab-header {
  margin-bottom: 0.5rem;
  height: 35px;
  min-height: 35px;
  max-height: 35px;
  flex-shrink: 0;
}

.tab-navigation {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: rgb(41, 41, 41);
  border-radius: 15px;
  padding: 0.3rem;
  gap: 0.3rem;
}

.nav-arrow {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: none;
  border-radius: 50%;
  width: 26px;
  height: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.8rem;
}

.nav-arrow:hover:not(:disabled) {
  background: rgb(204, 161, 82);
  color: rgb(41, 41, 41);
  transform: scale(1.1);
}

.nav-arrow:disabled {
  opacity: 0.3;
  cursor: not-allowed;
  transform: none;
}

.tab-indicator {
  flex: 1;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.tab-title {
  font-size: 1rem;
  font-weight: bold;
  color: rgb(204, 161, 82);
}

.tab-counter {
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.7);
  font-weight: normal;
}

/* Tab Content */
.tab-content {
  flex: 1;  /* Changed from fixed height to flex to use available space */
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 237px;  /* Maintain minimum height */
}

.tab-pane {
  flex: 1;  /* Changed from fixed height to flex */
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 237px;  /* Maintain minimum height */
}

/* Animation for tab switching */
.tab-pane {
  animation: fadeIn 0.2s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateX(10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Responsive adjustments */
@media screen and (max-width: 1300px) {
  .tab-title {
    font-size: 1rem;
  }
  
  .nav-arrow {
    width: 28px;
    height: 28px;
    font-size: 0.8rem;
  }
  
  .tab-counter {
    font-size: 0.7rem;
  }
}
</style>