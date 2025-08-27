import Cookies from "js-cookie";
import axios from "axios";

// Add a custom property to the AxiosRequestConfig interface
declare module "axios" {
  export interface AxiosRequestConfig {
    _suppressRedirect?: boolean;
  }
}

const axiosInstance = axios.create({
  baseURL: `${import.meta.env.VITE_BASE_URL}api`,
  // This ensures the browser sends HttpOnly cookies with each request
  withCredentials: true,
});

// Request Interceptor to add CSRF token to headers
axiosInstance.interceptors.request.use((config) => {
  const csrfToken = Cookies.get("csrf_access_token");
  if (csrfToken) {
    config.headers["X-CSRF-TOKEN"] = csrfToken;
  }
  return config;
});

// Response Interceptor for automatic token refresh
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Check if the error is a 401, it's not a retry, and we should handle it automatically
    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !originalRequest._suppressRedirect
    ) {
      originalRequest._retry = true; // Mark as retried to prevent infinite loops

      try {
        // The refresh token cookie is sent automatically by the browser
        await axiosInstance.post("/auth/refresh");
        // Retry the original request with the new access token
        return axiosInstance(originalRequest);
      } catch (refreshError) {
        // Only log unexpected refresh errors, not the expected 401s
        if (
          refreshError &&
          typeof refreshError === "object" &&
          "response" in refreshError
        ) {
          const axiosRefreshError = refreshError as {
            response?: { status?: number };
          };
          if (axiosRefreshError.response?.status !== 401) {
            console.error("Token refresh failed:", refreshError);
          }
        }
        
        // Log the specific error for debugging
        if (refreshError && typeof refreshError === "object" && "message" in refreshError) {
          console.error("Token refresh error details:", {
            message: (refreshError as any).message,
            status: (refreshError as any).response?.status,
            url: (refreshError as any).config?.url
          });
        }

        // **THIS IS THE KEY CHANGE**
        // Only redirect if the original request did NOT have the suppress flag.
        if (
          !originalRequest._suppressRedirect &&
          window.location.pathname !== "/login"
        ) {
          console.log(
            "Redirecting to login for protected endpoint:",
            originalRequest.url
          );
          window.location.href = "/login";
        }

        // If the flag was present, we just reject the promise and let the
        // calling function handle the error gracefully.
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default axiosInstance;
