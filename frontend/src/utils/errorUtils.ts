import axios, { AxiosError } from "axios";

import { toast } from "@/hooks/use-toast";

export type ApiErrorType =
  | "validation"
  | "auth"
  | "server"
  | "network"
  | "unknown";

export interface ApiErrorResponse {
  type: ApiErrorType;
  message: string;
  errors?: Record<string, string[]>;
}

interface ErrorResponseData {
  message?: string;
  errors?: Record<string, string[]>;
}

/**
 * Handles API errors and returns a standardized error response
 */
export const handleApiError = (error: unknown): ApiErrorResponse => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ErrorResponseData>;

    if (axiosError.response) {
      // Server responded with a status code outside of 2xx range
      const { status, data } = axiosError.response;

      if (status === 400) {
        return {
          type: "validation",
          message: data?.message || "Validation error",
          errors: data?.errors || {},
        };
      } else if (status === 401) {
        return {
          type: "auth",
          message: "Authentication required",
        };
      } else if (status === 403) {
        return {
          type: "auth",
          message: "You don't have permission to perform this action",
        };
      } else if (status === 404) {
        return {
          type: "server",
          message: "Resource not found",
        };
      } else {
        return {
          type: "server",
          message: data?.message || `Server error (${status})`,
        };
      }
    } else if (axiosError.request) {
      // Request was made but no response received
      return {
        type: "network",
        message: "Network error - please check your connection",
      };
    }
  }

  // Something else happened
  const errorMessage =
    error instanceof Error ? error.message : "An unknown error occurred";
  return {
    type: "unknown",
    message: errorMessage,
  };
};

/**
 * Handles API errors, displays toast notification, and returns a standardized error response
 * @param error The error object
 * @param operation Optional operation name to include in the toast title
 * @returns ApiErrorResponse object
 */
export const handleApiErrorWithToast = (
  error: unknown,
  operation?: string
): ApiErrorResponse => {
  const apiError = handleApiError(error);

  const title = operation
    ? `Error ${operation}`
    : getErrorTypeTitle(apiError.type);

  toast({
    title,
    description: apiError.message,
  });

  return apiError;
};

/**
 * Get a human-readable title based on error type
 */
const getErrorTypeTitle = (type: ApiErrorType): string => {
  switch (type) {
    case "validation":
      return "Validation Error";
    case "auth":
      return "Authentication Error";
    case "server":
      return "Server Error";
    case "network":
      return "Network Error";
    default:
      return "Error";
  }
};

/**
 * Extracts form field errors from an API error response
 */
export const getFormErrors = (
  apiError: ApiErrorResponse
): Record<string, string> => {
  if (apiError.type !== "validation" || !apiError.errors) {
    return {};
  }

  const formErrors: Record<string, string> = {};

  // Convert API error format (field => string[]) to form error format (field => string)
  Object.entries(apiError.errors).forEach(([field, messages]) => {
    if (messages && messages.length > 0) {
      formErrors[field] = messages[0];
    }
  });

  return formErrors;
};

/**
 * Format validation errors for display in forms
 */
export const formatValidationErrors = (
  errors: Record<string, string[]>
): string => {
  if (!errors || Object.keys(errors).length === 0) {
    return "Invalid data provided";
  }

  return Object.entries(errors)
    .map(([field, messages]) => {
      const fieldName = field.replace(/_/g, " ");
      return `${fieldName}: ${messages.join(", ")}`;
    })
    .join("\n");
};

/**
 * Generic error handler for async functions
 * @param asyncFn The async function to execute
 * @param options Configuration options
 * @returns The result of the async function or null if an error occurred
 */
export const withErrorHandling = async <T>(
  asyncFn: () => Promise<T>,
  options?: {
    onError?: (error: ApiErrorResponse) => void;
    showToast?: boolean;
    operationName?: string;
  }
): Promise<T | null> => {
  try {
    return await asyncFn();
  } catch (error) {
    const apiError = handleApiError(error);

    // Show toast notification if requested
    if (options?.showToast !== false) {
      const title = options?.operationName
        ? `Error ${options.operationName}`
        : getErrorTypeTitle(apiError.type);

      toast({
        title,
        description: apiError.message,
      });
    }

    if (options?.onError) {
      options.onError(apiError);
    } else {
      console.error(apiError.message);
    }

    return null;
  }
};
