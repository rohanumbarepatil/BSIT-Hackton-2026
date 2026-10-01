"use client";

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

type User = {
  id: string;
  name: string;
  email: string;
  role: string;
};

type AuthContextType = {
  user: User | null;
  token: string | null;
  login: (token: string, user: User) => void;
  logout: () => void;
  loading: boolean;
};

const AuthContext = createContext<AuthContextType>({
  user: null,
  token: null,
  login: () => {},
  logout: () => {},
  loading: true,
});

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const authData = localStorage.getItem('wastesense_auth');
    if (authData) {
      try {
        const parsed = JSON.parse(authData);
        if (parsed.access_token && parsed.user) {
          setToken(parsed.access_token);
          setUser(parsed.user);
        }
      } catch (e) {}
    }
    setLoading(false);
  }, []);

  const login = (newToken: string, newUser: User) => {
    const authObj = {
      access_token: newToken,
      user: newUser
    };
    localStorage.setItem('wastesense_auth', JSON.stringify(authObj));
    setToken(newToken);
    setUser(newUser);
    
    // Redirect based on role
    if (newUser.role === 'student') router.push('/student');
    else if (newUser.role === 'staff') router.push('/staff');
    else if (newUser.role === 'admin') router.push('/admin');
    else if (newUser.role === 'recycler') router.push('/recycler');
  };

  const logout = () => {
    localStorage.removeItem('wastesense_auth');
    setToken(null);
    setUser(null);
    router.push('/login');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
