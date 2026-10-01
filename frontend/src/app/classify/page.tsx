"use client";

import { useState, useRef } from "react";
import { UploadCloud, Camera, Loader2, Info, AlertTriangle, CheckCircle, ArrowRight, ScanLine } from "lucide-react";
import { classifyWaste, startDisposal, verifyDisposal } from "@/lib/api";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";

export default function ClassifyPage() {
  const { user } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  
  const [disposalSession, setDisposalSession] = useState<any>(null);
  const [disposalVerified, setDisposalVerified] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) {
      setFile(selected);
      setPreview(URL.createObjectURL(selected));
      setResult(null);
      setError(null);
      setDisposalSession(null);
      setDisposalVerified(false);
    }
  };

  const handleClassify = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const res = await classifyWaste(file);
      setResult(res);
    } catch (err: any) {
      setError(err.message || "Failed to classify image.");
    } finally {
      setLoading(false);
    }
  };

  const handleDisposal = async () => {
    if (!result || result.is_low_confidence || result.class_name === "mixed" || !user) return;
    setLoading(true);
    try {
      const session = await startDisposal(user.id, result);
      setDisposalSession(session);
    } catch (err: any) {
      setError(err.message || "Failed to start disposal session.");
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async () => {
    if (!disposalSession) return;
    setLoading(true);
    try {
      await verifyDisposal(disposalSession.session_id);
      setDisposalVerified(true);
    } catch (err: any) {
      setError(err.message || "Failed to verify disposal.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 animate-in fade-in duration-500 max-w-6xl mx-auto">
      
      {/* LEFT PANEL: UPLOAD */}
      <div className="bg-white rounded-2xl p-8 shadow-soft border border-[#E5E9E5] flex flex-col">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-[#17201B]">Identify your waste</h2>
          <p className="text-[#68736D] mt-2">Upload a clear image of a single waste item.</p>
        </div>
        
        <div 
          className={`flex-1 border-2 border-dashed rounded-xl flex flex-col items-center justify-center p-8 transition-colors ${
            preview ? 'border-[#3A8F83] bg-[#E8F3EC]/50' : 'border-[#E5E9E5] hover:border-[#68736D] bg-[#F7F8F5]'
          }`}
        >
          {preview ? (
            <div className="relative w-full h-64 md:h-80 rounded-lg overflow-hidden mb-4">
              <img src={preview} alt="Preview" className="w-full h-full object-contain" />
            </div>
          ) : (
            <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-sm mb-6 text-[#2F7D57]">
              <UploadCloud className="w-10 h-10" />
            </div>
          )}
          
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileChange} 
            accept="image/jpeg,image/png" 
            className="hidden" 
          />
          
          <div className="flex gap-4 w-full justify-center">
            <button 
              onClick={() => fileInputRef.current?.click()}
              className="px-6 py-3 bg-[#17201B] text-white rounded-lg font-medium hover:bg-[#2A3B31] transition flex items-center gap-2"
            >
              <UploadCloud className="w-4 h-4" /> 
              {preview ? "Change Image" : "Upload Image"}
            </button>
          </div>
        </div>

        {preview && !result && !loading && (
          <button 
            onClick={handleClassify}
            className="w-full mt-6 py-4 bg-[#2F7D57] text-white rounded-lg font-bold text-lg hover:bg-[#246244] transition shadow-lg shadow-emerald-500/20"
          >
            Analyze Image
          </button>
        )}
        
        {loading && !disposalSession && (
          <div className="w-full mt-6 py-4 bg-[#E8F3EC] text-[#2F7D57] rounded-lg font-medium flex items-center justify-center gap-3">
            <Loader2 className="w-5 h-5 animate-spin" />
            Running AI Classification...
          </div>
        )}
      </div>

      {/* RIGHT PANEL: RESULTS */}
      <div className="bg-white rounded-2xl p-8 shadow-soft border border-[#E5E9E5] flex flex-col min-h-[500px]">
        {!result && !error && !loading ? (
          <div className="flex-1 flex flex-col items-center justify-center text-center">
            <div className="w-24 h-24 bg-[#F7F8F5] rounded-full flex items-center justify-center mb-6 border border-[#E5E9E5]">
              <ScanLine className="w-10 h-10 text-[#68736D]" />
            </div>
            <h3 className="text-xl font-medium text-[#17201B] mb-2">Awaiting Image</h3>
            <p className="text-[#68736D] max-w-xs">Results and disposal guidance will appear here after classification.</p>
          </div>
        ) : error ? (
          <div className="flex-1 flex flex-col items-center justify-center text-center">
            <div className="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mb-4 text-[#C85B4A]">
              <AlertTriangle className="w-8 h-8" />
            </div>
            <h3 className="text-lg font-medium text-[#17201B] mb-2">Classification Error</h3>
            <p className="text-sm text-[#C85B4A]">{error}</p>
          </div>
        ) : result ? (
          <div className="flex-1 flex flex-col animate-in slide-in-from-right-4 duration-500">
            <h3 className="text-sm font-semibold text-[#68736D] uppercase tracking-wider mb-6">AI Prediction Result</h3>
            
            <div className="mb-8">
              <div className="flex justify-between items-end mb-2">
                <h1 className="text-4xl font-bold text-[#17201B] uppercase tracking-tight">{result.class_name}</h1>
                <span className="text-2xl font-light text-[#3A8F83]">{(result.confidence * 100).toFixed(0)}%</span>
              </div>
              <div className="w-full h-2 bg-[#E5E9E5] rounded-full overflow-hidden">
                <div 
                  className={`h-full rounded-full transition-all duration-1000 ${result.is_low_confidence ? 'bg-[#D89B35]' : 'bg-[#3A8F83]'}`}
                  style={{ width: `${result.confidence * 100}%` }}
                ></div>
              </div>
            </div>

            {/* Low Confidence Warning */}
            {result.is_low_confidence && (
              <div className="mb-6 p-4 bg-yellow-50 rounded-xl border border-yellow-200 flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-[#D89B35] shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-[#17201B]">Image needs a clearer view.</h4>
                  <p className="text-sm text-[#68736D] mt-1">Try photographing one item at a time in good lighting. Low confidence scans do not award credits.</p>
                </div>
              </div>
            )}

            {/* E-Waste Disclosure */}
            {result.class_name === "ewaste" && (
              <div className="mb-6 p-4 bg-blue-50 rounded-xl border border-blue-200 flex items-start gap-3">
                <Info className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-blue-900">Designated e-waste collection required.</h4>
                  <p className="text-sm text-blue-800 mt-1">Current AI e-waste training coverage is limited to battery imagery. Do not dispose of laptops or PCBs here.</p>
                </div>
              </div>
            )}

            {/* Disposal Guidance */}
            <div className="bg-[#F7F8F5] p-6 rounded-xl border border-[#E5E9E5] mb-auto">
              <h4 className="text-sm font-semibold text-[#68736D] uppercase mb-2">Recommended Category</h4>
              <p className="text-lg font-medium text-[#17201B] mb-4">{result.category_group}</p>
              
              <h4 className="text-sm font-semibold text-[#68736D] uppercase mb-2">Instructions</h4>
              <p className="text-[#17201B]">{result.guidance}</p>
            </div>

            {/* Action Buttons */}
            {!result.is_low_confidence && result.class_name !== "mixed" && (
              <div className="mt-8 pt-6 border-t border-[#E5E9E5]">
                {!disposalSession ? (
                  <button 
                    onClick={handleDisposal}
                    disabled={loading}
                    className="w-full py-4 bg-[#17201B] text-white rounded-lg font-medium hover:bg-[#2A3B31] transition flex items-center justify-center gap-2"
                  >
                    Proceed to Disposal <ArrowRight className="w-5 h-5" />
                  </button>
                ) : !disposalVerified ? (
                  <button 
                    onClick={handleVerify}
                    disabled={loading}
                    className="w-full py-4 bg-[#2F7D57] text-white rounded-lg font-bold hover:bg-[#246244] transition flex items-center justify-center gap-2"
                  >
                    {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : "Verify Disposal"}
                  </button>
                ) : (
                  <div className="w-full py-4 bg-[#E8F3EC] text-[#2F7D57] rounded-lg font-bold flex items-center justify-center gap-2 border border-[#2F7D57]/20">
                    <CheckCircle className="w-5 h-5" />
                    Disposal Verified! Check Green Credits.
                  </div>
                )}
              </div>
            )}
          </div>
        ) : null}
      </div>
      
    </div>
  );
}
