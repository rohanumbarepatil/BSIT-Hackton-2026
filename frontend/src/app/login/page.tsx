"use client";

import { useState } from 'react';
import { useAuth } from '@/context/AuthContext';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch('http://127.0.0.1:8001/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Login failed');
      login(data.access_token, data.user);
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#F7F8F5]">
      <div className="bg-white p-8 rounded-2xl shadow-soft max-w-md w-full border border-[#E5E9E5]">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-[#17201B]">WasteSense AI</h1>
          <p className="text-sm text-[#68736D] mt-1">Campus Sustainability Platform</p>
          <div className="mt-2 inline-block px-3 py-1 bg-blue-50 text-blue-700 text-xs font-semibold rounded-full">
            Demo Environment
          </div>
        </div>

        {error && <div className="mb-4 p-3 bg-red-50 text-red-700 text-sm rounded-lg">{error}</div>}

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-[#17201B] mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 rounded-lg border border-[#E5E9E5] focus:outline-none focus:ring-2 focus:ring-[#2F7D57]"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-[#17201B] mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 rounded-lg border border-[#E5E9E5] focus:outline-none focus:ring-2 focus:ring-[#2F7D57]"
              required
            />
          </div>
          <button
            type="submit"
            className="w-full py-2 bg-[#17201B] text-white rounded-lg font-medium hover:bg-[#2F7D57] transition"
          >
            Sign In
          </button>
        </form>
      </div>
    </div>
  );
}
