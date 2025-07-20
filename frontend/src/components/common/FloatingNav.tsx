import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { NavLink, useLocation, useNavigate } from "react-router-dom";

import { Button } from "@/components/ui/button";
import UserItem from "@/components/UserItem";
import { useAuth } from "@/contexts/AuthContext";
import { useState } from "react";

const getPageTitle = (pathname: string) => {
  switch (pathname) {
    default:
      return "PLACEHOLDER_PROJECT_NAME";
  }
};

export default function FloatingNav() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const pageTitle = getPageTitle(location.pathname);
  const [isOpen, setIsOpen] = useState(false);

  const handleLogin = () => {
    setIsOpen(false);
    navigate("/login", { state: { from: location.pathname } });
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
        <DropdownMenuContent
          align="start"
          className="w-auto min-w-64 max-w-80 p-2"
          sideOffset={8}
        >
          <div className="flex items-center space-x-2 p-2">
            <img src="/vite.svg" alt="logo" className="w-6 h-6 flex-shrink-0" />
            <span className="font-bold text-sm truncate">{pageTitle}</span>
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
            {user ? (
              <div className="flex items-center space-x-2">
                <UserItem />
              </div>
            ) : (
              <Button
                variant="outline"
                size="sm"
                className="w-full"
                onClick={handleLogin}
              >
                Login
              </Button>
            )}
          </div>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
