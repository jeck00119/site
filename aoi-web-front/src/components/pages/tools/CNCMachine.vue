<template>
  <div class="page-container">
    <div class="actions-header">
      <button @click="initializeConnections" class="initialize-button">
        Initialize All CNCs
      </button>
    </div>
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
import { computed, onMounted } from 'vue';
import { useStore } from 'vuex';

import cnc from "../../cnc/CNC.vue";

export default {
  components: {
    cnc,
  },

  setup(props, context) {
    const store = useStore();

    const currentConfiguration = computed(function() {
        return store.getters["configurations/getCurrentConfiguration"];
    });

    onMounted(()=>{
      if(currentConfiguration.value)
      {
        store.dispatch("cnc/loadCNCs");
      }
    });

    function initializeConnections() {
      console.log("Attempting to initialize all CNCs...");
      store.dispatch("cnc/initializeAllCNCs").catch(error => {
        console.error("Failed to initialize CNCs:", error);
      });
    }

    return {
      cncList: computed(()=>store.getters["cnc/getCNCs"]),
      initializeConnections
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
}

.actions-header {
  padding: 1rem;
  background-color: #2c2c2c;
  display: flex;
  justify-content: center;
  align-items: center;
}

.initialize-button {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: bold;
  color: white;
  background-color: #4CAF50;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.initialize-button:hover {
  background-color: #45a049;
}

.flex-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  flex-grow: 1;
  overflow-y: auto;
  margin: 0;
}

.cnc-container::-webkit-scrollbar { 
    display: none;
}

.cnc {
  width: 100%;
  display: flex;
  margin: 0;
  padding: 0;
  justify-content: flex-start;
}
</style>