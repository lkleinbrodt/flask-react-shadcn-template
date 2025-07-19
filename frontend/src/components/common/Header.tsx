import { Button } from "@/components/ui/button";
import { NavLink } from "react-router-dom";
import UserItem from "@/components/UserItem";
import { useNavigationAuth } from "@/hooks/useNavigationAuth";

const getPageTitle = (pathname: string) => {
  switch (pathname) {
    default:
      return "PLACEHOLDER_PROJECT_NAME";
  }
};

export default function Header() {
  const { shouldShowLogin, shouldShowUser, handleLogin, loading } =
    useNavigationAuth();
  const pageTitle = getPageTitle(window.location.pathname);

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
          {loading ? (
            <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
          ) : shouldShowUser ? (
            <UserItem />
          ) : shouldShowLogin ? (
            <Button variant="outline" onClick={handleLogin}>
              Login
            </Button>
          ) : null}
        </div>
      </div>
    </header>
  );
}
