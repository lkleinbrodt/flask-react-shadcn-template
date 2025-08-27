import type { User, UserCredentials } from "@/types/auth";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";

import type { ReactNode } from "react";
import { authService } from "@/services/auth";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (credentials: UserCredentials) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchUser = useCallback(async () => {
    try {
      // Since cookies are HttpOnly, we can't check them from JavaScript
      // Just try to fetch the user data - if there are valid cookies, it will work
      // If not, we handle the 401 gracefully
      const userData = await authService.getMe();
      setUser(userData);
    } catch (error) {
      // This means no valid token, so no user.
      // Only log if it's not a 401 (expected for unauthenticated users)
      if (error && typeof error === "object" && "response" in error) {
        const axiosError = error as { response?: { status?: number } };
        if (axiosError.response?.status !== 401) {
          console.error("Error fetching user:", error);
        }
      } else {
        // Log unexpected error types
        console.error("Unexpected error type when fetching user:", error);
      }
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  const login = async (credentials: UserCredentials) => {
    setLoading(true);
    try {
      const userData = await authService.login(credentials);
      setUser(userData);
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    setLoading(true); // Prevent any new fetchUser calls during logout
    await authService.logout();
    setUser(null);
    setLoading(false);
    // Optional: redirect to login page
    window.location.href = "/login";
  };

  const value = { user, loading, login, logout };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
