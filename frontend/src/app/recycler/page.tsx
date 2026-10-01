"use client";

import { useAuth } from "@/context/AuthContext";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ScanLine, Loader2, Package, CheckCircle, Clock } from "lucide-react";
import { getEwasteAssets } from "@/lib/api";

export default function RecyclerDashboard() {
  const { user, loading } = useAuth();
  const router = useRouter();
  
  const [assets, setAssets] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!loading && (!user || user.role !== 'recycler')) {
      router.push('/login');
    }
  }, [user, loading, router]);

  useEffect(() => {
    if (user && user.role === 'recycler') {
      fetchAssets();
    }
  }, [user]);

  const fetchAssets = async () => {
    try {
      setIsLoading(true);
      const data = await getEwasteAssets();
      // Only show assets that are handed over or already recycled
      const recyclerAssets = data.filter((a: any) => 
        a.status === "HANDED_OVER" || a.status === "RECYCLED"
      );
      setAssets(recyclerAssets);
    } catch (err: any) {
      setError(err.message || "Failed to load assigned assets");
    } finally {
      setIsLoading(false);
    }
  };

  if (loading || !user || user.role !== 'recycler') return null;

  const pending = assets.filter(a => a.status === "HANDED_OVER").length;
  const completed = assets.filter(a => a.status === "RECYCLED").length;

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      
      {/* Header */}
      <div className="bg-[#17201B] rounded-3xl p-10 flex flex-col md:flex-row md:items-center justify-between gap-6 shadow-lg">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Recycler Dashboard</h1>
          <p className="text-gray-400 font-medium">Manage and process assigned e-waste assets.</p>
        </div>
        <div>
          <Link href="/recycler/scan" className="px-6 py-3.5 bg-[#1F8A5B] hover:bg-[#38A169] text-white rounded-xl font-bold flex items-center justify-center gap-2 transition-colors shadow-sm">
            <ScanLine className="w-5 h-5" /> Scan Asset for Processing
          </Link>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-[#E5E9E5] flex items-center gap-4">
          <div className="w-12 h-12 bg-amber-50 rounded-xl flex items-center justify-center text-amber-600">
            <Clock className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-semibold text-[#68736D] uppercase">Pending Processing</p>
            <p className="text-3xl font-bold text-[#17201B]">{pending}</p>
          </div>
        </div>
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-[#E5E9E5] flex items-center gap-4">
          <div className="w-12 h-12 bg-green-50 rounded-xl flex items-center justify-center text-[#1F8A5B]">
            <CheckCircle className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-semibold text-[#68736D] uppercase">Completed Records</p>
            <p className="text-3xl font-bold text-[#17201B]">{completed}</p>
          </div>
        </div>
      </div>

      {/* Records Table */}
      <div className="bg-white rounded-2xl shadow-sm border border-[#E5E9E5] overflow-hidden">
        <div className="p-6 border-b border-[#E5E9E5] flex items-center gap-3">
          <Package className="w-6 h-6 text-[#1F8A5B]" />
          <h2 className="text-xl font-bold text-[#17201B]">Assigned Assets & Records</h2>
        </div>
        
        {isLoading ? (
          <div className="flex p-12 justify-center">
            <Loader2 className="w-8 h-8 animate-spin text-[#1F8A5B]" />
          </div>
        ) : error ? (
          <div className="p-8 text-center text-red-600 font-medium">{error}</div>
        ) : assets.length === 0 ? (
          <div className="p-12 text-center text-[#68736D] flex flex-col items-center">
            <Package className="w-12 h-12 text-gray-300 mb-3" />
            <p className="text-lg font-medium">No recycling records found.</p>
            <p className="text-sm mt-1">When staff hands over e-waste, it will appear here.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-[#F5F8F5] border-b border-[#E5E9E5]">
                  <th className="p-4 text-sm font-semibold text-[#68736D]">Asset ID</th>
                  <th className="p-4 text-sm font-semibold text-[#68736D]">Name</th>
                  <th className="p-4 text-sm font-semibold text-[#68736D]">Type</th>
                  <th className="p-4 text-sm font-semibold text-[#68736D]">Status</th>
                  <th className="p-4 text-sm font-semibold text-[#68736D]">Added</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E5E9E5]">
                {assets.map((asset) => (
                  <tr key={asset.id} className="hover:bg-gray-50 transition-colors">
                    <td className="p-4 text-sm font-medium text-[#17201B]">{asset.asset_id}</td>
                    <td className="p-4 font-bold text-[#17201B]">{asset.asset_name}</td>
                    <td className="p-4 text-sm text-[#68736D]">{asset.asset_type}</td>
                    <td className="p-4">
                      {asset.status === 'RECYCLED' ? (
                        <span className="inline-flex px-2.5 py-1 text-xs font-semibold uppercase rounded-full bg-green-50 text-green-700 border border-green-200">
                          Recycled
                        </span>
                      ) : (
                        <span className="inline-flex px-2.5 py-1 text-xs font-semibold uppercase rounded-full bg-amber-50 text-amber-700 border border-amber-200">
                          Pending
                        </span>
                      )}
                    </td>
                    <td className="p-4 text-sm text-[#68736D]">
                      {new Date(asset.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
