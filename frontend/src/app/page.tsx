"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowRight, Leaf, Cpu, Recycle, ShieldCheck, AlertCircle, Loader2, ScanLine } from "lucide-react";
import { getDashboardStats, getEwasteDashboard, getModelInfo } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";

export default function DashboardPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [modelInfo, setModelInfo] = useState<any>(null);
  const [binStats, setBinStats] = useState<any>(null);
  const [ewasteStats, setEwasteStats] = useState<any>(null);

  const { user, loading: authLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (authLoading) return;
    if (!user) {
      router.push('/login');
      return;
    }
    
    if (user.role === 'student') router.push('/student');
    else if (user.role === 'staff') router.push('/staff');
    else if (user.role === 'admin') router.push('/admin');
    else if (user.role === 'recycler') router.push('/recycler');
  }, [user, authLoading, router]);

  if (loading || authLoading) {
    return (
      <div className="flex h-[60vh] items-center justify-center text-[#68736D]">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-8 h-8 animate-spin text-[#2F7D57]" />
          <p>Loading campus intelligence...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <div className="bg-white p-8 rounded-2xl shadow-soft max-w-md w-full text-center border border-red-100">
          <div className="w-12 h-12 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-4 text-[#C85B4A]">
            <AlertCircle className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-semibold text-[#17201B] mb-2">Connection Error</h3>
          <p className="text-sm text-[#68736D] mb-6">{error}</p>
          <button 
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-[#F7F8F5] text-[#17201B] rounded-lg font-medium text-sm hover:bg-[#E5E9E5] transition"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  const collectionRisk = binStats?.critical > 0 || binStats?.overflow > 0 ? "High" : binStats?.warning > 0 ? "Medium" : "Low";
  const riskColor = collectionRisk === "High" ? "text-[#C85B4A]" : collectionRisk === "Medium" ? "text-[#D89B35]" : "text-[#2F7D57]";

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      
      {/* Hero Section */}
      <div className="bg-[#17201B] rounded-3xl p-10 flex flex-col md:flex-row items-center justify-between overflow-hidden relative">
        <div className="absolute top-0 right-0 w-96 h-96 bg-[#2F7D57] rounded-full blur-3xl opacity-20 -mr-20 -mt-20"></div>
        
        <div className="relative z-10 max-w-xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-white/10 rounded-full text-white/80 text-xs font-medium mb-6">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            WasteSense {modelInfo?.model_version || "Prototype"} Active
          </div>
          <h1 className="text-4xl font-bold text-white mb-4 tracking-tight leading-tight">
            Make every disposal count.
          </h1>
          <p className="text-lg text-zinc-400 mb-8">
            AI-powered waste classification, responsible disposal tracking, and intelligent campus collection.
          </p>
          <div className="flex items-center gap-4">
            <Link 
              href="/classify" 
              className="px-6 py-3 bg-white text-[#17201B] rounded-xl font-medium flex items-center gap-2 hover:bg-zinc-100 transition shadow-lg"
            >
              Scan Waste <ArrowRight className="w-4 h-4" />
            </Link>
            <Link 
              href="/bins" 
              className="px-6 py-3 bg-white/10 text-white rounded-xl font-medium hover:bg-white/20 transition"
            >
              View Smart Bins
            </Link>
          </div>
        </div>
        
        <div className="hidden md:block relative z-10 w-64 h-64">
          {/* Abstract visual */}
          <div className="w-full h-full border-4 border-white/10 rounded-full flex items-center justify-center p-8">
            <div className="w-full h-full border-4 border-emerald-500/30 rounded-full flex items-center justify-center p-8">
              <div className="w-full h-full bg-emerald-500/20 rounded-full flex items-center justify-center">
                 <Leaf className="w-16 h-16 text-emerald-400 opacity-80" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-2xl shadow-soft border border-[#E5E9E5]">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-[#68736D] uppercase tracking-wider">AI Capabilities</h3>
            <div className="w-8 h-8 rounded-full bg-[#E8F3EC] flex items-center justify-center">
              <ScanLine className="w-4 h-4 text-[#2F7D57]" />
            </div>
          </div>
          <p className="text-3xl font-bold text-[#17201B]">{modelInfo?.trained_classes?.length || 0}</p>
          <p className="text-sm text-[#68736D] mt-2">Waste categories trained</p>
        </div>

        <div className="bg-white p-6 rounded-2xl shadow-soft border border-[#E5E9E5]">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-[#68736D] uppercase tracking-wider">E-Waste Assets</h3>
            <div className="w-8 h-8 rounded-full bg-[#E8F3EC] flex items-center justify-center">
              <Cpu className="w-4 h-4 text-[#2F7D57]" />
            </div>
          </div>
          <p className="text-3xl font-bold text-[#17201B]">{ewasteStats?.total_assets || 0}</p>
          <p className="text-sm text-[#68736D] mt-2">Institutional assets tracked</p>
        </div>

        <div className="bg-white p-6 rounded-2xl shadow-soft border border-[#E5E9E5]">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-[#68736D] uppercase tracking-wider">Smart Bins</h3>
            <div className="w-8 h-8 rounded-full bg-[#E8F3EC] flex items-center justify-center">
              <Recycle className="w-4 h-4 text-[#2F7D57]" />
            </div>
          </div>
          <p className="text-3xl font-bold text-[#17201B]">{binStats?.total_bins || 0}</p>
          <p className="text-sm text-[#68736D] mt-2">Active telemetry endpoints</p>
        </div>
      </div>

      {/* Campus Status Section */}
      <div className="bg-white rounded-2xl shadow-soft border border-[#E5E9E5] overflow-hidden">
        <div className="px-8 py-6 border-b border-[#E5E9E5] flex justify-between items-center">
          <div>
            <h2 className="text-lg font-bold text-[#17201B]">Campus Waste Pulse</h2>
            <p className="text-sm text-[#68736D] mt-1">Live telemetry across all deployed smart bins</p>
          </div>
          <div className="text-right">
            <p className="text-sm font-medium text-[#68736D] uppercase tracking-wider mb-1">Collection Risk</p>
            <p className={`text-lg font-bold ${riskColor}`}>{collectionRisk}</p>
          </div>
        </div>
        <div className="p-8 grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="flex flex-col items-center justify-center p-6 bg-[#F7F8F5] rounded-xl">
            <span className="text-3xl font-bold text-[#2F7D57] mb-2">{binStats?.normal || 0}</span>
            <span className="text-sm font-medium text-[#68736D]">Normal</span>
          </div>
          <div className="flex flex-col items-center justify-center p-6 bg-yellow-50 rounded-xl">
            <span className="text-3xl font-bold text-[#D89B35] mb-2">{binStats?.warning || 0}</span>
            <span className="text-sm font-medium text-[#68736D]">Warning</span>
          </div>
          <div className="flex flex-col items-center justify-center p-6 bg-red-50 rounded-xl">
            <span className="text-3xl font-bold text-[#C85B4A] mb-2">{binStats?.critical || 0}</span>
            <span className="text-sm font-medium text-[#68736D]">Critical</span>
          </div>
          <div className="flex flex-col items-center justify-center p-6 bg-red-100 rounded-xl">
            <span className="text-3xl font-bold text-red-700 mb-2">{binStats?.overflow || 0}</span>
            <span className="text-sm font-medium text-red-700">Overflow</span>
          </div>
        </div>
      </div>

    </div>
  );
}
