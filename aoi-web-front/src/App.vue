<template>
  <div class="page-container">
    <div class="nav-container">
      <the-navigator></the-navigator>
    </div>
    <div class="body-container">
      <div style="align-self: center" class="route-wrapper">
        <router-view v-slot="slotProps">
          <transition name="route" mode="out-in">
            <component :is="slotProps.Component"></component>
          </transition>
        </router-view>
      </div>
      <div style="align-self: flex-end" class="error-list-wrapper">
        <the-footer></the-footer>
      </div>
    </div>
  </div>
</template>


<script>
import { computed, onMounted, onUnmounted, watch } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router'; 
import { uuid } from 'vue3-uuid';

import TheNavigator from './components/layout/TheNavigator.vue';
import TheFooter from './components/layout/TheFooter.vue';
import { ipAddress, port } from "./url.js";
export default {
  components: {
    TheNavigator,
    TheFooter
  },

  setup() {
    const store = useStore();
    const router = useRouter();

    let configurationSocket = null;
    let ws_uid = null;

    const didAutoLogout = computed(function() {
      return store.getters["auth/didAutoLogout"];
    });

    watch(didAutoLogout, (current, old) => {
      if(current && current !== old)
      {
        router.replace('login');
      }
    });

    function connectToSocket() {
      ws_uid = uuid.v4();
      // Use secure WebSocket protocol based on current page protocol
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      configurationSocket = new WebSocket(`${protocol}//${ipAddress}:${port}/configurations/configuration_changes/${ws_uid}/ws`);

      configurationSocket.addEventListener('open', onConfigurationSocketOpen);
      configurationSocket.addEventListener('message', configurationChanged);
    }

    function disconnectFromSocket() {
      if(configurationSocket)
      {
        configurationSocket.removeEventListener('open', onConfigurationSocketOpen);
        configurationSocket.removeEventListener('message', configurationChanged);

        configurationSocket.close();
        configurationSocket = null;
        store.dispatch("configurations/closeConfigurationChangedSocket", {
          uid: ws_uid
        });
      }
    }

    function onConfigurationSocketOpen() {
      if(configurationSocket)
            configurationSocket.send('eses');
    }

    function configurationChanged(event) {
      let msg = JSON.parse(event.data);

      store.dispatch("configurations/setCurrentConfiguration", msg.configuration);
    }

    async function onLoad() {
      await store.dispatch("configurations/tryLoadConfiguration");
      // Temporarily disabled due to CORS issues - will re-enable after backend fix
      // store.dispatch("log/loadEvents");

      const configuration = store.getters["configurations/getCurrentConfiguration"];

      if(configuration)
      {
        store.dispatch('algorithms/loadAlgorithms');
        store.dispatch('algorithms/loadReferenceAlgorithms');

        store.dispatch('imageSources/loadImageSources');
        
        store.dispatch('algorithms/loadConfiguredAlgorithms');
        store.dispatch('algorithms/loadBasicAlgorithms');
      }

      connectToSocket();
    }

    store.dispatch("auth/tryLogin");

    onMounted(() => onLoad());

    onUnmounted(() => {
      disconnectFromSocket();
    });
  }
}
</script>

<style src="vue-multiselect/dist/vue-multiselect.css"></style>

<style scoped>
.page-container {
  display: flex;
  flex-direction: column;
  width: 100vw;
  padding: 0;
}

.body-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding: 0;
}

.route-wrapper {
  height: 93vh;
  padding: 0;
  width: 95%;
  margin-left: 3%;
}

.error-list-wrapper {
  height: 7vh;
  width: 100vw;
  background-color: black;
  color: white;
}

.route-enter-from {
  opacity: 0;
  transform: translateY(-30px);
}

.route-leave-to {
  opacity: 0;
  transform: translateY(30px);
}

.route-enter-to,
.route-leave-from {
  opacity: 1;
  transform: translateY(0);
}

.route-enter-active {
  transition: all 0.3s ease-out;
}

.route-leave-active {
  transition: all 0.3s ease-in;
}
</style>
