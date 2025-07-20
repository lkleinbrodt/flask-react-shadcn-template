import { NavLink, useLocation, useNavigate } from "react-router-dom";

import { Button } from "@/components/ui/button";
import UserItem from "@/components/UserItem";
import { useAuth } from "@/contexts/AuthContext";

const getPageTitle = (pathname: string) => {
  switch (pathname) {
    default:
      return "PLACEHOLDER_PROJECT_NAME";
  }
};

export default function Header() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const pageTitle = getPageTitle(location.pathname);

  const handleLogin = () => {
    navigate("/login", { state: { from: location.pathname } });
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b bg-background">
      <div className="container flex h-14 items-center">
        <NavLink to="/" className="mr-6 flex items-center space-x-2">
          <img src="/vite.svg" alt="logo" className="w-8 h-8" />
          <span className="font-bold">{pageTitle}</span>
        </NavLink>
        <nav className="flex items-center space-x-4 lg:space-x-6">
          <NavLink
            to="/"
            className={({ isActive }) =>
              `text-sm font-medium transition-colors hover:text-primary ${
                isActive ? "" : "text-muted-foreground"
              }`
            }
          >
            Home
          </NavLink>
        </nav>
        <div className="flex flex-1 items-center justify-end space-x-4">
          {user ? (
            <UserItem />
          ) : (
            <Button variant="outline" onClick={handleLogin}>
              Login
            </Button>
          )}
        </div>
      </div>
    </header>
  );
}
