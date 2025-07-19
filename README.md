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
    - Creates a Python virtual environment (`venv/`).
    - Installs all Python dependencies from `backend/requirements.txt`.
    - Initializes the database and applies migrations.
    - Installs all Node.js dependencies for the frontend.
    - Starts both the Flask backend (on `http://localhost:5002`) and the Vite frontend (on `http://localhost:5173`).

### Environment Variables

You need to create two environment files:

1.  **Backend (`.env`):** Create this file in the project root.

    ```env
    # .env
    # A strong, random string for signing sessions and JWTs.
    SECRET_KEY=your_super_secret_key

    # Google OAuth Credentials
    GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
    GOOGLE_CLIENT_SECRET=your_google_client_secret

    # Stripe Test Keys (optional, for billing)
    STRIPE_PUBLISHABLE_KEY_TESTING=pk_test_...
    STRIPE_SECRET_KEY_TESTING=sk_test_...
    STRIPE_WEBHOOK_SECRET=whsec_...
    ```

2.  **Frontend (`frontend/.env.development`):** Create this file inside the `frontend` directory.
    ```env
    # frontend/.env.development
    VITE_BASE_URL=http://127.0.0.1:5002/
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

### Authentication Flow (OAuth + JWT)

The authentication flow is a multi-step process between the frontend and backend.

1.  **Initiation (Frontend):** A user clicks a "Login" button. This calls the `login()` function from the `useAuth` hook.
2.  **Redirect to Backend:** `authService.initiateLogin()` redirects the browser to the backend endpoint: `/api/auth/authorize/<provider>`.
3.  **OAuth Dance (Backend):** The backend endpoint (`/api/auth/authorize/...`) redirects the user to the OAuth provider (e.g., Google).
4.  **Callback to Backend:** After successful authentication, the provider redirects back to the backend callback URL: `/api/auth/callback/<provider>`.
5.  **Token Generation (Backend):** The callback endpoint:
    - Receives user info from the provider.
    - Creates or updates the `User` in the database.
    - Generates a short-lived **JWT access token** and a long-lived **JWT refresh token**.
    - Sets the **refresh token** as a secure, `HttpOnly` cookie.
    - Redirects the browser back to the frontend, passing the **access token** as a URL parameter: `http://localhost:5173/auth?access_token=...`.
6.  **Token Storage (Frontend):**
    - The `/auth` route renders `AuthPage.tsx`.
    - This page grabs the access token from the URL.
    - `authService.handleLoginSuccess()` stores the access token in a standard browser cookie.
    - It then performs a full page reload to the home page (`/`).
7.  **Authenticated State:** The `AuthContext` initializes, reads the user data and access token from cookies, and the user is now logged in.

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

1.  **Request Interceptor:** Automatically attaches the `Authorization: Bearer <token>` header to every outgoing request by reading the `accessToken` cookie.
2.  **Response Interceptor (Token Refresh):**
    - If an API call returns a `401 Unauthorized` error, it means the access token has expired.
    - The interceptor automatically calls the `/api/auth/refresh` endpoint using the `HttpOnly` refresh token cookie.
    - If successful, it receives a new access token, updates the `accessToken` cookie, and **transparently retries the original failed request.**
    - If the refresh fails, it logs the user out.

This pattern means you **do not need to manually handle token refreshing** in your components or services.

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
