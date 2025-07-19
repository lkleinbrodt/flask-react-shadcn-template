import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

import { Button } from "@/components/ui/button";
import { NavLink } from "react-router-dom";
import UserItem from "@/components/UserItem";
import { useNavigationAuth } from "@/hooks/useNavigationAuth";
import { useState } from "react";

const getPageTitle = (pathname: string) => {
  switch (pathname) {
    default:
      return "PLACEHOLDER_PROJECT_NAME";
  }
};

export default function FloatingNav() {
  const { shouldShowLogin, shouldShowUser, handleLogin, loading } =
    useNavigationAuth();
  const pageTitle = getPageTitle(window.location.pathname);
  const [isOpen, setIsOpen] = useState(false);

  const handleLoginClick = () => {
    setIsOpen(false);
    handleLogin();
  };

  return (
    <div className="fixed top-4 left-4 z-50">
      <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
        <DropdownMenuTrigger asChild>
          <Button
            variant="outline"
            size="icon"
            className="h-12 w-12 rounded-full shadow-lg hover:shadow-xl transition-all duration-200 bg-background/80 backdrop-blur-sm border-2"
          >
            <img src="/vite.svg" alt="logo" className="w-6 h-6" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start" className="w-64 p-2" sideOffset={8}>
          <div className="flex items-center space-x-2 p-2">
            <img src="/vite.svg" alt="logo" className="w-6 h-6" />
            <span className="font-bold text-sm">{pageTitle}</span>
          </div>

          <DropdownMenuSeparator />

          <div className="space-y-1">
            <DropdownMenuItem asChild>
              <NavLink
                to="/"
                className="w-full flex items-center px-2 py-1.5 text-sm rounded-md hover:bg-accent"
                onClick={() => setIsOpen(false)}
              >
                Home
              </NavLink>
            </DropdownMenuItem>
          </div>

          <DropdownMenuSeparator />

          <div className="p-2">
            {loading ? (
              <div className="flex items-center justify-center py-2">
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
              </div>
            ) : shouldShowUser ? (
              <div className="flex items-center space-x-2">
                <UserItem />
              </div>
            ) : shouldShowLogin ? (
              <Button
                variant="outline"
                size="sm"
                className="w-full"
                onClick={handleLoginClick}
              >
                Login
              </Button>
            ) : null}
          </div>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
