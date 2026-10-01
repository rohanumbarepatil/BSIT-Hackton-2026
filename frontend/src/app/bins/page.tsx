"use client";

import { useEffect, useState } from "react";
import { Recycle, AlertTriangle, CheckCircle, Clock, Info, Loader2, ArrowRight } from "lucide-react";
import { getBins, getBinAlerts, getBinPrediction, collectBin, getDashboardStats } from "@/lib/api";

export default function SmartBinsPage() {
  const [loading, setLoading] = useState(true);
  const [bins, setBins] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  
  const [selectedBin, setSelectedBin] = useState<any | null>(null);
  const [prediction, setPrediction] = useState<any | null>(null);
  const [predLoading, setPredLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      const [bRes, aRes, sRes] = await Promise.all([
        getBins(),
        getBinAlerts(),
        getDashboardStats()
      ]);
      setBins(bRes);
      setAlerts(aRes);
      setStats(sRes);
      
      // Update selected bin if it was open
      if (selectedBin) {
        const updated = bRes.find((b: any) => b.bin_id === selectedBin.bin_id);
        if (updated) openBinDetails(updated);
      }
    } catch (err: any) {
      setError(err.message || "Failed to load telemetry.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const openBinDetails = async (bin: any) => {
    setSelectedBin(bin);
    setPredLoading(true);
    try {
      const pred = await getBinPrediction(bin.bin_id);
      setPrediction(pred);
    } catch (err) {
      console.error(err);
    } finally {
      setPredLoading(false);
    }
  };

  const handleCollect = async (binId: string) => {
    setActionLoading(true);
    try {
      await collectBin(binId);
      await loadData();
    } catch (err) {
      console.error(err);
    } finally {
      setActionLoading(false);
    }
  };

  if (loading && bins.length === 0) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-[#2F7D57]" />
      </div>
    );
  }

  const getStatusConfig = (status: string) => {
    switch(status) {
      case "OVERFLOW": return { color: "bg-red-500", text: "text-red-700", border: "border-red-200", bg: "bg-red-50" };
      case "CRITICAL": return { color: "bg-[#C85B4A]", text: "text-[#C85B4A]", border: "border-red-100", bg: "bg-white" };
      case "WARNING": return { color: "bg-[#D89B35]", text: "text-[#D89B35]", border: "border-yellow-100", bg: "bg-white" };
      default: return { color: "bg-[#2F7D57]", text: "text-[#2F7D57]", border: "border-[#E5E9E5]", bg: "bg-white" };
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500">
      
      {/* Simulation Badge */}
      <div className="flex justify-between items-center mb-2">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-[#17201B] text-white rounded-lg text-xs font-bold uppercase tracking-wider">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
          Simulation Mode
        </div>
      </div>

      {error && <div className="p-4 bg-red-50 text-[#C85B4A] rounded-xl">{error}</div>}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
        
        {/* Left Column: Alerts & Stats */}
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-2xl shadow-soft border border-[#E5E9E5]">
            <h3 className="text-sm font-semibold text-[#68736D] uppercase tracking-wider mb-4">Network Overview</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-3xl font-bold text-[#17201B]">{stats?.total_bins || 0}</p>
                <p className="text-xs text-[#68736D] mt-1 uppercase tracking-wider">Total Bins</p>
              </div>
              <div>
                <p className="text-3xl font-bold text-[#D89B35]">{stats?.warning || 0}</p>
                <p className="text-xs text-[#68736D] mt-1 uppercase tracking-wider">Warnings</p>
              </div>
              <div>
                <p className="text-3xl font-bold text-[#C85B4A]">{stats?.critical || 0}</p>
                <p className="text-xs text-[#68736D] mt-1 uppercase tracking-wider">Critical</p>
              </div>
              <div>
                <p className="text-3xl font-bold text-red-600">{stats?.overflow || 0}</p>
                <p className="text-xs text-[#68736D] mt-1 uppercase tracking-wider">Overflow</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-2xl shadow-soft border border-[#E5E9E5]">
            <div className="flex items-center gap-2 mb-4">
              <AlertTriangle className="w-5 h-5 text-[#C85B4A]" />
              <h3 className="font-semibold text-[#17201B]">Attention Required</h3>
            </div>
            
            {alerts.length === 0 ? (
              <p className="text-sm text-[#68736D] text-center py-4 bg-[#F7F8F5] rounded-xl">No active alerts.</p>
            ) : (
              <div className="space-y-3">
                {alerts.map((alert, i) => (
                  <div key={i} className={`p-4 rounded-xl border text-sm ${alert.level === 'OVERFLOW' ? 'bg-red-50 border-red-200 text-red-800' : 'bg-yellow-50 border-yellow-200 text-yellow-800'}`}>
                    <strong>{alert.bin_id}</strong>: {alert.message}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Bin Grid */}
        <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-6">
          {bins.map((bin) => {
            const conf = getStatusConfig(bin.status);
            const isSelected = selectedBin?.bin_id === bin.bin_id;
            
            return (
              <div 
                key={bin.bin_id}
                onClick={() => openBinDetails(bin)}
                className={`relative overflow-hidden rounded-2xl shadow-soft border cursor-pointer transition-all hover:shadow-lg ${conf.bg} ${isSelected ? 'ring-2 ring-[#3A8F83] border-transparent' : conf.border}`}
              >
                {/* Visual Fill Background */}
                <div 
                  className={`absolute bottom-0 left-0 right-0 opacity-10 transition-all duration-1000 ${conf.color}`}
                  style={{ height: `${Math.min(100, bin.current_fill_percent)}%` }}
                ></div>
                
                <div className="relative z-10 p-6 flex flex-col h-full">
                  <div className="flex justify-between items-start mb-6">
                    <div>
                      <h3 className="text-xl font-bold text-[#17201B]">{bin.bin_id}</h3>
                      <p className="text-sm text-[#68736D]">{bin.location}</p>
                    </div>
                    <div className="text-right">
                      <span className={`text-2xl font-bold ${conf.text}`}>{bin.current_fill_percent}%</span>
                    </div>
                  </div>
                  
                  <div className="mt-auto pt-4 border-t border-black/5 flex justify-between items-center">
                    <span className="text-xs font-medium text-[#68736D] bg-black/5 px-2 py-1 rounded-md">{bin.waste_type}</span>
                    <span className={`text-xs font-bold ${conf.text}`}>{bin.status}</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Prediction / Action Panel (Modal-like behavior on mobile, bottom panel on desktop) */}
      {selectedBin && (
        <div className="bg-white rounded-2xl shadow-soft border border-[#3A8F83] p-6 lg:p-8 animate-in slide-in-from-bottom-8 duration-300">
          <div className="flex flex-col lg:flex-row justify-between lg:items-center gap-6">
            
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h2 className="text-2xl font-bold text-[#17201B]">{selectedBin.bin_id} Insights</h2>
                <span className="px-3 py-1 bg-[#F7F8F5] text-[#68736D] text-xs font-semibold rounded-full border border-[#E5E9E5]">
                  {selectedBin.location}
                </span>
              </div>
              <p className="text-[#68736D] text-sm max-w-lg">
                Predictive analytics generated from simulated telemetry timestamps.
              </p>
            </div>

            <div className="flex-1 bg-[#F7F8F5] p-6 rounded-xl border border-[#E5E9E5] relative overflow-hidden">
              {predLoading ? (
                <div className="flex justify-center py-4"><Loader2 className="w-6 h-6 animate-spin text-[#3A8F83]" /></div>
              ) : prediction ? (
                prediction.prediction_status === "INSUFFICIENT_HISTORY" ? (
                  <div className="flex items-center gap-3 text-[#68736D]">
                    <Info className="w-5 h-5 shrink-0" />
                    <p className="text-sm font-medium">Not enough telemetry history for a reliable prediction.</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs text-[#68736D] font-semibold uppercase mb-1">Fill Rate</p>
                      <p className="text-xl font-bold text-[#17201B]">{prediction.fill_rate_per_hour}% / hr</p>
                    </div>
                    <div>
                      <p className="text-xs text-[#68736D] font-semibold uppercase mb-1">Time to Full</p>
                      <p className="text-xl font-bold text-[#17201B]">{prediction.hours_to_full < 999 ? `${prediction.hours_to_full} hrs` : "Stable"}</p>
                    </div>
                  </div>
                )
              ) : null}
            </div>

            <div className="flex-shrink-0">
              <button 
                onClick={() => handleCollect(selectedBin.bin_id)}
                disabled={actionLoading || selectedBin.current_fill_percent === 0}
                className="w-full lg:w-auto px-8 py-4 bg-[#17201B] text-white rounded-xl font-bold hover:bg-[#2A3B31] transition disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {actionLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <CheckCircle className="w-5 h-5" />}
                Mark Collected
              </button>
            </div>
            
          </div>
        </div>
      )}

    </div>
  );
}
