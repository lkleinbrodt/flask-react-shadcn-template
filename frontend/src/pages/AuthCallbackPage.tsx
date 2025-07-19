import { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { isValidRedirectPath } from "@/utils/routes";

const AuthCallbackPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const next = searchParams.get("next") || "/";
    
    // Validate the redirect path for security
    const redirectTo = isValidRedirectPath(next) ? next : "/";
    
    // The tokens are already set as cookies by the backend.
    // We just need to navigate, and the AuthContext will handle the rest.
    navigate(redirectTo, { replace: true });
  }, [navigate, searchParams]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-4"></div>
        <p>Finalizing login...</p>
      </div>
    </div>
  );
};

export default AuthCallbackPage;