# Full-Stack Web App Template (Flask + React + Shadcn/ui)

This repository is a template for building modern, full-stack web applications. It combines a Python/Flask backend with a React/Vite frontend, featuring a robust authentication system and a clean, scalable structure.

The primary goal of this template is to provide a solid foundation with pre-configured essentials like authentication, API communication, and UI components, allowing you to focus on building features.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
  - [Environment Variables](#environment-variables)
- [Project Architecture](#project-architecture)
  - [Backend (Flask)](#backend-flask)
  - [Frontend (React)](#frontend-react)
- [Key Workflows & Patterns](#key-workflows--patterns)
  - [Authentication Flow (OAuth + JWT)](#authentication-flow-oauth--jwt)
  - [Making Authenticated API Calls](#making-authenticated-api-calls)
  - [Handling API Errors](#handling-api-errors)
- [Customization](#customization)

## Features

- **Full-Stack Monorepo:** A single repository containing both the `backend` and `frontend` applications.
- **Flask Backend:** A scalable backend built with Flask, using an application factory pattern.
- **React Frontend:** A modern, fast UI built with React, Vite, and TypeScript.
- **JWT Authentication:** Secure authentication using JWT access and refresh tokens.
- **OAuth 2.0:** Pre-configured Google Sign-In for easy user onboarding.
- **Database Ready:** Uses Flask-SQLAlchemy and Flask-Migrate for database operations and schema management.
- **Modern UI:** Comes with [shadcn/ui](https://ui.shadcn.com/) for beautiful, accessible, and customizable components.
- **Centralized API Client:** A pre-configured Axios instance that handles token management and automatic token refreshing.
- **Billing Integration:** Includes models and API stubs for Stripe payments and user credit management.
- **Automated Setup:** A single `setup.sh` script to install all dependencies, set up the database, and start both servers.

## Tech Stack

- **Backend:**
  - **Framework:** Flask
  - **Authentication:** Flask-JWT-Extended
  - **ORM:** Flask-SQLAlchemy
  - **Database Migrations:** Flask-Migrate (Alembic)
  - **CORS:** Flask-Cors
  - **OAuth:** Rauth
- **Frontend:**
  - **Framework:** React 19
  - **Build Tool:** Vite
  - **Language:** TypeScript
  - **UI Library:** shadcn/ui, Tailwind CSS
  - **Routing:** React Router DOM
  - **API Client:** Axios
- **Database:** SQLite (for development), configurable for PostgreSQL in production.

## Getting Started

### Prerequisites

- Python 3.8+ and `pip`
- Node.js 18+ and `npm`

### Setup

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd flask-react-shadcn-template
    ```

2.  **Set up Environment Variables:**
    Create the necessary environment files before running the setup script. See the [Environment Variables](#environment-variables) section below for details.

3.  **Run the setup script:**
    This script automates the entire setup process.
    ```bash
    bash setup.sh
    ```
    The script performs the following actions:
- Validates Python 3.8+ and Node.js 18+ versions
- Creates a Python virtual environment (`venv/`)
- Installs all Python dependencies from `backend/requirements.txt`
- Initializes the database and applies migrations with error handling
- Installs all Node.js dependencies for the frontend
- Starts both the Flask backend (on `http://localhost:5000`) and the Vite frontend (on `http://localhost:5173`)
- Provides detailed error messages and validation throughout the process

### Environment Variables

You need to create two environment files:

1.  **Backend (`.env`):** Create this file in the project root.

    ```env
    # .env
    # A strong, random string for signing sessions and JWTs.
    SECRET_KEY=your_super_secret_key

    # Google OAuth Credentials (both must be set for OAuth to work)
    GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
    GOOGLE_CLIENT_SECRET=your_google_client_secret

    # Stripe Test Keys (optional, for billing)
    STRIPE_PUBLISHABLE_KEY_TESTING=pk_test_...
    STRIPE_SECRET_KEY_TESTING=sk_test_...
    STRIPE_WEBHOOK_SECRET=whsec_...
    
    # Production Database (required for production deployment)
    # DATABASE_URL=postgresql://user:password@localhost/dbname

    # Email Server Configuration (for password reset)
    # Example for SendGrid (use 'smtp.gmail.com' for Gmail, etc.)
    MAIL_SERVER=smtp.sendgrid.net
    MAIL_PORT=587
    MAIL_USE_TLS=true
    MAIL_USERNAME=apikey  # For SendGrid, the username is literally 'apikey'
    MAIL_PASSWORD=your_sendgrid_api_key
    MAIL_DEFAULT_SENDER="Your Name <noreply@yourdomain.com>"
    
    # JWT Cookie Security (optional, defaults to false for development)
    JWT_COOKIE_SECURE=false
    
    # CORS Origins for Production (comma-separated list)
    # CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
    ```

2.  **Frontend (`frontend/.env.development`):** Create this file inside the `frontend` directory.
    ```env
    # frontend/.env.development
    VITE_BASE_URL=http://127.0.0.1:5000/
    ```

## Project Architecture

### Backend (Flask)

The backend is structured to be modular and scalable.

- **`app.py`**: The main entry point for the Flask application. It uses the `create_app` factory from `backend/__init__.py`.
- **`config.py`**: Defines configuration classes for different environments (Development, Production, Testing). Environment variables are loaded here.
- **`extensions.py`**: Initializes and exports Flask extensions (`db`, `jwt`, `migrate`, `cors`) to avoid circular imports.
- **`models/`**: Contains all SQLAlchemy database models.
  - `user.py`: The `User` model.
  - `billing.py`: `UserBalance` and `Transaction` models for Stripe integration.
- **`routes/`**: Defines API endpoints using Flask Blueprints.
  - `__init__.py`: Aggregates all blueprints. Note the `api_bp` which prefixes all API routes with `/api`.
  - `auth.py`: Handles all authentication-related endpoints (`/api/auth/...`).
  - `billing.py`: Handles payment and balance endpoints (`/api/billing/...`).
- **`src/`**: Contains business logic and services not directly tied to a route.
  - `OAuthSignIn.py`: A class-based implementation for handling different OAuth providers.

### Frontend (React)

The frontend uses Vite for a fast development experience and is structured by feature/domain.

- **`main.tsx`**: The entry point for the React application.
- **`App.tsx`**: Sets up the main application structure, including routing and context providers.
- **`src/components/`**:
  - `ui/`: Contains the UI components from **shadcn/ui**. These are foundational and unstyled.
  - `common/`: Contains application-specific, reusable components like `Layout.tsx` and `FloatingNav.tsx`.
- **`src/contexts/`**:
  - `AuthContext.tsx`: Manages global authentication state (`user`, `loading`, etc.). Components access this via the `useAuth()` hook.
- **`src/hooks/`**:
  - `use-toast.ts`: A custom hook for displaying toast notifications, accessible via `useToast()`.
- **`src/pages/`**: Top-level components that correspond to a page/route (e.g., `HomePage.tsx`, `AuthPage.tsx`).
- **`src/services/`**:
  - `auth.ts`: A dedicated service for handling authentication logic, like initiating login, handling the callback, and logging out.
- **`src/utils/`**:
  - `axiosInstance.tsx`: A crucial file that exports a pre-configured Axios instance for all API calls.
  - `errorUtils.ts`: Helper functions to parse and display API errors.

## Key Workflows & Patterns

This section explains how common tasks are implemented, which is essential for an AI agent to understand the coding style.

### Authentication Flow (HttpOnly Cookies)

This template uses a secure, modern authentication pattern where JWTs (Access and Refresh tokens) are stored in `HttpOnly`, `Secure` cookies. This is a best practice that protects against XSS attacks. The frontend code never touches the tokens directly.

1.  **Initiation (Frontend):** A user navigates to the `/login` page or clicks a "Login with Google" button.
2.  **Authentication Request:**
    - **Password Login:** The frontend sends credentials to `/api/auth/login`.
    - **OAuth Login:** The browser is redirected to `/api/auth/authorize/google`, which in turn redirects to Google's OAuth screen.
3.  **Token Generation (Backend):** After successful authentication (either via password check or OAuth callback), the Flask backend generates a short-lived **JWT access token** and a long-lived **JWT refresh token**.
4.  **Set Secure Cookies (Backend):** The backend sets the tokens in two separate `HttpOnly` cookies. The browser will now automatically include these cookies on all subsequent requests to the API.
5.  **Redirect to Frontend:** The backend redirects the user back to the frontend application (e.g., to `/auth/callback` which then redirects to `/`).
6.  **Authenticated State (Frontend):**
    - The `AuthContext` provider loads. Since it cannot read the `HttpOnly` cookies, it sends a request to the `/api/auth/me` endpoint.
    - The browser automatically attaches the `access_token_cookie`.
    - The backend validates the JWT and returns the user's data (`id`, `name`, `email`).
    - The `AuthContext` sets the user state, and the application now reflects that the user is logged in.
7.  **Automatic Token Refresh:** If an API call fails with a `401 Unauthorized` error (meaning the access token expired), a pre-configured `axios` interceptor automatically makes a request to `/api/auth/refresh`. The browser sends the `refresh_token_cookie`, the backend issues a new set of tokens, and the original failed request is retried seamlessly.

### Making Authenticated API Calls

All API communication should use the pre-configured Axios instance.

**File:** `frontend/src/utils/axiosInstance.tsx`

```typescript
import axiosInstance from "@/utils/axiosInstance";

// Example: Fetching user profile
async function fetchProfile() {
  try {
    const response = await axiosInstance.get("/profile"); // The base /api is already included
    return response.data;
  } catch (error) {
    // Error handling
  }
}
```

**How it Works:**

1.  **Request Interceptor:** Automatically adds the CSRF token to the `X-CSRF-TOKEN` header for requests that require CSRF protection.
2.  **Response Interceptor (Token Refresh):**
    - If an API call returns a `401 Unauthorized` error, it means the access token has expired.
    - The interceptor automatically calls the `/api/auth/refresh` endpoint. The browser sends the `HttpOnly` refresh token cookie automatically.
    - If successful, the backend sets new `HttpOnly` cookies, and the interceptor **transparently retries the original failed request.**
    - If the refresh fails, it redirects the user to the login page.

This pattern means you **do not need to manually handle token refreshing** in your components or services. The `HttpOnly` cookies are managed entirely by the browser and backend.

### Handling API Errors

A set of utility functions is provided to standardize error handling.

**File:** `frontend/src/utils/errorUtils.ts`

**Usage:**

```typescript
import { handleApiErrorWithToast } from "@/utils/errorUtils";

async function saveData(data) {
  try {
    await axiosInstance.post("/my-data", data);
  } catch (error) {
    // This will parse the error and show a toast notification.
    handleApiErrorWithToast(error, "while saving data");
  }
}
```

This ensures consistent error messages and user feedback across the application.

## Recent Improvements

This template has been enhanced with the following improvements:

- **Port Consistency**: Backend now consistently runs on port 5000
- **OAuth Validation**: Graceful handling of missing OAuth credentials with warnings
- **Configurable CORS**: CORS origins are now configurable per environment
- **Environment Validation**: Production database URL is required and validated
- **Enhanced Error Handling**: Better error logging and validation throughout
- **Setup Script Robustness**: Improved error handling and validation in setup process
- **Type Safety**: Better TypeScript error handling and type guards

## Customization

To adapt this template for your new project:

1.  **Rename the Project:** Search and replace all instances of `PLACEHOLDER_PROJECT_NAME` in the following files:

    - `frontend/package.json`
    - `frontend/src/components/common/Header.tsx`
    - `frontend/src/components/common/FloatingNav.tsx`
    - `frontend/src/pages/HomePage.tsx`
    - `frontend/index.html`

2.  **Update Database Configuration:** In `backend/config.py`, change the `SQLALCHEMY_DATABASE_URI` for `ProductionConfig` to your production database URL (e.g., PostgreSQL).

3.  **Modify UI Components:** Add or modify components in `frontend/src/components/common/` and pages in `frontend/src/pages/`.

4.  **Add New API Routes:**
    - Create new models in `backend/models/`.
    - Create a new blueprint file in `backend/routes/`.
    - Register the new blueprint in `backend/routes/__init__.py` under the `api_bp`.
    - Run `flask db migrate -m "Add new models"` and `flask db upgrade` to update the database schema.
