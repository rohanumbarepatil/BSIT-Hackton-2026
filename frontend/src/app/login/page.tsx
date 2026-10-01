"use client";

import { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { 
  Leaf, 
  ScanLine, 
  Trash2, 
  Cpu, 
  ArrowRight, 
  Loader2, 
  AlertCircle, 
  Mail, 
  Lock, 
  Eye, 
  EyeOff, 
  GraduationCap, 
  Users, 
  ShieldCheck, 
  Recycle
} from 'lucide-react';
import Image from 'next/image';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { login } = useAuth();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isSubmitting) return;
    
    setIsSubmitting(true);
    setError('');
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8001';
      
      const res = await fetch(`${apiUrl}/api/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      
      const data = await res.json();
      
      if (!res.ok) {
        if (res.status === 401 || res.status === 403 || res.status === 400) {
          throw new Error('Unable to sign in. Please check your email and password.');
        } else {
          throw new Error('Unable to connect to WasteSense AI. Please try again.');
        }
      }
      
      login(data.access_token, data.user);
    } catch (err: any) {
      if (err.message === 'Failed to fetch') {
        setError('Unable to connect to WasteSense AI. Please try again.');
      } else {
        setError(err.message || 'Unable to connect to WasteSense AI. Please try again.');
      }
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-white text-[#14201A] font-sans selection:bg-[#1F8A5B] selection:text-white">
      
      {/* LEFT SECTION (Story & Sustainability Visual) */}
      <div className="relative w-full md:w-[60%] flex flex-col justify-between overflow-hidden bg-[#12372A]">
        {/* Background Image */}
        <div className="absolute inset-0 z-0">
          <Image 
            src="/bg-campus.jpg" 
            alt="Campus Environment" 
            fill 
            className="object-cover object-center opacity-90"
            priority
          />
          {/* Gradient Overlay for Text Readability */}
          <div className="absolute inset-0 bg-gradient-to-t from-[#12372A]/90 via-[#12372A]/40 to-[#12372A]/10 mix-blend-multiply"></div>
          <div className="absolute inset-0 bg-gradient-to-r from-[#12372A]/80 to-transparent"></div>
        </div>

        {/* Top Brand */}
        <div className="relative z-10 p-8 md:p-12 flex items-center gap-3">
          <div className="w-12 h-12 bg-white/20 backdrop-blur-md rounded-xl flex items-center justify-center shadow-lg border border-white/20">
            <Leaf className="w-7 h-7 text-white" />
          </div>
          <div>
            <div className="text-2xl font-bold tracking-tight text-white flex items-center gap-1">
              WasteSense <span className="text-[#38A169]">AI</span>
            </div>
            <div className="text-sm font-medium text-white/80 tracking-wide">
              Campus Sustainability Platform
            </div>
          </div>
        </div>

        {/* Hero & Features */}
        <div className="relative z-10 p-8 md:p-12 mt-auto">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-white/10 backdrop-blur-md border border-white/20 rounded-full text-white/90 text-[10px] font-bold uppercase tracking-widest mb-6 shadow-sm">
            <Leaf className="w-3 h-3 text-[#38A169]" /> AI-Powered Waste Intelligence
          </div>
          
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white leading-[1.1] mb-6 tracking-tight drop-shadow-md">
            Make Every <br className="hidden sm:block" />
            <span className="text-[#38A169]">Disposal Count.</span>
          </h1>
          
          {/* Feature Cards Grid */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-10 max-w-3xl">
            <div className="bg-white/10 backdrop-blur-md border border-white/20 p-4 rounded-2xl flex flex-col items-center text-center gap-3 transition-transform hover:-translate-y-1 shadow-sm">
              <div className="p-2.5 bg-[#F5F8F5] rounded-xl text-[#12372A] shadow-sm">
                <ScanLine className="w-5 h-5" />
              </div>
              <div className="font-semibold text-xs leading-tight text-white drop-shadow-sm">AI Waste<br/>Classification</div>
            </div>
            
            <div className="bg-white/10 backdrop-blur-md border border-white/20 p-4 rounded-2xl flex flex-col items-center text-center gap-3 transition-transform hover:-translate-y-1 shadow-sm">
              <div className="p-2.5 bg-[#F5F8F5] rounded-xl text-[#159A9C] shadow-sm">
                <Trash2 className="w-5 h-5" />
              </div>
              <div className="font-semibold text-xs leading-tight text-white drop-shadow-sm">Campus<br/>Smart Bins</div>
            </div>
            
            <div className="bg-white/10 backdrop-blur-md border border-white/20 p-4 rounded-2xl flex flex-col items-center text-center gap-3 transition-transform hover:-translate-y-1 shadow-sm">
              <div className="p-2.5 bg-[#F5F8F5] rounded-xl text-[#38A169] shadow-sm">
                <Cpu className="w-5 h-5" />
              </div>
              <div className="font-semibold text-xs leading-tight text-white drop-shadow-sm">E-Waste<br/>Lifecycle</div>
            </div>
            
            <div className="bg-white/10 backdrop-blur-md border border-white/20 p-4 rounded-2xl flex flex-col items-center text-center gap-3 transition-transform hover:-translate-y-1 shadow-sm">
              <div className="p-2.5 bg-[#F5F8F5] rounded-xl text-[#1F8A5B] shadow-sm">
                <Leaf className="w-5 h-5" />
              </div>
              <div className="font-semibold text-xs leading-tight text-white drop-shadow-sm">Green<br/>Credits</div>
            </div>
          </div>

          {/* Ecosystem flowchart */}
          <div className="hidden md:flex flex-wrap items-center gap-3 text-[10px] lg:text-xs font-bold tracking-wide uppercase text-white/80 drop-shadow-sm mb-12">
            <span className="bg-[#12372A]/60 backdrop-blur-sm border border-white/10 px-3 py-1.5 rounded-full">Waste Item</span>
            <ArrowRight className="w-3 h-3 text-white/60" />
            <span className="bg-[#12372A]/60 backdrop-blur-sm border border-white/10 px-3 py-1.5 rounded-full">AI Classification</span>
            <ArrowRight className="w-3 h-3 text-white/60" />
            <span className="bg-[#12372A]/60 backdrop-blur-sm border border-white/10 px-3 py-1.5 rounded-full">Correct Disposal</span>
            <ArrowRight className="w-3 h-3 text-white/60" />
            <span className="bg-[#12372A]/60 backdrop-blur-sm border border-[#159A9C]/30 px-3 py-1.5 rounded-full text-[#159A9C]">Smart Bin</span>
            <ArrowRight className="w-3 h-3 text-white/60" />
            <span className="bg-[#12372A]/60 backdrop-blur-sm border border-[#38A169]/30 px-3 py-1.5 rounded-full text-[#38A169]">Green Credits</span>
          </div>

          {/* Bottom Context Statement */}
          <div className="bg-[#12372A]/80 backdrop-blur-md border border-white/10 p-5 rounded-2xl max-w-2xl text-white/90 text-sm md:text-base font-medium leading-relaxed">
            AI-powered campus waste intelligence. Built for smarter segregation, responsible e-waste handling and measurable sustainability.
          </div>
        </div>
      </div>

      {/* RIGHT SECTION (Login Panel) */}
      <div className="w-full md:w-[40%] flex items-center justify-center p-6 lg:p-12 bg-[#F5F8F5]">
        
        {/* Premium Login Card */}
        <div className="w-full max-w-[420px] bg-white p-8 lg:p-10 rounded-[32px] shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-gray-100 relative">
          
          {/* Header */}
          <div className="mb-10 text-center">
            <div className="inline-flex items-center justify-center px-3 py-1.5 bg-[#1F8A5B]/10 text-[#1F8A5B] text-[10px] font-bold uppercase tracking-widest rounded-full mb-6">
              Demo Environment
            </div>
            <div className="flex justify-center mb-4">
              <Leaf className="w-10 h-10 text-[#1F8A5B]" />
            </div>
            <h2 className="text-2xl lg:text-3xl font-bold text-[#14201A] tracking-tight mb-2">Welcome back</h2>
            <p className="text-[#64716A] text-sm lg:text-base">Sign in to your WasteSense AI workspace.</p>
          </div>

          {/* Role Access Strip (Informational) */}
          <div className="flex justify-center gap-2 mb-8 flex-wrap">
            <div className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-50 border border-gray-100 rounded-lg text-xs font-semibold text-[#64716A]">
              <GraduationCap className="w-3.5 h-3.5" /> Student
            </div>
            <div className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-50 border border-gray-100 rounded-lg text-xs font-semibold text-[#64716A]">
              <Users className="w-3.5 h-3.5" /> Staff
            </div>
            <div className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-50 border border-gray-100 rounded-lg text-xs font-semibold text-[#64716A]">
              <ShieldCheck className="w-3.5 h-3.5" /> Admin
            </div>
            <div className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-50 border border-gray-100 rounded-lg text-xs font-semibold text-[#64716A]">
              <Recycle className="w-3.5 h-3.5" /> Recycler
            </div>
          </div>

          {/* Error State */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-100 text-red-700 text-sm rounded-xl flex items-start gap-3 animate-in fade-in slide-in-from-top-2">
              <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
              <span className="font-medium">{error}</span>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleLogin} className="space-y-5">
            <div className="space-y-2">
              <label className="block text-sm font-semibold text-[#14201A]">Email address</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-400">
                  <Mail className="w-5 h-5" />
                </div>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="student@wastesense.ai"
                  className="w-full pl-11 pr-4 py-3.5 bg-gray-50 hover:bg-gray-100/50 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-[#1F8A5B] focus:border-transparent focus:bg-white transition-all text-[#14201A] placeholder-gray-400 font-medium"
                  required
                  disabled={isSubmitting}
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <label className="block text-sm font-semibold text-[#14201A]">Password</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-400">
                  <Lock className="w-5 h-5" />
                </div>
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  className="w-full pl-11 pr-12 py-3.5 bg-gray-50 hover:bg-gray-100/50 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-[#1F8A5B] focus:border-transparent focus:bg-white transition-all text-[#14201A] placeholder-gray-400 font-medium"
                  required
                  disabled={isSubmitting}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-400 hover:text-gray-600 transition-colors focus:outline-none"
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full py-4 mt-4 bg-[#1F8A5B] hover:bg-[#12372A] text-white rounded-xl font-bold text-base transition-all flex items-center justify-center gap-2 shadow-[0_4px_14px_0_rgba(31,138,91,0.39)] hover:shadow-[0_6px_20px_rgba(31,138,91,0.23)] hover:-translate-y-[1px] disabled:opacity-70 disabled:cursor-not-allowed disabled:transform-none disabled:shadow-none"
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

          {/* Footer */}
          <div className="mt-8 text-center">
            <p className="text-xs text-[#64716A] font-semibold flex items-center justify-center gap-3">
              <ShieldCheck className="w-4 h-4 text-[#1F8A5B]" />
              Secure role-based campus access
            </p>
          </div>
          
        </div>
      </div>
      
    </div>
  );
}
