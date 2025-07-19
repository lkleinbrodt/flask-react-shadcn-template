## Codebase Improvement Recommendations

This is a strong and well-structured template. The following recommendations aim to enhance security, improve developer experience (DX), and align with modern best practices for full-stack applications.

# Important note:

When accomplishing this plan we are going to make changes to a lot of different parts of the codebase. It is imperative that we use best practice version control to ensure maintainability and ease of review. So, for each task/feature (or group of features if related) you should create a new branch, make your changes, and then open a PR to the main branch. Some features might build on other features, in that case you can branch a new feature branch off from that other feature branch.

### Backend (Flask) Recommendations

The backend is clean and follows good patterns. The suggestions here are mostly for added robustness and scalability.

#### 1. Enhance Authentication Security and Flow

**Issue:** The current OAuth callback redirects to the frontend with the access token in the URL query parameters (`/auth?access_token=...`). This is a security risk as the token can be exposed in browser history, server logs, or referrer headers.

**Recommendation:**
Modify the backend callback (`/api/auth/callback/<provider>`) to set the **access token as a cookie**, just like the refresh token. This cookie should be readable by JavaScript (i.e., not `HttpOnly`).

```python
# In backend/routes/auth.py -> oauth_callback()

# ... (user lookup/creation logic)

access_token = create_access_token(...)
refresh_token = create_refresh_token(...)

# Instead of redirecting with the token in the URL:
# redirect_url = f"{current_app.config['FRONTEND_URL']}/auth?access_token={access_token}..."

# NEW APPROACH: Set both tokens as cookies and redirect to a clean URL.
redirect_url = f"{current_app.config['FRONTEND_URL']}/auth/callback?next={next_path}"
response = make_response(redirect(redirect_url))

# Set refresh token as HttpOnly cookie (as it is now)
set_refresh_cookies(response, refresh_token)

# Set access token as a JS-readable cookie
# This requires a slight change in config to specify a different path if needed
# For simplicity, we'll use the same settings as the refresh token for now.
from flask_jwt_extended import set_access_cookies
set_access_cookies(response, access_token) # This will store it in 'access_token_cookie'

return response
```

**Why it's better:**

- **More Secure:** No tokens are exposed in URLs.
- **Cleaner Frontend Logic:** The frontend no longer needs to parse tokens from the URL, simplifying the `AuthPage.tsx` component.

#### 2. Implement a Centralized Error Handler

**Issue:** API errors currently use Flask's default handlers. While functional, a custom handler can ensure all API errors (validation, server, etc.) have a consistent JSON structure that the frontend can reliably parse.

**Recommendation:**
Create a global error handler in `backend/__init__.py` or a new `backend/errors.py` file.

```python
# In backend/__init__.py

def create_app(config_class: Config):
    app = Flask(__name__)
    # ... (other initializations)

    # Register error handler
    @app.errorhandler(Exception)
    def handle_exception(e):
        # Pass through HTTP exceptions
        if isinstance(e, HTTPException):
            return e
        # Handle non-HTTP exceptions
        # You can add logging here
        return jsonify(error="An unexpected error occurred. See server logs for details."), 500

    @app.errorhandler(404)
    def resource_not_found(e):
        return jsonify(error=str(e)), 404

    # ... (register blueprints)
    return app
```

**Why it's better:**

- **Consistency:** Guarantees a predictable error format (`{"error": "message"}`), which the frontend's `errorUtils.ts` can easily handle.
- **Centralized Logging:** Provides a single place to log all unhandled exceptions.

#### 3. Add a `/api/users/me` Endpoint

**Issue:** The frontend currently decodes the JWT to get user information. This is standard, but it means the user info can become stale if it's updated in the database (e.g., name change). It also leads to the frontend storing the user object in cookies, which is redundant.

**Recommendation:**
Create a dedicated, authenticated endpoint to fetch the current user's data.

```python
# In backend/routes/auth.py or a new backend/routes/user.py

from flask_jwt_extended import jwt_required, get_current_user

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_me():
    """Get the profile of the currently authenticated user."""
    user = get_current_user() # Relies on the user_lookup_loader
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "image": user.image,
    })
```

**Why it's better:**

- **Single Source of Truth:** The backend is always the source of truth for user data.
- **Simplifies Frontend:** The frontend can simply call this endpoint on app load to get the user, rather than storing a stale user object in cookies.

#### 4. Improve Testing Coverage

**Issue:** The `tests/` directory contains only a single "healthy" check. A template should provide a foundation for robust testing.

**Recommendation:**

- **Auth Tests:** Add tests for `login`, `refresh`, and `logout` endpoints. You will need to mock the external OAuth provider's responses.
- **Model Tests:** Write unit tests for model logic, e.g., testing the `debit` and `credit` methods in the `UserBalance` model.
- **Protected Route Tests:** Add tests for a protected endpoint (like the new `/api/users/me`) to ensure it fails without a token and succeeds with one.
- **Use Fixtures:** Expand `conftest.py` to include fixtures that create a test user and an authenticated test client.

**Advice**
The developer does not like using mocks / patches, these often get very messy and brittle. Try your best to avoid them or at least to make them as simple as possible. Furthermore, if you find yourself stuck in a loop with testing (especially when using mocks), simply stop work on that test, add a TODO comment that it needs to be implemented, and move on.

---

### Frontend (React) Recommendations

The frontend is modern, but the authentication flow can be significantly streamlined for a better user and developer experience.

#### 1. Drastically Simplify the Authentication Flow

**Issue:** The current flow relies on a dedicated `/auth` page, full page reloads, and storing the user object in cookies. This is complex and results in a jarring UX.

**Recommendation:**
Adopt a modern, Single-Page Application (SPA) friendly auth flow, especially after implementing the backend changes above.

1.  **Refactor `AuthContext.tsx`:**

    - On initial load, `AuthContext` should check for the presence of the `access_token_cookie`.
    - If the cookie exists but `state.user` is `null`, call the new `/api/users/me` endpoint to fetch the user profile. Set a `loading: true` state during this fetch.
    - The `user` object should **not** be stored in cookies anymore. The `accessToken` and `refreshToken` cookies are the only session state needed on the client.
    - The `login()` function should remain, but the callback page (`/auth/callback`) will be simpler.

2.  **Simplify `AuthPage.tsx` (now `AuthCallbackPage.tsx`):**

    - Rename `AuthPage.tsx` to something like `AuthCallbackPage.tsx` and map it to `/auth/callback`.
    - Its only purpose is to act as a landing spot after the backend redirect. It can then navigate the user to the `next` path.
    - The main `AuthContext` on the target page will handle fetching the user data.

    ```typescript
    // In a new AuthCallbackPage.tsx
    import { useEffect } from "react";
    import { useNavigate, useSearchParams } from "react-router-dom";

    const AuthCallbackPage = () => {
      const navigate = useNavigate();
      const [searchParams] = useSearchParams();

      useEffect(() => {
        const next = searchParams.get("next") || "/";
        // The tokens are already set as cookies by the backend.
        // We just need to navigate, and the AuthContext will handle the rest.
        navigate(next, { replace: true });
      }, [navigate, searchParams]);

      return <div>Finalizing login...</div>;
    };
    ```

**Why it's better:**

- **Seamless UX:** No more full-page reloads after login. The app state updates smoothly.
- **Simplified Logic:** Removes the need to pass tokens in URLs and manage user objects in cookies.
- **Robust State:** The application state is derived from a single source of truth (the auth cookies) on every load.

#### 2. Introduce a Data Fetching Library (e.g., TanStack Query)

**Issue:** Data fetching logic is manual (`useEffect`, `useState`). This leads to repetitive boilerplate for handling loading, error, and data states.

**Recommendation:**
Integrate **TanStack Query (formerly React Query)**. It's the industry standard for data fetching in React and would massively simplify the codebase.

**Example with `AuthContext`:**

```typescript
// In AuthContext.tsx, using TanStack Query
import { useQuery } from "@tanstack/react-query";
import { authService } from "@/services/auth"; // authService would have a 'getMe()' method

export function AuthProvider({ children }) {
  const {
    data: user,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["user"], // Unique key for this query
    queryFn: authService.getMe, // The function that fetches data
    retry: false, // Don't retry on auth errors
    refetchOnWindowFocus: false, // Optional: prevent refetching on window focus
  });

  // ... rest of the context provider logic
  // The 'user' object, loading state, and error state are now managed by TanStack Query.
}
```

**Why it's better:**

- **Less Code:** Eliminates manual `loading`, `error`, `data` states.
- **Caching:** Automatically caches data, improving performance and reducing redundant API calls.
- **Developer Experience:** Provides dedicated devtools for inspecting queries and cache.

#### 3. Refine Type Definitions

**Issue:** The `User` type in `frontend/src/types/auth.ts` includes a `token`. This is an anti-pattern; the token is a transport-layer concern, not an attribute of the user model.

**Recommendation:**
Remove the `token` property from the `User` interface.

```typescript
// frontend/src/types/auth.ts
export interface User {
  id: number;
  email: string;
  name: string;
  image: string;
  // token: string; // <-- REMOVE THIS
}
```

**Why it's better:**

- **Separation of Concerns:** The user's identity (`User` object) is separate from their session credentials (`token`).
- **Clarity:** Makes the data model cleaner and more accurate.

---

### General Project & DevOps Recommendations

#### 1. Implement CI/CD with GitHub Actions

**Issue:** There are no automated checks for code quality or tests.

**Recommendation:**
Create a `.github/workflows/ci.yml` file. This workflow should:

- Trigger on every push and pull request.
- Set up both Python and Node.js environments.
- Run linters (e.g., Ruff for Python, ESLint for TypeScript).
- Run the test suites for both the backend and frontend.

**Why it's better:**

- **Automated Quality Control:** Catches bugs and style issues early.
- **Confidence:** Ensures the main branch is always in a deployable state.
