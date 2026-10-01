"use client";

import { useEffect, useState } from "react";
import { Leaf, History, Award, Zap, Loader2 } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { getUserCredits, getCreditHistory } from "@/lib/api";

export default function CreditsPage() {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [credits, setCredits] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      if (!user) return;
      try {
        setLoading(true);
        const [cred, hist] = await Promise.all([
          getUserCredits(user.id),
          getCreditHistory(user.id)
        ]);
        setCredits(cred);
        setHistory(hist.history || []);
      } catch (err: any) {
        setError(err.message || "Failed to load credits. Demo user may not exist yet.");
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-[#2F7D57]" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white p-8 rounded-2xl shadow-soft text-center max-w-md mx-auto mt-12 border border-red-100">
        <h3 className="text-lg font-semibold text-[#17201B] mb-2">No Green Credits Yet</h3>
        <p className="text-[#68736D] text-sm">Please verify a disposal on the Classification page first.</p>
      </div>
    );
  }

  const todayCredits = history
    .filter(h => new Date(h.created_at).toDateString() === new Date().toDateString())
    .reduce((sum, h) => sum + h.points, 0);

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in duration-500">
      
      {/* Demo Warning */}
      <div className="bg-blue-50 text-blue-800 px-4 py-2 rounded-lg text-sm inline-flex items-center gap-2 border border-blue-200">
        <Zap className="w-4 h-4" />
        Demo Mode: Viewing data for Student ({user?.id})
      </div>

      {/* Hero Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="col-span-1 md:col-span-2 bg-[#2F7D57] rounded-3xl p-8 text-white relative overflow-hidden shadow-soft">
          <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl -mr-10 -mt-10"></div>
          <div className="relative z-10 flex flex-col justify-between h-full">
            <div>
              <p className="text-emerald-100 font-medium mb-1 uppercase tracking-wider text-sm">Your Green Impact</p>
              <h1 className="text-6xl font-bold tracking-tight">{credits?.total_credits || 0}</h1>
            </div>
            <div className="mt-8 flex items-center gap-2 text-emerald-50">
              <Award className="w-5 h-5 text-yellow-300" />
              <span>Campus Sustainability Contributor</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-3xl p-8 border border-[#E5E9E5] shadow-soft flex flex-col justify-center">
          <h3 className="text-[#68736D] font-medium text-sm uppercase tracking-wider mb-2">Earned Today</h3>
          <div className="flex items-end gap-2">
            <span className="text-5xl font-bold text-[#17201B]">+{todayCredits}</span>
            <span className="text-[#2F7D57] font-medium mb-1 flex items-center gap-1"><Leaf className="w-4 h-4"/></span>
          </div>
          <p className="text-sm text-[#68736D] mt-4">Keep classifying and disposing correctly to maximize your impact.</p>
        </div>
      </div>

      {/* History */}
      <div className="bg-white rounded-3xl border border-[#E5E9E5] shadow-soft overflow-hidden">
        <div className="px-8 py-6 border-b border-[#E5E9E5] flex items-center gap-3">
          <History className="w-5 h-5 text-[#68736D]" />
          <h2 className="text-lg font-bold text-[#17201B]">Contribution History</h2>
        </div>
        
        {history.length === 0 ? (
          <div className="p-12 text-center text-[#68736D]">
            No verified disposals yet.
          </div>
        ) : (
          <div className="divide-y divide-[#E5E9E5]">
            {history.map((item, idx) => (
              <div key={idx} className="p-6 px-8 flex items-center justify-between hover:bg-[#F7F8F5] transition">
                <div>
                  <h4 className="font-semibold text-[#17201B] capitalize">{item.reason || "Responsible Disposal"}</h4>
                  <p className="text-sm text-[#68736D] mt-1">{new Date(item.created_at).toLocaleString()}</p>
                </div>
                <div className="flex items-center gap-2 text-[#2F7D57] font-bold text-lg bg-[#E8F3EC] px-4 py-2 rounded-full">
                  +{item.points}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  );
}
