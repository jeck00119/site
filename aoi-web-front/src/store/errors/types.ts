// Error Module Types

export interface ErrorItem {
  id: string;
  message: string;
  type?: 'error' | 'warning' | 'info';
  timestamp?: number;
  details?: any;
}

export interface ErrorsState {
  errors: ErrorItem[];
}

export interface ErrorsGetters {
  getErrors: (state: ErrorsState) => ErrorItem[];
  isEmpty: (state: ErrorsState) => boolean;
  numberOfErrors: (state: ErrorsState) => number;
  hasErrors: (state: ErrorsState) => boolean;
}

export interface ErrorsMutations {
  removeError: (state: ErrorsState, id: string) => void;
  addError: (state: ErrorsState, payload: ErrorItem) => void;
  clearAllErrors: (state: ErrorsState) => void;
}

export interface ErrorsActions {
  removeError: (context: any, payload: { errorId: string }) => void;
  addError: (context: any, payload: ErrorItem) => void;
  clearErrors: (context: any) => void;
}