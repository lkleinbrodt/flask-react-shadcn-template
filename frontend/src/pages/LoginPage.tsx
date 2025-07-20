import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  NavLink,
  useLocation,
  useNavigate,
  useSearchParams,
} from "react-router-dom";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Icons } from "@/components/ui/icons";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { authService } from "@/services/auth";
import { useAuth } from "@/contexts/AuthContext";

// Login Form Component
const LoginForm = ({
  email,
  setEmail,
  password,
  setPassword,
  isLoading,
  onSubmit,
  error,
}: {
  email: string;
  setEmail: (email: string) => void;
  password: string;
  setPassword: (password: string) => void;
  isLoading: boolean;
  onSubmit: (e: React.FormEvent) => void;
  error: string | null;
}) => (
  <form onSubmit={onSubmit} className="space-y-4">
    {error && (
      <Alert variant="destructive">
        <AlertTitle>Login Error</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    )}

    <div className="space-y-2">
      <Label htmlFor="email">Email</Label>
      <Input
        id="email"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Enter your email"
        required
        disabled={isLoading}
        autoComplete="email"
      />
    </div>

    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <Label htmlFor="password">Password</Label>
        <NavLink
          to="/forgot-password"
          className="text-sm font-medium text-primary hover:underline"
        >
          Forgot password?
        </NavLink>
      </div>
      <Input
        id="password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Enter your password"
        required
        disabled={isLoading}
        autoComplete="current-password"
      />
    </div>

    <Button type="submit" className="w-full" disabled={isLoading}>
      {isLoading && <Icons.spinner className="mr-2 h-4 w-4 animate-spin" />}
      {isLoading ? "Signing in..." : "Sign in"}
    </Button>
  </form>
);

// Register Form Component
const RegisterForm = ({
  name,
  setName,
  email,
  setEmail,
  password,
  setPassword,
  confirmPassword,
  setConfirmPassword,
  isLoading,
  onSubmit,
  error,
}: {
  name: string;
  setName: (name: string) => void;
  email: string;
  setEmail: (email: string) => void;
  password: string;
  setPassword: (password: string) => void;
  confirmPassword: string;
  setConfirmPassword: (password: string) => void;
  isLoading: boolean;
  onSubmit: (e: React.FormEvent) => void;
  error: string | null;
}) => (
  <form onSubmit={onSubmit} className="space-y-4">
    {error && (
      <Alert variant="destructive">
        <AlertTitle>Registration Error</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    )}

    <div className="space-y-2">
      <Label htmlFor="name">Full Name (Optional)</Label>
      <Input
        id="name"
        type="text"
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Enter your full name"
        disabled={isLoading}
        autoComplete="name"
      />
    </div>

    <div className="space-y-2">
      <Label htmlFor="email">Email</Label>
      <Input
        id="email"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Enter your email"
        required
        disabled={isLoading}
        autoComplete="email"
      />
    </div>

    <div className="space-y-2">
      <Label htmlFor="password">Password</Label>
      <Input
        id="password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Enter your password"
        required
        disabled={isLoading}
        autoComplete="new-password"
      />
    </div>

    <div className="space-y-2">
      <Label htmlFor="confirmPassword">Confirm Password</Label>
      <Input
        id="confirmPassword"
        type="password"
        value={confirmPassword}
        onChange={(e) => setConfirmPassword(e.target.value)}
        placeholder="Confirm your password"
        required
        disabled={isLoading}
        autoComplete="new-password"
      />
    </div>

    <Button type="submit" className="w-full" disabled={isLoading}>
      {isLoading && <Icons.spinner className="mr-2 h-4 w-4 animate-spin" />}
      {isLoading ? "Creating account..." : "Create account"}
    </Button>
  </form>
);

const LoginPage = () => {
  const [isRegisterMode, setIsRegisterMode] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const from = location.state?.from || "/";

  useEffect(() => {
    const errorParam = searchParams.get("error");
    const emailParam = searchParams.get("email");
    if (errorParam === "account_exists" && emailParam) {
      setError(
        `An account with the email ${emailParam} already exists. Please sign in with your password to link your account.`
      );
      setEmail(emailParam);
    } else if (errorParam === "oauth_failed") {
      setError("OAuth authentication failed. Please try again.");
    }
  }, [searchParams]);

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      await login({ email, password });
      navigate(from, { replace: true });
    } catch (err: unknown) {
      setError("Login failed. Please check your credentials.");
      console.error("Login failed:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegisterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      if (password !== confirmPassword) {
        setError("Passwords do not match.");
        return;
      }

      await authService.register({
        name: name.trim() || undefined,
        email,
        password,
      });

      // After successful registration, log the user in
      await login({ email, password });
      navigate(from, { replace: true });
    } catch (err: unknown) {
      if (
        err &&
        typeof err === "object" &&
        "response" in err &&
        err.response &&
        typeof err.response === "object" &&
        "status" in err.response &&
        err.response.status === 409
      ) {
        setError("An account with this email already exists.");
      } else {
        setError("Registration failed. Please try again.");
      }
      console.error("Registration failed:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleLogin = () => {
    authService.initiateOAuthLogin("google");
  };

  const toggleMode = () => {
    setIsRegisterMode(!isRegisterMode);
    setError(null);
    setPassword("");
    setConfirmPassword("");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background to-muted/20 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1 text-center">
          <CardTitle className="text-2xl font-bold">
            {isRegisterMode ? "Create an account" : "Welcome back"}
          </CardTitle>
          <CardDescription>
            {isRegisterMode
              ? "Enter your details to create your account"
              : "Enter your credentials to access your account"}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {isRegisterMode ? (
            <RegisterForm
              name={name}
              setName={setName}
              email={email}
              setEmail={setEmail}
              password={password}
              setPassword={setPassword}
              confirmPassword={confirmPassword}
              setConfirmPassword={setConfirmPassword}
              isLoading={isLoading}
              onSubmit={handleRegisterSubmit}
              error={error}
            />
          ) : (
            <LoginForm
              email={email}
              setEmail={setEmail}
              password={password}
              setPassword={setPassword}
              isLoading={isLoading}
              onSubmit={handleLoginSubmit}
              error={error}
            />
          )}

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-background px-2 text-muted-foreground">
                Or continue with
              </span>
            </div>
          </div>

          <Button
            variant="outline"
            type="button"
            className="w-full"
            onClick={handleGoogleLogin}
            disabled={isLoading}
          >
            <Icons.google className="mr-2 h-4 w-4" />
            {isRegisterMode ? "Sign up with Google" : "Sign in with Google"}
          </Button>

          <div className="text-center text-sm">
            <span className="text-muted-foreground">
              {isRegisterMode
                ? "Already have an account?"
                : "Don't have an account?"}
            </span>{" "}
            <button
              type="button"
              onClick={toggleMode}
              className="font-medium text-primary hover:underline"
              disabled={isLoading}
            >
              {isRegisterMode ? "Sign in" : "Sign up"}
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default LoginPage;
