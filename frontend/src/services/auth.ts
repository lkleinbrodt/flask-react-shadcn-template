import type { User, UserCredentials } from "@/types/auth";

import axiosInstance from "@/utils/axiosInstance";

interface GetMeResponse {
  user: User;
}

interface AuthMessageResponse {
  message: string;
}

export const authService = {
  initiateOAuthLogin: (provider: string): void => {
    window.location.href = `${
      import.meta.env.VITE_BASE_URL
    }api/auth/authorize/${provider}`;
  },

  login: async (credentials: UserCredentials): Promise<User> => {
    const response = await axiosInstance.post<GetMeResponse>(
      "/auth/login",
      credentials
    );
    return response.data.user;
  },

  register: async (credentials: UserCredentials): Promise<void> => {
    await axiosInstance.post("/auth/register", credentials);
  },

  logout: async (): Promise<void> => {
    // First, try to revoke the access token
    try {
      await axiosInstance.post("/auth/logout", {}, { _suppressRedirect: true });
    } catch (error) {
      // If access token is invalid, continue to refresh token revocation
      if (error && typeof error === "object" && "response" in error) {
        const axiosError = error as { response?: { status?: number } };
        console.warn(`Access token logout failed (status: ${axiosError.response?.status}), trying refresh token logout`);
      } else {
        console.warn("Access token logout failed with unexpected error type, trying refresh token logout");
      }
    }

    // Then, try to revoke the refresh token
    try {
      await axiosInstance.post(
        "/auth/logout/refresh",
        {},
        { _suppressRedirect: true }
      );
    } catch (error) {
      // If refresh token is also invalid, that's fine - user is already logged out
      if (error && typeof error === "object" && "response" in error) {
        const axiosError = error as { response?: { status?: number } };
        console.warn(`Refresh token logout failed (status: ${axiosError.response?.status}), user may already be logged out`);
      } else {
        console.warn("Refresh token logout failed with unexpected error type, user may already be logged out");
      }
    }
  },

  getMe: async (): Promise<User> => {
    // **ADD THE CUSTOM CONFIG OBJECT HERE**
    const response = await axiosInstance.get<GetMeResponse>("/auth/me", {
      _suppressRedirect: true, // This tells our interceptor to not redirect on failure
    });
    return response.data.user;
  },

  forgotPassword: async (email: string): Promise<AuthMessageResponse> => {
    const response = await axiosInstance.post<AuthMessageResponse>(
      "/auth/forgot-password",
      { email }
    );
    return response.data;
  },

  resetPassword: async (
    token: string,
    password: string
  ): Promise<AuthMessageResponse> => {
    const response = await axiosInstance.post<AuthMessageResponse>(
      `/auth/reset-password/${token}`,
      { password }
    );
    return response.data;
  },
};
