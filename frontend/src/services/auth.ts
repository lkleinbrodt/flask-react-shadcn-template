import Cookies from "js-cookie";
import type { User } from "@/types/auth";
import axiosInstance from "@/utils/axiosInstance";

// Define UserProfile type without the token, as token is managed separately
export interface UserProfile {
  id: string;
  email: string;
  name: string;
  image: string;
}

// Response from the /auth/refresh endpoint
export interface RefreshAuthResponse {
  access_token: string;
}

export const authService = {
  /**
   * Initiates the OAuth login flow by redirecting to the backend.
   * @param provider - The OAuth provider (e.g., "google").
   * @param nextPath - The path to redirect to after successful login.
   */
  initiateLogin: (provider: string, nextPath: string = "/"): void => {
    const encodedPath = encodeURIComponent(nextPath);
    window.location.href = `${
      import.meta.env.VITE_BASE_URL
    }api/auth/authorize/${provider}?next=${encodedPath}`;
  },

  /**
   * DEPRECATED: This method is no longer needed with the new authentication flow.
   * Tokens are now set directly as cookies by the backend.
   */
  handleLoginSuccess: (accessToken: string): UserProfile => {
    console.warn("handleLoginSuccess is deprecated - tokens are now set by backend");
    // Legacy method kept for backward compatibility but not used in new flow
    const decodedPayload = JSON.parse(atob(accessToken.split(".")[1]));
    return {
      id: decodedPayload.sub,
      email: decodedPayload.email,
      name: decodedPayload.name,
      image: decodedPayload.image || decodedPayload.picture,
    };
  },

  /**
   * Calls the backend logout endpoint and clears client-side authentication data.
   */
  logout: async (): Promise<void> => {
    // Clear client-side auth data immediately for faster UI response
    authService.clearClientSideCookies();

    // Navigate to the backend logout endpoint which will handle redirect
    window.location.href = `${import.meta.env.VITE_BASE_URL}api/auth/logout`;
  },

  /**
   * Clears all client-side authentication cookies and storage.
   * Useful for immediate UI feedback during logout process.
   */
  clearClientSideCookies: (): void => {
    // Clear legacy cookies for backward compatibility
    Cookies.remove("accessToken");
    Cookies.remove("user");
    // Clear new auth cookies (will be cleared by backend but good to be explicit)
    Cookies.remove("access_token_cookie");
    Cookies.remove("refresh_token_cookie");
    localStorage.removeItem("authError"); // Any stored auth errors
  },

  /**
   * DEPRECATED: This method is no longer needed with TanStack Query approach.
   * User data is now fetched fresh from the server when needed.
   */
  getCurrentUserProfile: (): User | null => {
    console.warn("getCurrentUserProfile is deprecated - use TanStack Query in AuthContext instead");
    return null;
  },

  /**
   * Fetches the current user data from the backend using the /api/users/me endpoint.
   * This ensures we always have fresh user data from the server.
   */
  getMe: async (): Promise<UserProfile> => {
    try {
      const response = await axiosInstance.get<UserProfile>("/auth/me");
      return response.data;
    } catch (err) {
      console.error("Failed to fetch user data:", err);
      throw new Error("Failed to fetch user data");
    }
  },

  /**
   * Manually refresh the access token.
   * Note: This is now primarily handled by the axios interceptor.
   */
  refreshToken: async (): Promise<RefreshAuthResponse> => {
    try {
      const response = await axiosInstance.post<RefreshAuthResponse>(
        "/auth/refresh"
      );

      // The new access token is automatically set as a cookie by the backend
      // No need to manually manage cookies in the new flow
      return response.data;
    } catch (err) {
      console.error("Failed to refresh token:", err);
      throw new Error("Failed to refresh token");
    }
  },
};
