"use client";

import { useAuth } from "@/context/AuthContext";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ScanLine } from "lucide-react";

export default function RecyclerDashboard() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && (!user || user.role !== 'recycler')) {
      router.push('/login');
    }
  }, [user, loading, router]);

  if (loading || !user || user.role !== 'recycler') return null;

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="bg-[#17201B] rounded-3xl p-10">
        <h1 className="text-3xl font-bold text-white mb-4">Recycler Dashboard</h1>
        <div className="flex gap-4">
          <Link href="/recycler/scan" className="px-6 py-3 bg-emerald-500 text-white rounded-xl font-medium flex items-center gap-2">
            <ScanLine className="w-5 h-5" /> Scan Asset
          </Link>
        </div>
      </div>
    </div>
  );
}
