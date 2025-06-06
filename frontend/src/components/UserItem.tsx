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
  const initials = name
    ?.split(" ")
    .map((n) => n[0])
    .join("");

  return (
    <div className="p-1">
      <DropdownMenu>
        <DropdownMenuTrigger className="flex items-start w-full gap-2 rounded-[8px] p-1">
          <Avatar>
            <AvatarImage src={user!.image ?? ""} />
            <AvatarFallback>{initials}</AvatarFallback>
          </Avatar>
          <div>
            <div className="text-lg font-bold text-foreground">{name}</div>
            <div className="text-xs text-muted-foreground">{email}</div>
          </div>
        </DropdownMenuTrigger>
        <DropdownMenuContent>
          <DropdownMenuLabel>{name}</DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={logout}>Sign out</DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
};

export default UserItem;
