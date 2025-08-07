<template>
  <div class="page-container">
    <div class="flex-container">
      <div class="cnc" v-for="cnc in cncList" :key="cnc.id">
        <cnc 
          :axisName="cnc.name" 
          :axisUid="cnc.uid">
        </cnc>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, onMounted, onUnmounted, watch } from 'vue';
import { useStore } from 'vuex';

import cnc from "../../cnc/CNCRefactored.vue";

export default {
  components: {
    cnc,
  },

  setup(props, context) {
    const store = useStore();

    const currentConfiguration = computed(function() {
        return store.getters["configurations/getCurrentConfiguration"];
    });

    // Watch for configuration changes and load CNCs when available
    watch(currentConfiguration, (newConfig) => {
      if (newConfig) {
        try {
          store.dispatch("cnc/loadCNCs");
        } catch (error) {
          console.error("Failed to load CNCs:", error);
        }
      }
    }, { immediate: true });

    onMounted(() => {
      // Configuration should be loaded by the parent component
      // We'll rely on the watcher to trigger CNC loading
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
      cncList: computed(()=>store.getters["cnc/getCNCs"])
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