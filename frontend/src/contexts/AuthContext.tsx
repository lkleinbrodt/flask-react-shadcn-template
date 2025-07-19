import type { User } from "@/types/auth";
import {
  type ReactNode,
  createContext,
  useCallback,
  useContext,
} from "react";
import { useQuery } from "@tanstack/react-query";
import Cookies from "js-cookie";
import { authService } from "@/services/auth";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: Error | null;
  logout: () => Promise<void>;
  login: (from?: string) => Promise<void>;
  isAuthenticated: () => boolean;
  refetch: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  // Check if we have an access token to determine if we should fetch user data
  const hasAccessToken = !!Cookies.get("access_token_cookie");
  
  // Use TanStack Query to fetch user data if we have a token
  const {
    data: user,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["user"],
    queryFn: authService.getMe,
    enabled: hasAccessToken, // Only fetch if we have a token
    retry: false, // Don't retry on auth errors
    refetchOnWindowFocus: false, // Don't refetch on window focus
    staleTime: 5 * 60 * 1000, // Consider data fresh for 5 minutes
  });

  const logout = async () => {
    // Clear any cached user data
    refetch();
    // Call authService.logout which will clear client cookies and redirect
    await authService.logout();
  };

  const login = async (from: string = "/") => {
    try {
      authService.initiateLogin("google", from);
    } catch (err) {
      console.error("Failed to initiate login:", err);
      throw new Error("Failed to initiate login");
    }
  };

  const isAuthenticated = useCallback(() => {
    return !!user && !!Cookies.get("access_token_cookie");
  }, [user]);

  return (
    <AuthContext.Provider
      value={{
        user: user || null,
        loading: isLoading,
        error: error || null,
        logout,
        login,
        isAuthenticated,
        refetch,
      }}
    >
      {children}
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
