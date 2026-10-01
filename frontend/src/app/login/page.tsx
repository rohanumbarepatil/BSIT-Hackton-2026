"use client";

import { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Leaf, ScanLine, Recycle, Cpu, ArrowRight, Loader2, AlertCircle } from 'lucide-react';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { login } = useAuth();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isSubmitting) return;
    
    setIsSubmitting(true);
    setError('');
    
    try {
      // Use the NEXT_PUBLIC_API_URL or fallback to localhost for development
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8001';
      
      const res = await fetch(`${apiUrl}/api/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      
      const data = await res.json();
      
      if (!res.ok) {
        if (res.status === 401 || res.status === 403 || res.status === 400) {
          throw new Error('Email or password is incorrect.');
        } else {
          throw new Error('Unable to connect to WasteSense AI. Please try again.');
        }
      }
      
      login(data.access_token, data.user);
    } catch (err: any) {
      // Use a generic network error if it's a fetch failure without response
      if (err.message === 'Failed to fetch') {
        setError('Unable to connect to WasteSense AI. Please try again.');
      } else {
        setError(err.message || 'Unable to connect to WasteSense AI. Please try again.');
      }
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-[#F5F8F5] text-[#17201B] font-sans selection:bg-[#1F8A5B] selection:text-white">
      
      {/* LEFT SECTION (Branding & Features) */}
      <div className="md:w-[55%] lg:w-[60%] p-8 md:p-16 flex flex-col relative overflow-hidden bg-[#12372A] text-white justify-between">
        {/* Subtle background decorations */}
        <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-[#1F8A5B] rounded-full blur-[120px] opacity-20 -mr-[400px] -mt-[400px] pointer-events-none"></div>
        <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-[#159A9C] rounded-full blur-[100px] opacity-20 -ml-[200px] -mb-[200px] pointer-events-none"></div>

        <div className="relative z-10 flex items-center gap-3 mb-16">
          <div className="w-10 h-10 bg-white/10 backdrop-blur-md rounded-xl flex items-center justify-center border border-white/20">
            <Leaf className="w-6 h-6 text-[#38A169]" />
          </div>
          <span className="text-2xl font-bold tracking-tight">WasteSense AI</span>
        </div>

        <div className="relative z-10 max-w-2xl mt-auto mb-16">
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold leading-tight mb-6 tracking-tight">
            Make Every <br/>
            <span className="text-[#38A169]">Disposal Count.</span>
          </h1>
          <p className="text-lg md:text-xl text-[#F5F8F5]/80 leading-relaxed max-w-xl mb-12">
            AI-powered waste intelligence for a cleaner, more responsible campus.
          </p>

          {/* Feature Cards Grid */}
          <div className="grid grid-cols-2 gap-4 max-w-lg mb-12">
            <div className="bg-white/5 border border-white/10 p-4 rounded-2xl backdrop-blur-sm flex items-start gap-4 transition hover:bg-white/10">
              <div className="p-2 bg-[#1F8A5B]/20 rounded-lg text-[#38A169]">
                <ScanLine className="w-5 h-5" />
              </div>
              <div className="font-medium text-sm leading-tight mt-0.5 text-white/90">AI Waste <br/> Classification</div>
            </div>
            
            <div className="bg-white/5 border border-white/10 p-4 rounded-2xl backdrop-blur-sm flex items-start gap-4 transition hover:bg-white/10">
              <div className="p-2 bg-[#159A9C]/20 rounded-lg text-[#159A9C]">
                <Recycle className="w-5 h-5" />
              </div>
              <div className="font-medium text-sm leading-tight mt-0.5 text-white/90">Campus <br/> Smart Bins</div>
            </div>
            
            <div className="bg-white/5 border border-white/10 p-4 rounded-2xl backdrop-blur-sm flex items-start gap-4 transition hover:bg-white/10">
              <div className="p-2 bg-[#F5F8F5]/10 rounded-lg text-white">
                <Cpu className="w-5 h-5" />
              </div>
              <div className="font-medium text-sm leading-tight mt-0.5 text-white/90">E-Waste <br/> Lifecycle</div>
            </div>
            
            <div className="bg-white/5 border border-white/10 p-4 rounded-2xl backdrop-blur-sm flex items-start gap-4 transition hover:bg-white/10">
              <div className="p-2 bg-[#38A169]/20 rounded-lg text-[#38A169]">
                <Leaf className="w-5 h-5" />
              </div>
              <div className="font-medium text-sm leading-tight mt-0.5 text-white/90">Green <br/> Credits</div>
            </div>
          </div>

          {/* Ecosystem flowchart */}
          <div className="hidden md:flex items-center gap-3 text-[11px] font-medium tracking-wide uppercase text-white/60">
            <span className="bg-white/10 px-3 py-1.5 rounded-full">Waste Item</span>
            <ArrowRight className="w-3 h-3" />
            <span className="bg-[#1F8A5B]/20 px-3 py-1.5 rounded-full text-[#38A169]">AI Classification</span>
            <ArrowRight className="w-3 h-3" />
            <span className="bg-white/10 px-3 py-1.5 rounded-full">Correct Disposal</span>
            <ArrowRight className="w-3 h-3" />
            <span className="bg-[#159A9C]/20 px-3 py-1.5 rounded-full text-[#159A9C]">Smart Bin</span>
            <ArrowRight className="w-3 h-3" />
            <span className="bg-[#38A169]/20 px-3 py-1.5 rounded-full text-[#38A169]">Green Credits</span>
          </div>
        </div>

        <div className="relative z-10 text-xs text-white/40 mt-auto">
          &copy; {new Date().getFullYear()} WasteSense AI Campus Platform. All rights reserved.
        </div>
      </div>

      {/* RIGHT SECTION (Login Card) */}
      <div className="md:w-[45%] lg:w-[40%] flex items-center justify-center p-8 bg-[#F5F8F5]">
        <div className="w-full max-w-sm">
          
          <div className="mb-10">
            <div className="inline-flex items-center justify-center px-3 py-1 bg-[#1F8A5B]/10 text-[#1F8A5B] text-xs font-bold uppercase tracking-wider rounded-full mb-6">
              Demo Environment
            </div>
            <h2 className="text-3xl font-bold text-[#12372A] tracking-tight mb-2">Welcome back</h2>
            <p className="text-[#64716A]">Sign in to your WasteSense AI workspace.</p>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-100 text-red-700 text-sm rounded-xl flex items-start gap-3 animate-in fade-in slide-in-from-top-2">
              <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-5">
            <div className="space-y-1.5">
              <label className="block text-sm font-semibold text-[#12372A]">Email address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="student@wastesense.ai"
                className="w-full px-4 py-3 bg-white rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-[#1F8A5B] focus:border-transparent transition-shadow text-[#17201B] placeholder-gray-400"
                required
                disabled={isSubmitting}
              />
            </div>
            
            <div className="space-y-1.5">
              <div className="flex justify-between items-center">
                <label className="block text-sm font-semibold text-[#12372A]">Password</label>
              </div>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-4 py-3 bg-white rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-[#1F8A5B] focus:border-transparent transition-shadow text-[#17201B] placeholder-gray-400"
                required
                disabled={isSubmitting}
              />
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full py-3.5 mt-2 bg-[#1F8A5B] hover:bg-[#12372A] text-white rounded-xl font-semibold transition-colors flex items-center justify-center gap-2 shadow-sm disabled:opacity-70 disabled:cursor-not-allowed"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Signing in...
                </>
              ) : (
                "Sign In"
              )}
            </button>
          </form>

          <div className="mt-8 text-center">
            <p className="text-xs text-[#64716A] font-medium flex items-center justify-center gap-2">
              <span className="w-4 h-px bg-gray-300"></span>
              Secure role-based campus access
              <span className="w-4 h-px bg-gray-300"></span>
            </p>
          </div>
          
        </div>
      </div>
      
    </div>
  );
}
