// Core API Types for AOI Platform

export interface ApiResponse<T = any> {
  response: Response;
  responseData: T;
  ok: boolean;
  status: number;
  data?: T;
  _?: any;
  _2?: any;
  blob?: () => Promise<Blob>;
  headers?: Headers;
}

export interface StandardApiResponse<T = any> {
  data?: T;
  status: number;
  message?: string;
  error?: string;
}

export interface User {
  uid: string;
  username: string;
  level: 'admin' | 'user' | 'operator';
  password?: string; // Only for creation/update
}

export interface Configuration {
  uid: string;
  name: string;
  active: boolean;
  description?: string;
  created_at?: string;
  updated_at?: string;
}

export interface Algorithm {
  uid: string;
  name: string;
  type: string;
  parameters: Record<string, any>;
  enabled: boolean;
}

export interface Component {
  uid: string;
  name: string;
  type: string;
  x: number;
  y: number;
  width: number;
  height: number;
  rotation?: number;
  properties: Record<string, any>;
}

export interface CncPosition {
  x: number;
  y: number;
  z: number;
}

export interface CncModel {
  uid: string;
  name: string;
  type: string;
  port: string;
  connected: boolean;
  position?: CncPosition;
}

export interface LocationModel {
  uid: string;
  name: string;
  axisUid: string;
  x: number;
  y: number;
  z: number;
  feedrate: number;
  degreeInStep?: string;
}

export interface Camera {
  uid: string;
  name: string;
  type: string;
  connected: boolean;
  settings: Record<string, any>;
}

export interface ImageSource {
  uid: string;
  name: string;
  type: 'camera' | 'file' | 'generator';
  path?: string;
  settings: Record<string, any>;
}

export interface Inspection {
  uid: string;
  name: string;
  timestamp: string;
  result: 'pass' | 'fail' | 'pending';
  details: Record<string, any>;
  images?: string[];
}

export interface LogEvent {
  timestamp: string;
  user: string;
  type: string;
  title: string;
  description: string;
  details?: any[];
}

export interface Robot {
  uid: string;
  name: string;
  type: string;
  connected: boolean;
  position?: {
    x: number;
    y: number;
    z: number;
    rx: number;
    ry: number;
    rz: number;
  };
}

export interface MediaFile {
  uid: string;
  name: string;
  type: 'image' | 'video';
  path: string;
  size: number;
  created_at: string;
}

// Request/Response types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface CreateUserRequest {
  username: string;
  password: string;
  level: string;
}

export interface UpdateUserRoleRequest {
  uid: string;
  role: string;
}

// WebSocket message types
export interface WebSocketMessage<T = any> {
  event: string;
  data?: T;
  timestamp?: string;
  error?: string;
}

export interface CncWebSocketData {
  position: CncPosition;
  status: string;
  connected: boolean;
}

export interface ConfigurationWebSocketData {
  configuration: Configuration;
  action: 'created' | 'updated' | 'deleted' | 'selected';
}

