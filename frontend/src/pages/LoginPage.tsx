import { useAuth } from "@/contexts/AuthContext";
import { useEffect } from "react";
import { useLocation } from "react-router-dom";

const Login = () => {
  const location = useLocation();
  const from = location.state?.from?.pathname || "/";
  const { login } = useAuth();

  const handleSignIn = () => {
    login(from);
  };

  // Only run once on mount, not on every render
  useEffect(() => {
    handleSignIn();
  }, []); // Empty dependency array

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-4"></div>
        <p>Redirecting to login...</p>
      </div>
    </div>
  );
};

export default Login;
