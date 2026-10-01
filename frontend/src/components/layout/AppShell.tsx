"use client";

import { usePathname } from "next/navigation";
import Sidebar from "./Sidebar";
import TopHeader from "./TopHeader";
import { useAuth } from "@/context/AuthContext";

export default function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { user, loading } = useAuth();

  if (loading) {
    return <main className="flex flex-col w-full h-full bg-[#F7F8F5] items-center justify-center"></main>;
  }

  if (pathname === "/login") {
    return <main className="flex flex-col w-full h-full bg-[#F7F8F5]">{children}</main>;
  }

  // If we are not logged in and not on the login page, RouteGuard will handle the redirect.
  // But to avoid flashing the app shell, we return just the children (which might be loading state or null from RouteGuard).
  if (!user && pathname !== "/login") {
    return <main className="flex flex-col w-full h-full bg-[#F7F8F5]">{children}</main>;
  }

  return (
    <>
      {/* Sidebar */}
      <div className="hidden md:flex md:w-64 md:flex-col fixed h-full z-10">
        <Sidebar />
      </div>
      
      {/* Main Content */}
      <main className="md:pl-64 flex flex-col w-full h-full">
        <TopHeader />
        <div className="flex-1 overflow-y-auto bg-[#F7F8F5]">
          <div className="p-8">
            {children}
          </div>
        </div>
      </main>
    </>
  );
}
