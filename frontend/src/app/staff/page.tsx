"use client";

import { useAuth } from "@/context/AuthContext";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Cpu, ScanLine } from "lucide-react";

export default function StaffDashboard() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    if (!loading && (!user || user.role !== 'staff')) {
      router.push('/login');
    } else if (user?.role === 'staff') {
      fetch('http://127.0.0.1:8001/api/v1/ewaste/dashboard', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      }).then(res => res.json()).then(data => setStats(data));
    }
  }, [user, loading, router]);

  if (loading || !user || user.role !== 'staff') return null;

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="bg-[#17201B] rounded-3xl p-10">
        <h1 className="text-3xl font-bold text-white mb-4">Institutional E-Waste</h1>
        <div className="flex gap-4">
          <Link href="/staff/scan" className="px-6 py-3 bg-white text-[#17201B] rounded-xl font-medium flex items-center gap-2">
            <ScanLine className="w-5 h-5" /> Scan Asset QR
          </Link>
          <Link href="/ewaste" className="px-6 py-3 bg-white/20 text-white rounded-xl font-medium flex items-center gap-2">
            <Cpu className="w-5 h-5" /> View Assets
          </Link>
        </div>
      </div>
      <div className="grid grid-cols-4 gap-6">
        {stats && Object.entries(stats).map(([k, v]) => (
          <div key={k} className="bg-white p-6 rounded-2xl shadow-soft">
            <h3 className="text-sm font-semibold text-[#68736D] uppercase">{k.replace('_', ' ')}</h3>
            <p className="text-3xl font-bold text-[#17201B] mt-2">{String(v)}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
