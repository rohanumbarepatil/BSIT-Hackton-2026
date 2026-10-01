"use client";

import { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";

export default function QRScannerPage() {
  const [assetId, setAssetId] = useState("");
  const { user } = useAuth();
  const router = useRouter();

  const handleScan = () => {
    if (!assetId) return;
    fetch(`http://127.0.0.1:8001/api/v1/ewaste/assets/${assetId}`, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    .then(res => res.json())
    .then(data => {
      if (data.detail) alert(data.detail);
      else {
        alert(`Scanned: ${data.asset_name} (${data.status})`);
        // We could redirect to a details page, or show details here.
      }
    });
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500 max-w-lg mx-auto mt-20">
      <div className="bg-white p-8 rounded-2xl shadow-soft border border-[#E5E9E5] text-center">
        <h2 className="text-2xl font-bold mb-4">Scan E-Waste Asset</h2>
        <div className="w-full h-48 bg-zinc-100 rounded-xl flex items-center justify-center mb-6 border-2 border-dashed border-zinc-300">
          <span className="text-zinc-500">Camera Viewfinder</span>
        </div>
        <p className="text-sm text-zinc-500 mb-4">or enter asset ID manually</p>
        <input
          type="text"
          value={assetId}
          onChange={e => setAssetId(e.target.value)}
          placeholder="LAB-PC-001"
          className="w-full px-4 py-2 border rounded-lg mb-4 text-center text-lg"
        />
        <button 
          onClick={handleScan}
          className="w-full py-3 bg-emerald-500 text-white rounded-lg font-medium"
        >
          Scan / Find
        </button>
      </div>
    </div>
  );
}
