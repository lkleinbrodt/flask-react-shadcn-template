import { Navigate, Outlet, useLocation } from "react-router-dom";

import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/contexts/AuthContext";

export default function PrivateRoute() {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    // Show a loading skeleton or spinner while auth state is being determined
    return <Skeleton className="h-24 w-full" />;
  }

  if (!user) {
    // Redirect them to the /login page, but save the current location they were
    // trying to go to. This allows us to send them back after they log in.
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <Outlet />;
}
