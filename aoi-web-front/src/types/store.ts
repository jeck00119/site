// Vuex Store Types for AOI Platform

import type { 
  User, 
  Configuration, 
  Algorithm, 
  Component, 
  CncModel, 
  LocationModel, 
  Camera, 
  ImageSource, 
  Inspection, 
  LogEvent, 
  Robot, 
  MediaFile 
} from './api';

// Root State
export interface RootState {
  auth: AuthState;
  configurations: ConfigurationState;
  algorithms: AlgorithmState;
  components: ComponentState;
  cnc: CncState;
  cameras: CameraState;
  imageSources: ImageSourceState;
  inspections: InspectionState;
  log: LogState;
  robots: RobotState;
  media: MediaState;
  errors: ErrorState;
  graphics: GraphicsState;
  process: ProcessState;
  cameraSettings: CameraSettingsState;
  profilometers: ProfilometerState;
  itac: ItacState;
  help: HelpState;
  peripherals: PeripheralState;
  cameraCalibration: CameraCalibrationState;
  stereoCalibration: StereoCalibrationState;
  annotate: AnnotationState;
}

// Auth Module State
export interface AuthState {
  users: User[];
  token: string | null;
  currentUser: User | null;
  didAutoLogout: boolean;
  availableRoles: string[];
}

// Configuration Module State
export interface ConfigurationState {
  configurations: Configuration[];
  currentConfiguration: Configuration | null;
  loading: boolean;
  error: string | null;
}

// Algorithm Module State
export interface AlgorithmState {
  algorithms: Algorithm[];
  referenceAlgorithms: Algorithm[];
  configuredAlgorithms: Algorithm[];
  basicAlgorithms: Algorithm[];
  selectedAlgorithm: Algorithm | null;
  loading: boolean;
  error: string | null;
}

// Component Module State
export interface ComponentState {
  components: Component[];
  customComponents: Component[];
  selectedComponent: Component | null;
  loading: boolean;
  error: string | null;
}

// CNC Module State
export interface CncState {
  cncs: CncModel[];
  locations: LocationModel[];
  selectedCnc: CncModel | null;
  currentPosition: {
    x: number;
    y: number;
    z: number;
  };
  machinePosition: {
    x: number;
    y: number;
    z: number;
  };
  workPosition: {
    x: number;
    y: number;
    z: number;
  };
  connected: boolean;
  loading: boolean;
  error: string | null;
}

// Camera Module State
export interface CameraState {
  cameras: Camera[];
  selectedCamera: Camera | null;
  connected: boolean;
  loading: boolean;
  error: string | null;
}

// Image Source Module State
export interface ImageSourceState {
  imageSources: ImageSource[];
  selectedImageSource: ImageSource | null;
  loading: boolean;
  error: string | null;
}

// Inspection Module State
export interface InspectionState {
  inspections: Inspection[];
  currentInspection: Inspection | null;
  results: any[];
  loading: boolean;
  error: string | null;
}

// Log Module State
export interface LogState {
  events: LogEvent[];
  filters: string[];
  loading: boolean;
  error: string | null;
}

// Robot Module State
export interface RobotState {
  robots: Robot[];
  selectedRobot: Robot | null;
  connected: boolean;
  loading: boolean;
  error: string | null;
}

// Media Module State
export interface MediaState {
  files: MediaFile[];
  selectedFile: MediaFile | null;
  loading: boolean;
  error: string | null;
}

// Error Module State
export interface ErrorState {
  errors: Array<{
    id: string;
    message: string;
    type: 'error' | 'warning' | 'info';
    timestamp: number;
  }>;
}

// Graphics Module State
export interface GraphicsState {
  canvas: any;
  selectedTool: string | null;
  zoom: number;
  pan: { x: number; y: number };
}

// Process Module State
export interface ProcessState {
  running: boolean;
  progress: number;
  status: string;
  results: any[];
}

// Camera Settings Module State
export interface CameraSettingsState {
  settings: Record<string, any>;
  profiles: Array<{
    name: string;
    settings: Record<string, any>;
  }>;
}

// Profilometer Module State
export interface ProfilometerState {
  devices: any[];
  selectedDevice: any | null;
  measurements: any[];
  loading: boolean;
  error: string | null;
}

// ITAC Module State
export interface ItacState {
  settings: Record<string, any>;
  connected: boolean;
  loading: boolean;
  error: string | null;
}

// Help Module State
export interface HelpState {
  topics: Array<{
    id: string;
    title: string;
    content: string;
  }>;
  selectedTopic: string | null;
}

// Peripheral Module State
export interface PeripheralState {
  devices: any[];
  connected: boolean;
  loading: boolean;
  error: string | null;
}

// Camera Calibration Module State
export interface CameraCalibrationState {
  calibrationData: any;
  images: string[];
  progress: number;
  loading: boolean;
  error: string | null;
}

// Stereo Calibration Module State
export interface StereoCalibrationState {
  calibrationData: any;
  leftImages: string[];
  rightImages: string[];
  progress: number;
  loading: boolean;
  error: string | null;
}

// Annotation Module State
export interface AnnotationState {
  annotations: any[];
  selectedAnnotation: any | null;
  tools: string[];
  selectedTool: string | null;
}

// Mutation Types
export interface MutationTypes {
  // Auth mutations
  SET_USER: 'SET_USER';
  SET_USERS: 'SET_USERS';
  LOGOUT: 'LOGOUT';
  SET_AUTO_LOGOUT: 'SET_AUTO_LOGOUT';
  
  // Configuration mutations
  SET_CONFIGURATIONS: 'SET_CONFIGURATIONS';
  SET_CURRENT_CONFIGURATION: 'SET_CURRENT_CONFIGURATION';
  ADD_CONFIGURATION: 'ADD_CONFIGURATION';
  UPDATE_CONFIGURATION: 'UPDATE_CONFIGURATION';
  DELETE_CONFIGURATION: 'DELETE_CONFIGURATION';
  
  // Error mutations
  ADD_ERROR: 'ADD_ERROR';
  REMOVE_ERROR: 'REMOVE_ERROR';
  CLEAR_ERRORS: 'CLEAR_ERRORS';
}

// Action Types
export interface ActionTypes {
  // Auth actions
  LOGIN: 'login';
  LOGOUT: 'logout';
  TRY_LOGIN: 'tryLogin';
  LOAD_USERS: 'loadUsers';
  
  // Configuration actions
  LOAD_CONFIGURATIONS: 'loadConfigurations';
  SET_CURRENT_CONFIGURATION: 'setCurrentConfiguration';
  CREATE_CONFIGURATION: 'createConfiguration';
  UPDATE_CONFIGURATION: 'updateConfiguration';
  DELETE_CONFIGURATION: 'deleteConfiguration';
}

