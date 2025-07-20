export interface User {
  id: number;
  email: string;
  name: string;
  image: string;
  // token: string; // REMOVED: No longer storing tokens in JS
}

export interface UserCredentials {
  email: string;
  password?: string; // Optional for OAuth cases
  name?: string; // Optional for registration
}

export interface AuthError {
  message: string;
  code?: string;
}

export interface AuthResponse {
  access_token: string;
  user: User;
}

export interface AuthState {
  user: User | null;
  loading: boolean;
  error: AuthError | null;
}
