import "./App.css";

import { BrowserRouter, Route, Routes } from "react-router-dom";

import AuthCallbackPage from "@/pages/AuthCallbackPage";
import { AuthProvider } from "./contexts/AuthContext";
import ForgotPasswordPage from "./pages/ForgotPasswordPage";
import HomePage from "./pages/HomePage";
import Layout from "./components/common/Layout";
import LoginPage from "./pages/LoginPage";
import PrivateRoute from "./components/PrivateRoute";
import ResetPasswordPage from "./pages/ResetPasswordPage";
import { ThemeProvider } from "./components/theme-provider";
import { Toaster } from "@/components/ui/toaster";

function App() {
  return (
    <BrowserRouter>
      <ThemeProvider defaultTheme="light" storageKey="vite-ui-theme">
        <AuthProvider>
          <Toaster />
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
            <Route
              path="/reset-password/:token"
              element={<ResetPasswordPage />}
            />
            <Route path="/auth/callback" element={<AuthCallbackPage />} />
            <Route path="/" element={<Layout />}>
              <Route index element={<HomePage />} />
              <Route element={<PrivateRoute />}>
                <Route path="/private" element={<HomePage />} />
              </Route>
            </Route>
          </Routes>
        </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
}

export default App;
