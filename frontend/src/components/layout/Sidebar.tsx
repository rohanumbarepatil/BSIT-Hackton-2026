"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutDashboard, 
  ScanLine, 
  Leaf, 
  Cpu, 
  Recycle,
  Users,
  LogOut,
  Settings
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/context/AuthContext";

const roleNavigation: Record<string, any[]> = {
  admin: [
    { label: "Admin Dashboard", icon: LayoutDashboard, href: "/admin", color: "text-emerald-500" },
    { label: "AI Classification", icon: ScanLine, href: "/classify", color: "text-emerald-500" },
    { label: "E-Waste Lifecycle", icon: Cpu, href: "/ewaste", color: "text-emerald-500" },
    { label: "Smart Bins", icon: Recycle, href: "/bins", color: "text-emerald-500" },
    { label: "Green Credits", icon: Leaf, href: "/admin/credits", color: "text-emerald-500" },
    { label: "Users & Roles", icon: Users, href: "/admin/users", color: "text-emerald-500" },
    { label: "Audit Logs", icon: Settings, href: "/admin/audit", color: "text-emerald-500" },
  ],
  staff: [
    { label: "Staff Dashboard", icon: LayoutDashboard, href: "/staff", color: "text-emerald-500" },
    { label: "Scan E-Waste QR", icon: ScanLine, href: "/staff/scan", color: "text-emerald-500" },
    { label: "E-Waste Assets", icon: Cpu, href: "/ewaste", color: "text-emerald-500" },
    { label: "Smart Bins", icon: Recycle, href: "/bins", color: "text-emerald-500" },
  ],
  recycler: [
    { label: "Recycler Dashboard", icon: LayoutDashboard, href: "/recycler", color: "text-emerald-500" },
    { label: "Scan Asset", icon: ScanLine, href: "/recycler/scan", color: "text-emerald-500" },
    { label: "Assigned Assets", icon: Cpu, href: "/ewaste", color: "text-emerald-500" },
    { label: "Recycling Records", icon: Recycle, href: "#", color: "text-emerald-500" },
  ],
  student: [
    { label: "Overview", icon: LayoutDashboard, href: "/student", color: "text-emerald-500" },
    { label: "AI Classification", icon: ScanLine, href: "/classify", color: "text-emerald-500" },
    { label: "Green Credits", icon: Leaf, href: "/credits", color: "text-emerald-500" },
  ]
};

export default function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  const getRoutes = () => {
    if (!user) return [];
    return roleNavigation[user.role] || [];
  };

  const routes = getRoutes();

  return (
    <div className="space-y-4 py-4 flex flex-col h-full bg-[#17201B] text-white">
      <div className="px-3 py-2 flex-1">
        <Link href="/" className="flex items-center pl-3 mb-14">
          <h1 className="text-2xl font-bold text-white tracking-tight">
            WasteSense<span className="text-[#3A8F83]">.AI</span>
          </h1>
        </Link>
        <div className="space-y-1">
          {routes.map((route) => (
            <Link
              key={route.href}
              href={route.href}
              className={cn(
                "text-sm group flex p-3 w-full justify-start font-medium cursor-pointer hover:text-white hover:bg-white/10 rounded-lg transition",
                pathname === route.href ? "text-white bg-white/10" : "text-zinc-400"
              )}
            >
              <div className="flex items-center flex-1">
                <route.icon className={cn("h-5 w-5 mr-3", route.color)} />
                {route.label}
              </div>
            </Link>
          ))}
          
          {user && (
            <button
              onClick={logout}
              className="text-sm group flex p-3 w-full justify-start font-medium cursor-pointer text-zinc-400 hover:text-white hover:bg-white/10 rounded-lg transition mt-4"
            >
              <div className="flex items-center flex-1">
                <LogOut className="h-5 w-5 mr-3 text-red-500" />
                Logout
              </div>
            </button>
          )}
        </div>
      </div>
      <div className="px-6 py-4 mt-auto border-t border-white/10">
        <p className="text-xs text-zinc-400">WasteSense AI</p>
        <p className="text-[10px] text-zinc-500 mb-4">Campus Sustainability Platform</p>
        {user && (
          <p className="text-xs text-emerald-400 mb-4">Role: {user.role.toUpperCase()}</p>
        )}
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></div>
          <span className="text-xs text-zinc-300">Systems Operational</span>
        </div>
      </div>
    </div>
  );
}
