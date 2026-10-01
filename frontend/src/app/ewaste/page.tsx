"use client";

import { useEffect, useState } from "react";
import { Cpu, Server, ArchiveX, Truck, RefreshCw, X, QrCode, Loader2, ArrowDown } from "lucide-react";
import { getEwasteDashboard, getEwasteAssets, getEwasteAudit } from "@/lib/api";

export default function EWastePage() {
  const [loading, setLoading] = useState(true);
  const [dashboard, setDashboard] = useState<any>(null);
  const [assets, setAssets] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  const [selectedAsset, setSelectedAsset] = useState<any | null>(null);
  const [auditTrail, setAuditTrail] = useState<any[]>([]);
  const [auditLoading, setAuditLoading] = useState(false);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [dashRes, assetsRes] = await Promise.all([
          getEwasteDashboard(),
          getEwasteAssets()
        ]);
        setDashboard(dashRes);
        setAssets(assetsRes);
      } catch (err: any) {
        setError(err.message || "Failed to load E-Waste data.");
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const openAssetDetails = async (asset: any) => {
    setSelectedAsset(asset);
    setAuditLoading(true);
    try {
      const audit = await getEwasteAudit(asset.asset_id);
      setAuditTrail(audit.audit_trail || []);
    } catch (err) {
      console.error(err);
    } finally {
      setAuditLoading(false);
    }
  };

  const closeDetails = () => {
    setSelectedAsset(null);
    setAuditTrail([]);
  };

  if (loading) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-[#2F7D57]" />
      </div>
    );
  }

  if (error) {
    return <div className="text-[#C85B4A] bg-red-50 p-6 rounded-xl">{error}</div>;
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "REGISTERED": return "bg-zinc-100 text-zinc-700";
      case "IN_USE": return "bg-blue-50 text-blue-700";
      case "DECOMMISSIONED": return "bg-yellow-50 text-yellow-700";
      case "HANDED_OVER": return "bg-orange-50 text-orange-700";
      case "RECYCLED": return "bg-emerald-50 text-emerald-700";
      default: return "bg-zinc-100 text-zinc-700";
    }
  };

  return (
    <div className="max-w-7xl mx-auto animate-in fade-in duration-500 flex flex-col h-[calc(100vh-120px)]">
      
      {/* Metrics Row */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8 shrink-0">
        <div className="bg-white p-6 rounded-2xl shadow-soft border border-[#E5E9E5]">
          <div className="flex items-center gap-2 mb-2 text-[#68736D]">
            <Server className="w-4 h-4" /> <span className="text-xs uppercase tracking-wider font-semibold">Total Assets</span>
          </div>
          <p className="text-3xl font-bold text-[#17201B]">{dashboard?.total_assets || 0}</p>
        </div>
        <div className="bg-white p-6 rounded-2xl shadow-soft border border-[#E5E9E5]">
          <div className="flex items-center gap-2 mb-2 text-blue-600">
            <Cpu className="w-4 h-4" /> <span className="text-xs uppercase tracking-wider font-semibold">In Use</span>
          </div>
          <p className="text-3xl font-bold text-[#17201B]">{dashboard?.in_use || 0}</p>
        </div>
        <div className="bg-white p-6 rounded-2xl shadow-soft border border-[#E5E9E5]">
          <div className="flex items-center gap-2 mb-2 text-yellow-600">
            <ArchiveX className="w-4 h-4" /> <span className="text-xs uppercase tracking-wider font-semibold">Decommissioned</span>
          </div>
          <p className="text-3xl font-bold text-[#17201B]">{dashboard?.decommissioned || 0}</p>
        </div>
        <div className="bg-white p-6 rounded-2xl shadow-soft border border-[#E5E9E5]">
          <div className="flex items-center gap-2 mb-2 text-orange-600">
            <Truck className="w-4 h-4" /> <span className="text-xs uppercase tracking-wider font-semibold">Handed Over</span>
          </div>
          <p className="text-3xl font-bold text-[#17201B]">{dashboard?.handed_over || 0}</p>
        </div>
        <div className="bg-white p-6 rounded-2xl shadow-soft border border-[#E5E9E5]">
          <div className="flex items-center gap-2 mb-2 text-emerald-600">
            <RefreshCw className="w-4 h-4" /> <span className="text-xs uppercase tracking-wider font-semibold">Recycled</span>
          </div>
          <p className="text-3xl font-bold text-[#17201B]">{dashboard?.recycled || 0}</p>
        </div>
      </div>

      <div className="flex gap-8 flex-1 overflow-hidden">
        {/* Table Area */}
        <div className={`bg-white rounded-2xl shadow-soft border border-[#E5E9E5] flex flex-col transition-all duration-500 ease-in-out ${selectedAsset ? 'w-2/3 hidden md:flex' : 'w-full'}`}>
          <div className="px-6 py-5 border-b border-[#E5E9E5]">
            <h3 className="font-semibold text-[#17201B]">Institutional Asset Registry</h3>
          </div>
          <div className="flex-1 overflow-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-[#F7F8F5] text-xs uppercase tracking-wider text-[#68736D] sticky top-0">
                  <th className="px-6 py-4 font-medium">Asset ID</th>
                  <th className="px-6 py-4 font-medium">Item</th>
                  <th className="px-6 py-4 font-medium">Department</th>
                  <th className="px-6 py-4 font-medium">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E5E9E5]">
                {assets.map((asset) => (
                  <tr 
                    key={asset.asset_id} 
                    onClick={() => openAssetDetails(asset)}
                    className={`cursor-pointer transition-colors ${selectedAsset?.asset_id === asset.asset_id ? 'bg-[#E8F3EC]' : 'hover:bg-[#F7F8F5]'}`}
                  >
                    <td className="px-6 py-4 font-medium text-[#17201B]">{asset.asset_id}</td>
                    <td className="px-6 py-4 text-[#68736D]">{asset.asset_name}</td>
                    <td className="px-6 py-4 text-[#68736D]">{asset.department}</td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(asset.status)}`}>
                        {asset.status.replace("_", " ")}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Details Panel */}
        {selectedAsset && (
          <div className="w-full md:w-1/3 bg-white rounded-2xl shadow-soft border border-[#E5E9E5] flex flex-col animate-in slide-in-from-right-4 duration-300">
            <div className="px-6 py-5 border-b border-[#E5E9E5] flex justify-between items-center bg-[#F7F8F5] rounded-t-2xl">
              <h3 className="font-semibold text-[#17201B]">Asset Profile</h3>
              <button onClick={closeDetails} className="p-1 hover:bg-zinc-200 rounded-full text-[#68736D]">
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="p-6 overflow-y-auto flex-1">
              <div className="flex items-start gap-4 mb-8">
                <div className="w-16 h-16 bg-white border border-[#E5E9E5] shadow-sm rounded-lg flex items-center justify-center shrink-0 p-1">
                  <QrCode className="w-full h-full text-[#17201B] opacity-80" />
                </div>
                <div>
                  <h4 className="text-xl font-bold text-[#17201B] leading-tight">{selectedAsset.asset_id}</h4>
                  <p className="text-[#68736D] text-sm mt-1">{selectedAsset.asset_name} • {selectedAsset.asset_type}</p>
                </div>
              </div>

              <div className="space-y-4 mb-8">
                <div>
                  <p className="text-xs text-[#68736D] uppercase tracking-wider font-semibold">Department</p>
                  <p className="text-[#17201B] font-medium">{selectedAsset.department}</p>
                </div>
                <div>
                  <p className="text-xs text-[#68736D] uppercase tracking-wider font-semibold">Serial Number</p>
                  <p className="text-[#17201B] font-medium">{selectedAsset.serial_number}</p>
                </div>
              </div>

              <h4 className="text-sm font-semibold text-[#17201B] border-b border-[#E5E9E5] pb-2 mb-6">Lifecycle Audit Trail</h4>
              
              {auditLoading ? (
                <div className="flex justify-center p-4"><Loader2 className="w-6 h-6 animate-spin text-[#2F7D57]" /></div>
              ) : (
                <div className="relative pl-6 space-y-6 before:absolute before:inset-y-2 before:left-[11px] before:w-0.5 before:bg-[#E5E9E5]">
                  {auditTrail.map((audit: any, index: number) => {
                    const isLast = index === auditTrail.length - 1;
                    return (
                      <div key={index} className="relative">
                        <div className={`absolute -left-[30px] w-4 h-4 rounded-full border-2 border-white ${isLast ? 'bg-[#2F7D57]' : 'bg-[#E5E9E5]'}`}></div>
                        <p className={`font-semibold text-sm ${isLast ? 'text-[#2F7D57]' : 'text-[#17201B]'}`}>
                          {audit.new_status.replace("_", " ")}
                        </p>
                        <p className="text-xs text-[#68736D] mt-1">{new Date(audit.timestamp).toLocaleString()}</p>
                        {audit.notes && (
                          <div className="mt-2 bg-[#F7F8F5] p-3 rounded-lg text-sm text-[#68736D] border border-[#E5E9E5]">
                            {audit.notes}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        )}
      </div>

    </div>
  );
}
