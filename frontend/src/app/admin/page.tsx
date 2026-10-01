"use client";

import { useAuth } from "@/context/AuthContext";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getDashboardStats, getEwasteDashboard } from "@/lib/api";
import { Users, Recycle, Cpu, AlertTriangle } from "lucide-react";

export default function AdminDashboard() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [binStats, setBinStats] = useState<any>(null);
  const [ewasteStats, setEwasteStats] = useState<any>(null);

  useEffect(() => {
    if (!loading && (!user || user.role !== 'admin')) {
      router.push('/login');
    } else if (user?.role === 'admin') {
      // Mocked headers for API logic if required, but getDashboardStats doesn't take args currently.
      // Assuming api endpoints are auth-guarded.
      getDashboardStats().then(setBinStats).catch(console.error);
      getEwasteDashboard().then(setEwasteStats).catch(console.error);
    }
  }, [user, loading, router]);

  if (loading || !user || user.role !== 'admin') return null;

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <h1 className="text-3xl font-bold text-[#17201B]">Admin Dashboard</h1>
      <div className="grid grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-2xl shadow-soft border border-[#E5E9E5]">
          <h3 className="text-sm font-semibold text-[#68736D] uppercase flex items-center gap-2"><Cpu className="w-4 h-4"/> Total E-Waste</h3>
          <p className="text-3xl font-bold mt-2">{ewasteStats?.total_assets || 0}</p>
        </div>
        <div className="bg-white p-6 rounded-2xl shadow-soft border border-[#E5E9E5]">
          <h3 className="text-sm font-semibold text-[#68736D] uppercase flex items-center gap-2"><Cpu className="w-4 h-4"/> Recycled Assets</h3>
          <p className="text-3xl font-bold mt-2">{ewasteStats?.recycled || 0}</p>
        </div>
        <div className="bg-white p-6 rounded-2xl shadow-soft border border-[#E5E9E5]">
          <h3 className="text-sm font-semibold text-[#68736D] uppercase flex items-center gap-2"><Recycle className="w-4 h-4"/> Smart Bins</h3>
          <p className="text-3xl font-bold mt-2">{binStats?.total_bins || 0}</p>
        </div>
        <div className="bg-red-50 p-6 rounded-2xl shadow-soft border border-red-100">
          <h3 className="text-sm font-semibold text-red-700 uppercase flex items-center gap-2"><AlertTriangle className="w-4 h-4"/> Critical Bins</h3>
          <p className="text-3xl font-bold text-red-700 mt-2">{binStats?.critical || 0}</p>
        </div>
      </div>
    </div>
  );
}
