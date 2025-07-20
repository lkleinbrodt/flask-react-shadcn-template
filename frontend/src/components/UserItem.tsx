import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

import { Skeleton } from "@/components/ui/skeleton";
import { User } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";

const UserItem = () => {
  const { user, logout, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center space-x-0 border rounded-[8px] p-1">
        <Skeleton className="h-12 min-w-12 rounded-full" />
        <div className="space-y-1">
          <Skeleton className="h-4 w-52" />
          <Skeleton className="h-4 w-40" />
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  const name = user?.name;
  const email = user?.email;

  // Generate initials from name if available, otherwise use first letter of email
  const initials = name
    ? name
        .split(" ")
        .map((n) => n[0])
        .join("")
    : email?.charAt(0).toUpperCase() || "U";

  // Determine what to display as the main text
  const displayName = name || email;
  const displaySubtext = name ? email : null;

  return (
    <div className="p-1">
      <DropdownMenu>
        <DropdownMenuTrigger className="flex items-start w-full gap-2 rounded-[8px] p-1">
          <Avatar>
            <AvatarImage src={user.image || ""} />
            <AvatarFallback>
              {user.image ? <User className="h-6 w-6" /> : initials}
            </AvatarFallback>
          </Avatar>
          <div>
            <div className="text-lg font-bold text-foreground">
              {displayName}
            </div>
            {displaySubtext && (
              <div className="text-xs text-muted-foreground">
                {displaySubtext}
              </div>
            )}
          </div>
        </DropdownMenuTrigger>
        <DropdownMenuContent>
          <DropdownMenuLabel>{displayName}</DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={logout}>Sign out</DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
};

export default UserItem;
