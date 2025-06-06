import "./App.css";

import { BrowserRouter, Route, Routes } from "react-router-dom";

import AuthPage from "@/pages/AuthPage";
import { AuthProvider } from "./contexts/AuthContext";
import HomePage from "./pages/HomePage";
import Layout from "./components/common/Layout";
import Login from "./pages/LoginPage";
import { ThemeProvider } from "./components/theme-provider";
import { Toaster } from "@/components/ui/toaster";

function App() {
  return (
    <BrowserRouter>
      <ThemeProvider defaultTheme="light" storageKey="vite-ui-theme">
        <AuthProvider>
          <Toaster />
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/auth" element={<AuthPage />} />
            <Route path="/" element={<Layout />}>
              <Route index element={<HomePage />} />
            </Route>

            {/* <Route element={<PrivateRoute />}>
              <Route path="/" element={<Landing />} />
            </Route> */}
          </Routes>
        </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
}

export default App;
