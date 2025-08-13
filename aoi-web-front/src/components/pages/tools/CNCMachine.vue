<template>
  <div class="page-container">
    <div class="flex-container">
      <div class="cnc" v-for="cnc in cncList" :key="cnc.id">
        <cnc 
          :axisName="cnc.name" 
          :axisUid="cnc.uid">
        </cnc>
      </div>
      <!-- Debug info -->
      <div v-if="!cncList || cncList.length === 0" style="color: white; padding: 20px;">
        <p>No CNCs available.</p>
        <p>CNC List: {{ cncList }}</p>
        <p>Is Array: {{ Array.isArray(cncList) }}</p>
        <p>Length: {{ cncList?.length }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, onMounted, onUnmounted, watch } from 'vue';
import { useCncStore, useConfigurationsStore } from '@/composables/useStore';

import cnc from "../../cnc/CNCRefactored.vue";

export default {
  components: {
    cnc,
  },

  setup(props, context) {
    const cncStore = useCncStore();
    const configurationsStore = useConfigurationsStore();

    // These are already computed refs from the composables


    const currentConfiguration = configurationsStore.currentConfiguration;

    // Watch for configuration changes and load CNCs when available
    watch(currentConfiguration, async (newConfig) => {
      if (newConfig) {
        try {
          console.log("CNCMachine: Loading CNCs for configuration", newConfig);
          await cncStore.loadCNCs();
          console.log("CNCMachine: CNCs loaded, count:", cncStore.cncs.value?.length || 0);
        } catch (error) {
          console.error("CNCMachine: Failed to load CNCs:", error);
        }
      }
    }, { immediate: true });

    // Watch the CNCs for changes
    watch(cncStore.cncs, (newCncs) => {
      console.log("CNCMachine: CNCs changed:", newCncs);
    });

    onMounted(() => {
      // Configuration should be loaded by the parent component
      // We'll rely on the watcher to trigger CNC loading
      console.log("CNCMachine: Component mounted, current config:", currentConfiguration.value);
      console.log("CNCMachine: Current CNCs:", cncStore.cncs.value);
    });

    onUnmounted(() => {
      try {
        // Clean up any CNC connections if needed
        console.log("CNCMachine component unmounting");
      } catch (error) {
        console.warn('Error during CNCMachine component unmounting:', error);
      }
    });

    return {
      cncList: cncStore.cncs
    };
  },
};
</script>

<style scoped>
.page-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  overflow-y: auto;
}

.page-container::-webkit-scrollbar {
  width: 8px;
}

.page-container::-webkit-scrollbar-track {
  background: rgba(255,255,255,0.05);
}

.page-container::-webkit-scrollbar-thumb {
  background: rgba(224, 181, 102, 0.3);
  border-radius: 4px;
}

.page-container::-webkit-scrollbar-thumb:hover {
  background: rgba(224, 181, 102, 0.5);
}


.flex-container {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  width: 100%;
  flex-grow: 1;
  overflow: visible;
  margin: 0;
  margin-left: -1rem;
}

.cnc {
  width: 100%;
  display: flex;
  margin: 0;
  padding: 0;
  justify-content: flex-start;
}
</style>