import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

const AuthCallbackPage = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // The backend has set the cookies. We just need to go to the main app.
    // The AuthContext will then fetch the user data.
    navigate("/", { replace: true });
  }, [navigate]);

  return <div>Finalizing login...</div>;
};

export default AuthCallbackPage;
