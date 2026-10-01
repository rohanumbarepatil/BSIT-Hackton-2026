"use client";

import { useAuth } from "@/context/AuthContext";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { Loader2 } from "lucide-react";

const rolePermissions: Record<string, string[]> = {
  student: ["/", "/student", "/classify", "/credits", "/login"],
  staff: ["/", "/staff", "/ewaste", "/bins", "/staff/scan", "/login"],
  recycler: ["/", "/recycler", "/ewaste", "/recycler/scan", "/login"],
  admin: ["/", "/admin", "/classify", "/ewaste", "/bins", "/credits", "/users", "/login"],
};

export default function RouteGuard({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    if (loading) return;

    if (!user && pathname !== "/login") {
      router.push("/login");
      return;
    }

    if (user) {
      const allowedPaths = rolePermissions[user.role] || [];
      const isAllowed = allowedPaths.some(p => pathname === p || pathname.startsWith(`${p}/`));
      
      // Also prevent logged-in users from seeing login page
      if (pathname === "/login") {
        router.push(`/${user.role}`);
        return;
      }

      if (!isAllowed) {
        // redirect to their default dashboard
        router.push(`/${user.role}`);
      }
    }
  }, [user, loading, pathname, router]);

  if (loading) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-[#F7F8F5]">
        <Loader2 className="w-8 h-8 animate-spin text-[#2F7D57]" />
      </div>
    );
  }

  // Prevent flashing of unauthorized content before redirect
  if (user) {
    const allowedPaths = rolePermissions[user.role] || [];
    const isAllowed = allowedPaths.some(p => pathname === p || pathname.startsWith(`${p}/`));
    if (!isAllowed && pathname !== "/") return null; // Wait for redirect
  }

  return <>{children}</>;
}
