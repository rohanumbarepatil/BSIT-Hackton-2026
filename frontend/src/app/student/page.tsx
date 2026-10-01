"use client";

import { useAuth } from "@/context/AuthContext";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowRight, Leaf, ScanLine } from "lucide-react";

export default function StudentDashboard() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && (!user || user.role !== 'student')) {
      router.push('/login');
    }
  }, [user, loading, router]);

  if (loading || !user || user.role !== 'student') return null;

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="bg-[#17201B] rounded-3xl p-10 flex flex-col items-start justify-center relative overflow-hidden">
        <h1 className="text-4xl font-bold text-white mb-4">Your Sustainability Impact</h1>
        <p className="text-lg text-zinc-400 mb-8">Ready to dispose of waste responsibly?</p>
        <div className="flex gap-4 z-10">
          <Link href="/classify" className="px-6 py-3 bg-white text-[#17201B] rounded-xl font-medium flex items-center gap-2">
            <ScanLine className="w-5 h-5" /> Scan Waste
          </Link>
          <Link href="/credits" className="px-6 py-3 bg-emerald-500 text-white rounded-xl font-medium flex items-center gap-2">
            <Leaf className="w-5 h-5" /> View Credits
          </Link>
        </div>
      </div>
    </div>
  );
}
