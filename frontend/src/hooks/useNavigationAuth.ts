import { useAuth } from "@/contexts/AuthContext";
import { useLocation } from "react-router-dom";

export function useNavigationAuth() {
  const { user, loading, login, logout } = useAuth();
  const location = useLocation();

  const handleLogin = () => {
    login(location.pathname);
  };

  const handleLogout = async () => {
    await logout();
  };

  // Determine if we should show login button or user info
  const shouldShowLogin = !loading && !user;
  const shouldShowUser = !loading && !!user;

  return {
    user,
    loading,
    shouldShowLogin,
    shouldShowUser,
    handleLogin,
    handleLogout,
  };
}
