/**
 * Vuex Store Composables
 * 
 * Provides reusable composable functions for common Vuex patterns.
 * Eliminates duplicate store usage code across 43+ components.
 */

import { computed, ref, watch } from 'vue';
import { useStore as useVuexStore } from 'vuex';
import { logger } from '@/utils/logger';

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
  const locations = computed(() => store.getters['cnc/locations'] || []);
  
  // Additional getters for SystemSettings
  const cncs = computed(() => store.getters['cnc/getCNCs'] || []);
  const ports = computed(() => store.getters['cnc/getPorts'] || []);
  const cncTypes = computed(() => store.getters['cnc/getCNCTypes'] || []);
  
  // CNC actions
  const setPosition = (uid, position: any) => dispatch('cnc/setPos', { uid, ...position });
  const setMPosition = (uid, x, y, z: any) => dispatch('cnc/setMPos', { uid, x, y, z });
  const setWPosition = (uid, x, y, z: any) => dispatch('cnc/setWPos', { uid, x, y, z });
  const setCncState = (uid, state: any) => dispatch('cnc/setCNCState', { uid, state });
  const setFeedrate = (uid, feedrate: any) => dispatch('cnc/setFeedrate', { uid, feedrate });
  const apiCommand = (payload: any) => dispatch('cnc/api_command', payload);
  const increaseAxis = (payload: any) => dispatch('cnc/api_increaseAxis', payload);
  const decreaseAxis = (payload: any) => dispatch('cnc/api_decreaseAxis', payload);
  const moveRelative = (payload: any) => dispatch('cnc/api_moveRelative', payload);
  const terminalCommand = (payload: any) => dispatch('cnc/api_terminal', payload);
  const loadLocations = () => dispatch('cnc/loadLocations', {});
  const moveToLocation = (payload: any) => dispatch('cnc/api_moveToLocation', payload);
  const patchLocation = (payload: any) => dispatch('cnc/patchLocation', payload);
  const patchLocationWithCoordinates = (payload: any) => dispatch('cnc/patchLocationWithCoordinates', payload);
  const fetchLocations = (axisUid: any) => dispatch('cnc/fetchLocations', axisUid);
  const abort = (payload: any) => dispatch('cnc/api_jogCancel', payload);
  
  // Additional CNC management actions
  const loadCNCs = () => {
    logger.debug('CNC Composable: loadCNCs called, dispatching to store');
    return dispatch('cnc/loadCNCs', {});
  };
  const loadCNCTypes = () => dispatch('cnc/loadCNCTypes', {});
  const loadPorts = () => dispatch('cnc/loadPorts', {});
  const addCNC = (name: string, port: string, type: string) => dispatch('cnc/addCNC', { name, port, type });
  const removeCNC = (uid: any) => dispatch('cnc/removeCNC', uid);
  const updateCNCPort = (uid: any, port: string) => dispatch('cnc/updateCNCPort', { uid, port });
  const updateCNCType = (uid: any, type: string) => dispatch('cnc/updateCNCType', { uid, type });
  const saveCNCs = () => dispatch('cnc/saveCNCs', {});
  const saveCNC3DConfig = (cncUid: string, config3D: any) => dispatch('cnc/saveCNC3DConfig', { cncUid, config3D });
  
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
    locations,
    cncs,
    ports,
    cncTypes,
    
    // Actions
    setPosition,
    setMPosition,
    setWPosition,
    setCncState,
    setFeedrate,
    apiCommand,
    increaseAxis,
    decreaseAxis,
    moveRelative,
    terminalCommand,
    loadLocations,
    moveToLocation,
    patchLocation,
    patchLocationWithCoordinates,
    fetchLocations,
    abort,
    updateCncData,
    loadCNCs,
    loadCNCTypes,
    loadPorts,
    addCNC,
    removeCNC,
    updateCNCPort,
    updateCNCType,
    saveCNCs,
    saveCNC3DConfig,
    
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
  const cameras = computed(() => store.state.cameraSettings?.cameraList || []);
  const selectedCamera = computed(() => store.state.cameraSettings?.selectedCamera);
  const cameraSettings = computed(() => store.state.cameraSettings?.cameraSettingsList || []);
  const currentCameraSettings = computed(() => store.getters["cameraSettings/getCurrentCameraSettings"]);
  
  // Camera actions
  const selectCamera = (cameraId: any) => dispatch('cameraSettings/selectCamera', cameraId);
  const updateCameraSettings = (settings: any) => dispatch('cameraSettings/updateSettings', settings);
  const addCamera = (camera: any) => dispatch('cameraSettings/addCamera', camera);
  const removeCamera = (cameraId: any) => dispatch('cameraSettings/removeCamera', cameraId);
  const fetchCamerasList = () => dispatch('cameraSettings/fetchCamerasList', {});
  const fetchCamera = (cameraId: any) => dispatch('cameraSettings/fetchCamera', cameraId);
  const fetchCameraSettingsList = (cameraId: any) => dispatch('cameraSettings/fetchCameraSettingsList', cameraId);
  const fetchCameraSettings = (settingsId: any) => dispatch('cameraSettings/fetchCameraSettings', settingsId);
  const postCameraSettings = (settings: any) => dispatch('cameraSettings/postCameraSettings', settings);
  const putCameraSettings = (settings: any) => dispatch('cameraSettings/putCameraSettings', settings);
  const removeCameraSettings = (settingsId: any) => dispatch('cameraSettings/removeCameraSettings', settingsId);
  const loadCameraSettingsFromObject = (payload: any) => dispatch('cameraSettings/loadCameraSettingsFromObject', payload);
  const loadCameraSettingsToCamera = (payload: any) => dispatch('cameraSettings/loadCameraSettingsToCamera', payload);
  const setCurrentCameraConfig = (config: any) => dispatch('cameraSettings/setCurrentCameraConfig', config);
  const setCurrentCameraConfigName = (name: any) => dispatch('cameraSettings/setCurrentCameraConfigName', name);
  const setCurrentCameraConfigCameraType = (type: any) => dispatch('cameraSettings/setCurrentCameraConfigCameraType', type);
  const patchCameraSetting = (payload: any) => dispatch('cameraSettings/patchCameraSetting', payload);
  const readCameraTypes = () => dispatch('cameraSettings/readCameraTypes', {});
  
  return {
    // State
    cameras,
    selectedCamera,
    cameraSettings,
    currentCameraSettings,
    
    // Actions
    selectCamera,
    updateCameraSettings,
    addCamera,
    removeCamera,
    fetchCamerasList,
    fetchCamera,
    fetchCameraSettingsList,
    fetchCameraSettings,
    postCameraSettings,
    putCameraSettings,
    removeCameraSettings,
    loadCameraSettingsFromObject,
    loadCameraSettingsToCamera,
    setCurrentCameraConfig,
    setCurrentCameraConfigName,
    setCurrentCameraConfigCameraType,
    patchCameraSetting,
    readCameraTypes,
    
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
  
  // Auth state - match actual store structure
  const users = computed(() => store.getters['auth/getUsers']);
  const currentUser = computed(() => store.getters['auth/getCurrentUser']);
  const token = computed(() => store.getters['auth/getToken']);
  const isAuthenticated = computed(() => store.getters['auth/isAuthenticated']);
  const didAutoLogout = computed(() => store.getters['auth/didAutoLogout']);
  const availableRoles = computed(() => store.getters['auth/getAvailableRoles']);
  const userLevel = computed(() => store.getters['auth/userLevel']);
  const permissions = computed(() => store.getters['auth/permissions']);
  
  // Auth actions - match actual store actions
  const login = (credentials: any) => dispatch('auth/login', credentials);
  const logout = () => dispatch('auth/logout', {});
  const addUser = (userData: any) => dispatch('auth/addUser', userData);
  const loadUsers = () => dispatch('auth/loadUsers', {});
  const loadAvailableRoles = () => dispatch('auth/loadAvailableRoles', {});
  const updateUsersRole = (payload: any) => dispatch('auth/updateUsersRole', payload);
  const tryLogin = () => dispatch('auth/tryLogin', {});
  const autoLogout = () => dispatch('auth/autoLogout', {});
  
  return {
    // State
    users,
    currentUser,
    token,
    isAuthenticated,
    didAutoLogout,
    availableRoles,
    userLevel,
    permissions,
    
    // Actions
    login,
    logout,
    addUser,
    loadUsers,
    loadAvailableRoles,
    updateUsersRole,
    tryLogin,
    autoLogout,
    
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
export function useWebSocket(url: string, options: any = {}) {
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

/**
 * Algorithms store composable
 */
export function useAlgorithmsStore() {
  const { store, dispatch, getState } = useStore();
  
  const algorithms = computed(() => store.getters['algorithms/getAlgorithms']);
  const configuredAlgorithms = computed(() => store.getters['algorithms/getConfiguredAlgorithms']);
  const referenceAlgorithms = computed(() => store.getters['algorithms/getReferenceAlgorithms']);
  const currentAlgorithm = computed(() => store.getters['algorithms/getCurrentAlgorithm']);
  const algorithmAttributes = computed(() => store.getters['algorithms/getCurrentAlgorithmAttributes']);
  const algorithmResult = computed(() => store.getters['algorithms/getAlgorithmResult']);
  
  // Getter helper methods
  const getReferenceAlgorithmByType = (type) => store.getters['algorithms/getReferenceAlgorithmByType'](type);
  const getAlgorithmByType = (type) => store.getters['algorithms/getAlgorithmByType'](type);
  
  return {
    algorithms, configuredAlgorithms, referenceAlgorithms, currentAlgorithm, algorithmAttributes, algorithmResult,
    
    // Loading actions
    loadAlgorithms: () => dispatch('algorithms/loadAlgorithms', {}),
    loadReferenceAlgorithms: () => dispatch('algorithms/loadReferenceAlgorithms', {}),
    loadConfiguredAlgorithms: () => dispatch('algorithms/loadConfiguredAlgorithms', {}),
    loadBasicAlgorithms: () => dispatch('algorithms/loadBasicAlgorithms', {}),
    loadAlgorithm: (payload) => dispatch('algorithms/loadAlgorithm', payload),
    loadReferenceAlgorithm: (payload) => dispatch('algorithms/loadReferenceAlgorithm', payload),
    loadCurrentAlgorithm: (payload) => dispatch('algorithms/loadCurrentAlgorithm', payload),
    loadCurrentAlgorithmFromObject: (params) => dispatch('algorithms/loadCurrentAlgorithmFromObject', params),
    loadCurrentAlgorithmFromParameters: (payload) => dispatch('algorithms/loadCurrentAlgorithmFromParameters', payload),
    loadCurrentReferenceAlgorithmFromObject: (params) => dispatch('algorithms/loadCurrentReferenceAlgorithmFromObject', params),
    loadCurrentReferenceAlgorithmFromParameters: (payload) => dispatch('algorithms/loadCurrentReferenceAlgorithmFromParameters', payload),
    
    // Setters
    setCurrentAlgorithm: (algorithm) => dispatch('algorithms/setCurrentAlgorithm', algorithm),
    setCurrentAlgorithmAttributes: (attributes) => dispatch('algorithms/setCurrentAlgorithmAttributes', attributes),
    setCurrentReferenceAlgorithm: (algorithm) => dispatch('algorithms/setCurrentReferenceAlgorithm', algorithm),
    setCurrentReferenceAlgorithmAttributes: (attributes) => dispatch('algorithms/setCurrentReferenceAlgorithmAttributes', attributes),
    setAlgorithmResult: (result) => dispatch('algorithms/setAlgorithmResult', result),
    setLiveAlgorithm: (payload) => dispatch('algorithms/setLiveAlgorithm', payload),
    setLiveAlgorithmReference: () => dispatch('algorithms/setLiveAlgorithmReference', {}),
    setReferenceAlgorithm: (payload) => dispatch('algorithms/setReferenceAlgorithm', payload),
    setStaticImage: (image) => dispatch('algorithms/setStaticImage', image),
    
    // Update actions
    updateCurrentAlgorithmProperty: (payload) => dispatch('algorithms/updateCurrentAlgorithmProperty', payload),
    updateCurrentReferenceAlgorithmProperty: (payload) => dispatch('algorithms/updateCurrentReferenceAlgorithmProperty', payload),
    
    // Processing actions
    runAlgorithm: (payload) => dispatch('algorithms/runAlgorithm', payload),
    singleProcessAlgorithmCamera: (payload) => dispatch('algorithms/singleProcessAlgorithmCamera', payload),
    singleProcessReferenceCamera: (payload) => dispatch('algorithms/singleProcessReferenceCamera', payload),
    singleProcessReferenceStatic: (payload) => dispatch('algorithms/singleProcessReferenceStatic', payload),
    
    // Additional update actions
    updateCurrentBasicAlgorithmProperty: (payload) => dispatch('algorithms/updateCurrentBasicAlgorithmProperty', payload),
    updateCurrentBasicAlgorithmAttributes: (payload) => dispatch('algorithms/updateCurrentBasicAlgorithmAttributes', payload),
    updateCurrentAlgorithmAttributes: (payload) => dispatch('algorithms/updateCurrentAlgorithmAttributes', payload),
    updateCurrentReferenceAlgorithmAttributes: (payload) => dispatch('algorithms/updateCurrentReferenceAlgorithmAttributes', payload),
    updateCurrentAlgorithmGraphics: (data) => dispatch('algorithms/updateCurrentAlgorithmGraphics', data),
    uploadResource: (formData) => dispatch('algorithms/uploadResource', formData),
    
    // Reset actions
    resetLiveAlgorithmReference: () => dispatch('algorithms/resetLiveAlgorithmReference', {}),
    
    // Getter helpers
    getReferenceAlgorithmByType,
    getAlgorithmByType,
    
    store, dispatch
  };
}

/**
 * Components store composable
 */
export function useComponentsStore() {
  const { store, dispatch, getState } = useStore();
  
  const components = computed(() => store.getters['components/getAllComponents']);
  const currentComponent = computed(() => store.getters['components/getCurrentComponent']);
  const references = computed(() => store.getters['components/getReferences']);
  
  return {
    components, currentComponent, references,
    loadComponents: (payload) => {
      logger.debug('useComponentsStore.loadComponents called', { payload });
      logger.debug('Store modules available', { modules: Object.keys(store.state) });
      logger.debug('Components module exists', { exists: !!store.state.components });
      try {
        return dispatch('components/loadComponents', payload).then(result => {
          logger.debug('useComponentsStore.loadComponents dispatch completed', { type: payload.type });
          return result;
        }).catch(error => {
          logger.error('useComponentsStore.loadComponents dispatch failed', { type: payload.type, error });
          throw error;
        });
      } catch (syncError) {
        logger.error('useComponentsStore.loadComponents synchronous error', syncError);
        throw syncError;
      }
    },
    saveComponent: (component) => dispatch('components/saveComponent', component),
    deleteComponent: (id) => dispatch('components/deleteComponent', id),
    store, dispatch
  };
}

/**
 * Configurations store composable
 */
export function useConfigurationsStore() {
  const { store, dispatch, getState } = useStore();
  
  const configurations = computed(() => store.getters['configurations/getConfigurations']);
  const currentConfiguration = computed(() => store.getters['configurations/getCurrentConfiguration']);
  
  return {
    configurations, currentConfiguration,
    loadConfigurations: () => dispatch('configurations/loadConfigurations', {}),
    tryLoadConfiguration: () => dispatch('configurations/tryLoadConfiguration', {}),
    setCurrentConfiguration: (config) => dispatch('configurations/setCurrentConfiguration', config),
    loadConfiguration: (config) => dispatch('configurations/loadConfiguration', config),
    resetAllDatabases: () => dispatch('configurations/resetAllDatabases', {}),
    removeConfiguration: (payload) => dispatch('configurations/removeConfiguration', payload),
    addConfiguration: (config) => dispatch('configurations/addConfiguration', config),
    copyConfiguration: (payload) => dispatch('configurations/copyConfiguration', payload),
    editConfiguration: (config) => dispatch('configurations/editConfiguration', config),
    getConfigurationById: (id) => store.getters['configurations/getConfigurationById'](id),
    dispatch,
    store
  };
}

/**
 * Errors store composable
 */
export function useErrorsStore() {
  const { store, dispatch, getState } = useStore();
  
  const errors = computed(() => store.getters['errors/getErrors']);
  const hasErrors = computed(() => store.getters['errors/hasErrors']);
  
  return {
    errors, hasErrors,
    addError: (error) => dispatch('errors/addError', error),
    clearErrors: () => dispatch('errors/clearErrors', {}),
    removeError: (id) => dispatch('errors/removeError', id),
    store, dispatch
  };
}

/**
 * Graphics store composable
 */
export function useGraphicsStore() {
  const { store, dispatch, getState } = useStore();
  
  const graphicsItems = computed(() => store.getters['graphics/getGraphicsItems']);
  const selectedGraphic = computed(() => store.getters['graphics/getSelectedGraphic']);
  const currentGraphics = computed(() => store.getters['graphics/getCurrentGraphics']);
  const currentReferenceGraphics = computed(() => store.getters['graphics/getCurrentReferenceGraphics']);
  const canvas = computed(() => store.getters['graphics/getCanvas']);
  
  return {
    graphicsItems, selectedGraphic, currentGraphics, currentReferenceGraphics, canvas,
    
    // Graphics actions
    addGraphic: (graphic) => dispatch('graphics/addGraphic', graphic),
    removeGraphic: (id) => dispatch('graphics/removeGraphic', id),
    selectGraphic: (graphic) => dispatch('graphics/selectGraphic', graphic),
    setGraphicItems: (items) => dispatch('graphics/setGraphicItems', items),
    setReferenceGraphicItems: (items) => dispatch('graphics/setReferenceGraphicItems', items),
    setCanvas: (canvas) => dispatch('graphics/setCanvas', canvas),
    
    // Reset actions
    resetGraphicsItems: () => dispatch('graphics/resetGraphicsItems', {}),
    resetReferenceGraphicItems: () => dispatch('graphics/resetReferenceGraphicItems', {}),
    resetCompoundGraphicItems: () => dispatch('graphics/resetCompoundGraphicItems', {}),
    
    store, dispatch
  };
}

/**
 * Image Sources store composable
 */
export function useImageSourcesStore() {
  const { store, dispatch, getState } = useStore();
  
  const imageSources = computed(() => store.getters['imageSources/getImageSources']);
  const currentImageSource = computed(() => store.getters['imageSources/getCurrentImageSource']);
  const imageGenerators = computed(() => store.getters['imageSources/getImageGenerators']);
  const currentImageGenerator = computed(() => store.getters['imageSources/getCurrentImageGenerator']);
  const getImageSourceById = (id) => store.getters['imageSources/getImageSourceById'](id);
  
  return {
    imageSources, currentImageSource, imageGenerators, currentImageGenerator, getImageSourceById,
    loadImageSources: () => dispatch('imageSources/loadImageSources', {}),
    loadCurrentImageSource: (id) => dispatch('imageSources/loadCurrentImageSource', { uid: id }),
    selectImageSource: (source) => dispatch('imageSources/selectImageSource', source),
    setCurrentImageSource: (source) => dispatch('imageSources/setCurrentImageSource', source),
    setCurrentImageSourceProp: (prop, value) => dispatch('imageSources/setCurrentImageSourceProp', { prop, value }),
    getAllImageGenerators: () => dispatch('imageSources/getAllImageGenerators', {}),
    uploadImagesFromGenerator: (formData) => dispatch('imageSources/uploadImagesFromGenerator', formData),
    setCurrentImageGenerator: (gen) => dispatch('imageSources/setCurrentImageGenerator', gen),
    setCurrentImageGeneratorProp: (payload) => dispatch('imageSources/setCurrentImageGeneratorProp', payload),
    addImageGenerator: () => dispatch('imageSources/addImageGenerator', {}),
    loadImageGeneratorAsCurrent: (uid) => dispatch('imageSources/loadImageGeneratorAsCurrent', uid),
    updateImageSource: (config) => dispatch('imageSources/updateImageSource', config),
    removeImageSource: (source) => dispatch('imageSources/removeImageSource', source),
    getImageGeneratorById: (uid) => store.getters['imageSources/getImageGeneratorById'](uid),
    store, dispatch
  };
}

/**
 * Inspection List store composable
 */
export function useInspectionListStore() {
  const { store, dispatch, getState } = useStore();
  
  const inspectionList = computed(() => store.getters['inspections/getInspectionList']);
  const currentInspection = computed(() => store.getters['inspections/getCurrentInspection']);
  
  return {
    inspectionList, currentInspection,
    loadInspectionList: () => dispatch('inspections/loadInspectionList', {}),
    addInspection: (inspection) => dispatch('inspections/addInspection', inspection),
    store, dispatch
  };
}

/**
 * ITAC store composable
 */
export function useItacStore() {
  const { store, dispatch, getState } = useStore();
  
  const itacSettings = computed(() => store.getters['itac/getSettings']);
  const itacConnection = computed(() => store.getters['itac/getConnection']);
  
  return {
    itacSettings, itacConnection,
    updateSettings: (settings) => dispatch('itac/updateSettings', settings),
    testConnection: () => dispatch('itac/testConnection', {}),
    store, dispatch
  };
}

/**
 * Audit store composable - tracks user actions and events for compliance/audit trails
 */
export function useAuditStore() {
  const { store, dispatch, getState } = useStore();
  
  const logs = computed(() => store.getters['log/getLogs']);
  const logLevel = computed(() => store.getters['log/getLogLevel']);
  const events = computed(() => store.getters['log/getEvents']);
  
  return {
    logs, logLevel, events,
    loadLogs: () => dispatch('log/loadLogs', {}),
    loadEvents: () => dispatch('log/loadEvents', {}),
    addLog: (log) => dispatch('log/addLog', log),
    addEvent: (payload) => dispatch('log/addEvent', payload),
    removeEvent: (timestamp) => dispatch('log/removeEvent', { timestamp }),
    clearLogs: () => dispatch('log/clearLogs', {}),
    store, dispatch
  };
}

/**
 * Media store composable
 */
export function useMediaStore() {
  const { store, dispatch, getState } = useStore();
  
  const mediaFiles = computed(() => store.getters['media/getMediaFiles']);
  const currentMedia = computed(() => store.getters['media/getCurrentMedia']);
  const events = computed(() => store.getters['media/getEvents']);
  const channels = computed(() => store.getters['media/getChannels']);
  const files = computed(() => store.getters['media/getFiles']);
  
  return {
    mediaFiles, currentMedia, events, channels, files,
    loadMediaFiles: () => dispatch('media/loadMediaFiles', {}),
    loadEvents: () => dispatch('media/loadEvents', {}),
    loadChannels: () => dispatch('media/loadChannels', {}),
    loadFiles: () => dispatch('media/loadFiles', {}),
    playMedia: (media) => dispatch('media/playMedia', media),
    store, dispatch
  };
}

/**
 * Process store composable
 */
export function useProcessStore() {
  const { store, dispatch, getState } = useStore();
  
  const processState = computed(() => store.getters['process/getProcessState']);
  const isProcessing = computed(() => store.getters['process/isProcessing']);
  
  return {
    processState, isProcessing,
    startProcess: (config) => dispatch('process/startProcess', config),
    stopProcess: () => dispatch('process/stopProcess', {}),
    store, dispatch
  };
}

/**
 * Robots store composable
 */
export function useRobotsStore() {
  const { store, dispatch, getState } = useStore();
  
  const robots = computed(() => store.getters['robots/getRobots']);
  const currentRobot = computed(() => store.getters['robots/getCurrentRobot']);
  const robotState = computed(() => store.getters['robots/getRobotState']);
  const robotTypes = computed(() => store.getters['robots/getRobotTypes'] || []);
  const ultraArmPorts = computed(() => store.getters['robots/getUltraArmPorts'] || []);
  const currentAngles = computed(() => store.getters['robots/getCurrentAngles']);
  const currentRobotPositions = computed(() => store.getters['robots/getCurrentRobotPositions']);
  
  return {
    robots, currentRobot, robotState, robotTypes, ultraArmPorts, currentAngles, currentRobotPositions,
    loadRobots: () => dispatch('robots/loadRobots', {}),
    loadRobotTypes: () => dispatch('robots/loadRobotTypes', {}),
    loadUltraArmPorts: () => dispatch('robots/loadUltraArmPorts', {}),
    connectRobot: (robot) => dispatch('robots/connectRobot', robot),
    moveRobot: (position) => dispatch('robots/moveRobot', position),
    updateRobotConnectionID: (uid, value) => dispatch('robots/updateRobotConnectionID', { uid, value }),
    updateRobotType: (uid, type) => dispatch('robots/updateRobotType', { uid, type }),
    addRobot: (name) => dispatch('robots/addRobot', name),
    removeRobot: (uid) => dispatch('robots/removeRobot', uid),
    saveRobots: () => dispatch('robots/saveRobots', {}),
    store, dispatch
  };
}

/**
 * Camera Calibration store composable
 */
export function useCameraCalibrationStore() {
  const { store, dispatch, getState } = useStore();
  
  const calibrationData = computed(() => store.getters['cameraCalibration/getCalibrationData']);
  const isCalibrated = computed(() => store.getters['cameraCalibration/isCalibrated']);
  
  return {
    calibrationData, isCalibrated,
    startCalibration: () => dispatch('cameraCalibration/startCalibration', {}),
    saveCalibration: (data) => dispatch('cameraCalibration/saveCalibration', data),
    store, dispatch
  };
}

/**
 * Stereo Calibration store composable
 */
export function useStereoCalibrationStore() {
  const { store, dispatch, getState } = useStore();
  
  const stereoData = computed(() => store.getters['stereoCalibration/getStereoData']);
  
  return {
    stereoData,
    startStereoCalibration: () => dispatch('stereoCalibration/startCalibration', {}),
    saveStereoCalibration: (data) => dispatch('stereoCalibration/saveCalibration', data),
    store, dispatch
  };
}

/**
 * Profilometers store composable
 */
export function useProfilometersStore() {
  const { store, dispatch, getState } = useStore();
  
  const profilometers = computed(() => store.getters['profilometers/getProfilometers']);
  const currentProfilometer = computed(() => store.getters['profilometers/getCurrentProfilometer']);
  const profilometerTypes = computed(() => store.getters['profilometers/getProfilometerTypes'] || []);
  
  return {
    profilometers, currentProfilometer, profilometerTypes,
    loadProfilometers: () => dispatch('profilometers/loadProfilometers', {}),
    loadProfilometerTypes: () => dispatch('profilometers/loadProfilometerTypes', {}),
    connectProfilometer: (device) => dispatch('profilometers/connectProfilometer', device),
    addProfilometer: (name) => dispatch('profilometers/addProfilometer', name),
    removeProfilometer: (uid) => dispatch('profilometers/removeProfilometer', uid),
    updateProfilometerPort: (uid, port) => dispatch('profilometers/updateProfilometerPort', { uid, port }),
    updateProfilometerType: (uid, type) => dispatch('profilometers/updateProfilometerType', { uid, type }),
    saveProfilometers: () => dispatch('profilometers/saveProfilometers', {}),
    store, dispatch
  };
}

/**
 * Annotation store composable
 */
export function useAnnotationStore() {
  const { store, dispatch, getState } = useStore();
  
  const annotations = computed(() => store.getters['annotate/getAnnotations']);
  const currentAnnotation = computed(() => store.getters['annotate/getCurrentAnnotation']);
  
  return {
    annotations, currentAnnotation,
    addAnnotation: (annotation) => dispatch('annotate/addAnnotation', annotation),
    removeAnnotation: (id) => dispatch('annotate/removeAnnotation', id),
    store, dispatch
  };
}

/**
 * Help store composable
 */
export function useHelpStore() {
  const { store, dispatch, getState } = useStore();
  
  const helpContent = computed(() => store.getters['help/getHelpContent']);
  const currentTopic = computed(() => store.getters['help/getCurrentTopic']);
  
  return {
    helpContent, currentTopic,
    loadHelpContent: () => dispatch('help/loadHelpContent', {}),
    setCurrentTopic: (topic) => dispatch('help/setCurrentTopic', topic),
    store, dispatch
  };
}

// Import the new Fabric canvas composable
export { useFabricCanvas } from './useFabricCanvas';

// Alias for backward compatibility
export const useLogStore = useAuditStore;

// Export all composables
export default {
  useStore,
  useCncStore,
  useCameraStore,
  useAuthStore,
  useLoadingState,
  useFormState,
  useWebSocket,
  useAlgorithmsStore,
  useComponentsStore,
  useConfigurationsStore,
  useErrorsStore,
  useGraphicsStore,
  useImageSourcesStore,
  useInspectionListStore,
  useItacStore,
  useAuditStore,
  useLogStore,  // Alias for useAuditStore
  useMediaStore,
  useProcessStore,
  useRobotsStore,
  useCameraCalibrationStore,
  useStereoCalibrationStore,
  useProfilometersStore,
  useAnnotationStore,
  useHelpStore
};

