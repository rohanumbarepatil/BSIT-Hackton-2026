"use client";

import { usePathname } from "next/navigation";
import { Bell, MapPin, User } from "lucide-react";

export default function TopHeader() {
  const pathname = usePathname();
  
  const getPageTitle = () => {
    switch (pathname) {
      case "/": return { title: "Overview", subtitle: "Make every disposal count." };
      case "/classify": return { title: "AI Classification", subtitle: "Identify your waste for responsible disposal." };
      case "/ewaste": return { title: "Institutional E-Waste Lifecycle", subtitle: "Track assets from lab decommissioning to responsible recycling." };
      case "/bins": return { title: "Campus Smart Bins", subtitle: "Simulated telemetry with predictive collection intelligence." };
      case "/credits": return { title: "Your Green Impact", subtitle: "Track and earn credits for responsible disposal." };
      default: return { title: "Dashboard", subtitle: "WasteSense AI Platform" };
    }
  };

  const { title, subtitle } = getPageTitle();

  return (
    <div className="h-20 w-full flex items-center justify-between px-8 bg-white border-b border-[#E5E9E5]">
      <div>
        <h2 className="text-xl font-semibold text-[#17201B] tracking-tight">{title}</h2>
        <p className="text-sm text-[#68736D] mt-0.5">{subtitle}</p>
      </div>

      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2 px-3 py-1.5 bg-[#F7F8F5] rounded-full text-sm text-[#68736D]">
          <MapPin className="w-4 h-4 text-[#3A8F83]" />
          <span className="font-medium">SGI Campus</span>
        </div>
        
        <div className="w-px h-6 bg-[#E5E9E5]"></div>
        
        <button className="relative p-2 text-[#68736D] hover:bg-[#F7F8F5] rounded-full transition">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-[#C85B4A] rounded-full border-2 border-white"></span>
        </button>

        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-[#E8F3EC] flex items-center justify-center text-[#2F7D57]">
            <User className="w-5 h-5" />
          </div>
          <div className="hidden md:block text-sm">
            <p className="font-medium text-[#17201B]">Student</p>
          </div>
        </div>
      </div>
    </div>
  );
}
