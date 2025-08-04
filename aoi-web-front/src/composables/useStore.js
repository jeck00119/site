/**
 * Vuex Store Composables
 * 
 * Provides reusable composable functions for common Vuex patterns.
 * Eliminates duplicate store usage code across 43+ components.
 */

import { computed, ref, watch } from 'vue';
import { useStore as useVuexStore } from 'vuex';

/**
 * Base store composable with common functionality
 */
export function useStore() {
  const store = useVuexStore();
  
  return {
    store,
    
    // Common getters
    getState: (module, key) => computed(() => store.getters[`${module}/${key}`]),
    getRootState: (key) => computed(() => store.state[key]),
    
    // Common actions
    dispatch: (action, payload) => store.dispatch(action, payload),
    commit: (mutation, payload) => store.commit(mutation, payload),
    
    // Batch operations
    dispatchMultiple: async (actions) => {
      const promises = actions.map(({ action, payload }) => store.dispatch(action, payload));
      return Promise.all(promises);
    },
    
    commitMultiple: (mutations) => {
      mutations.forEach(({ mutation, payload }) => store.commit(mutation, payload));
    }
  };
}

/**
 * CNC-specific store composable
 */
export function useCncStore(axisUid = null) {
  const { store, dispatch, commit, getState } = useStore();
  
  // CNC state getters
  const pos = axisUid ? computed(() => store.getters['cnc/pos'](axisUid)) : null;
  const mPos = axisUid ? computed(() => store.getters['cnc/mPos'](axisUid)) : null;
  const wPos = axisUid ? computed(() => store.getters['cnc/wPos'](axisUid)) : null;
  const cncState = axisUid ? computed(() => store.getters['cnc/cncState'](axisUid)) : null;
  const feedrate = axisUid ? computed(() => store.getters['cnc/feedrate'](axisUid)) : null;
  
  // CNC actions
  const setPosition = (uid, position) => dispatch('cnc/setPos', { uid, ...position });
  const setMPosition = (uid, x, y, z) => dispatch('cnc/setMPos', { uid, x, y, z });
  const setWPosition = (uid, x, y, z) => dispatch('cnc/setWPos', { uid, x, y, z });
  const setCncState = (uid, state) => dispatch('cnc/setCNCState', { uid, state });
  const setFeedrate = (uid, feedrate) => dispatch('cnc/setFeedrate', { uid, feedrate });
  
  // Batch CNC updates
  const updateCncData = (uid, data) => {
    const mutations = [];
    
    if (data.mPos) {
      mutations.push({
        mutation: 'cnc/setMPos',
        payload: { uid, x: data.mPos[0], y: data.mPos[1], z: data.mPos[2] }
      });
    }
    
    if (data.wPos) {
      mutations.push({
        mutation: 'cnc/setWPos', 
        payload: { uid, x: data.wPos[0], y: data.wPos[1], z: data.wPos[2] }
      });
    }
    
    if (data.state) {
      mutations.push({
        mutation: 'cnc/setCNCState',
        payload: { uid, state: data.state }
      });
    }
    
    if (data.feedrate) {
      mutations.push({
        mutation: 'cnc/setFeedrate',
        payload: { uid, feedrate: data.feedrate }
      });
    }
    
    // Commit all mutations at once
    mutations.forEach(({ mutation, payload }) => commit(mutation, payload));
    
    // Update position last (depends on mPos/wPos)
    if (data.mPos || data.wPos) {
      dispatch('cnc/setPos', { uid });
    }
  };
  
  return {
    // State
    pos,
    mPos,
    wPos,
    cncState,
    feedrate,
    
    // Actions
    setPosition,
    setMPosition,
    setWPosition,
    setCncState,
    setFeedrate,
    updateCncData,
    
    // Raw store access
    store,
    dispatch,
    commit
  };
}

/**
 * Camera store composable
 */
export function useCameraStore() {
  const { store, dispatch, getState } = useStore();
  
  // Camera state
  const cameras = computed(() => store.state.camera_settings?.cameras || []);
  const selectedCamera = computed(() => store.state.camera_settings?.selectedCamera);
  const cameraSettings = computed(() => store.state.camera_settings?.settings || {});
  
  // Camera actions
  const selectCamera = (cameraId) => dispatch('camera_settings/selectCamera', cameraId);
  const updateCameraSettings = (settings) => dispatch('camera_settings/updateSettings', settings);
  const addCamera = (camera) => dispatch('camera_settings/addCamera', camera);
  const removeCamera = (cameraId) => dispatch('camera_settings/removeCamera', cameraId);
  
  return {
    // State
    cameras,
    selectedCamera,
    cameraSettings,
    
    // Actions
    selectCamera,
    updateCameraSettings,
    addCamera,
    removeCamera,
    
    // Raw store access
    store,
    dispatch
  };
}

/**
 * Authentication store composable
 */
export function useAuthStore() {
  const { store, dispatch, getState } = useStore();
  
  // Auth state
  const user = computed(() => store.state.auth?.user);
  const isAuthenticated = computed(() => store.getters['auth/isAuthenticated']);
  const userLevel = computed(() => store.getters['auth/userLevel']);
  const permissions = computed(() => store.getters['auth/permissions']);
  
  // Auth actions
  const login = (credentials) => dispatch('auth/login', credentials);
  const logout = () => dispatch('auth/logout');
  const updateUser = (userData) => dispatch('auth/updateUser', userData);
  const checkAuth = () => dispatch('auth/checkAuth');
  
  return {
    // State
    user,
    isAuthenticated,
    userLevel,
    permissions,
    
    // Actions
    login,
    logout,
    updateUser,
    checkAuth,
    
    // Raw store access
    store,
    dispatch
  };
}

/**
 * Loading state composable
 */
export function useLoadingState(initialState = false) {
  const isLoading = ref(initialState);
  const error = ref(null);
  
  const setLoading = (loading) => {
    isLoading.value = loading;
    if (loading) {
      error.value = null; // Clear error when starting new operation
    }
  };
  
  const setError = (err) => {
    error.value = err;
    isLoading.value = false;
  };
  
  const clearError = () => {
    error.value = null;
  };
  
  const withLoading = async (asyncFn) => {
    try {
      setLoading(true);
      const result = await asyncFn();
      setLoading(false);
      return result;
    } catch (err) {
      setError(err);
      throw err;
    }
  };
  
  return {
    isLoading: computed(() => isLoading.value),
    error: computed(() => error.value),
    hasError: computed(() => error.value !== null),
    setLoading,
    setError,
    clearError,
    withLoading
  };
}

/**
 * Form state composable
 */
export function useFormState(initialData = {}) {
  const formData = ref({ ...initialData });
  const isDirty = ref(false);
  const errors = ref({});
  
  const updateField = (field, value) => {
    formData.value[field] = value;
    isDirty.value = true;
    
    // Clear field error when user starts typing
    if (errors.value[field]) {
      delete errors.value[field];
    }
  };
  
  const setErrors = (newErrors) => {
    errors.value = { ...newErrors };
  };
  
  const clearErrors = () => {
    errors.value = {};
  };
  
  const resetForm = () => {
    formData.value = { ...initialData };
    isDirty.value = false;
    errors.value = {};
  };
  
  const hasErrors = computed(() => Object.keys(errors.value).length > 0);
  const isValid = computed(() => !hasErrors.value);
  
  return {
    formData: computed(() => formData.value),
    isDirty: computed(() => isDirty.value),
    errors: computed(() => errors.value),
    hasErrors,
    isValid,
    updateField,
    setErrors,
    clearErrors,
    resetForm
  };
}

/**
 * WebSocket composable for real-time updates
 */
export function useWebSocket(url, options = {}) {
  const socket = ref(null);
  const isConnected = ref(false);
  const lastMessage = ref(null);
  const error = ref(null);
  
  const {
    autoConnect = true,
    reconnectAttempts = 5,
    reconnectInterval = 3000,
    onMessage = null,
    onError = null,
    onOpen = null,
    onClose = null
  } = options;
  
  let reconnectCount = 0;
  let reconnectTimer = null;
  
  const connect = () => {
    try {
      socket.value = new WebSocket(url);
      
      socket.value.onopen = (event) => {
        isConnected.value = true;
        error.value = null;
        reconnectCount = 0;
        
        if (onOpen) onOpen(event);
      };
      
      socket.value.onmessage = (event) => {
        lastMessage.value = event.data;
        
        if (onMessage) onMessage(event);
      };
      
      socket.value.onerror = (event) => {
        error.value = event;
        
        if (onError) onError(event);
      };
      
      socket.value.onclose = (event) => {
        isConnected.value = false;
        
        // Attempt reconnection
        if (reconnectCount < reconnectAttempts) {
          reconnectTimer = setTimeout(() => {
            reconnectCount++;
            connect();
          }, reconnectInterval);
        }
        
        if (onClose) onClose(event);
      };
      
    } catch (err) {
      error.value = err;
    }
  };
  
  const disconnect = () => {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }
    
    if (socket.value) {
      socket.value.close();
      socket.value = null;
    }
    
    isConnected.value = false;
  };
  
  const send = (data) => {
    if (socket.value && isConnected.value) {
      socket.value.send(typeof data === 'string' ? data : JSON.stringify(data));
    }
  };
  
  // Auto-connect if enabled
  if (autoConnect) {
    connect();
  }
  
  // Cleanup on unmount
  watch(() => socket.value, (newSocket, oldSocket) => {
    if (oldSocket) {
      oldSocket.close();
    }
  });
  
  return {
    socket: computed(() => socket.value),
    isConnected: computed(() => isConnected.value),
    lastMessage: computed(() => lastMessage.value),
    error: computed(() => error.value),
    connect,
    disconnect,
    send
  };
}

// Export all composables
export default {
  useStore,
  useCncStore,
  useCameraStore,
  useAuthStore,
  useLoadingState,
  useFormState,
  useWebSocket
};

