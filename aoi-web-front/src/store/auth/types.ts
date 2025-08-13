// Auth Module Types

export interface AuthState {
  users: any[];
  token: any | null;
  currentUser: any | null;
  didAutoLogout: boolean;
  availableRoles: any[];
}
