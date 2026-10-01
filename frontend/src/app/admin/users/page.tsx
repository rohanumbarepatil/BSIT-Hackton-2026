"use client";

import { useEffect, useState } from "react";
import { getAdminUsers } from "@/lib/api";
import { Loader2, Users, ShieldAlert, BadgeCheck } from "lucide-react";

export default function AdminUsersPage() {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchUsers = async () => {
    try {
      setLoading(true);
      setError("");
      const data = await getAdminUsers();
      const normalizedUsers = Array.isArray(data) 
        ? data 
        : Array.isArray(data?.items) 
          ? data.items 
          : Array.isArray(data?.users) 
            ? data.users 
            : [];
      setUsers(normalizedUsers);
    } catch (err: any) {
      setError(err.message || "Failed to load users");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  if (loading) return (
    <div className="flex h-64 items-center justify-center">
      <Loader2 className="w-8 h-8 animate-spin text-[#1F8A5B]" />
    </div>
  );

  if (error) return (
    <div className="bg-red-50 p-6 rounded-xl border border-red-100 flex flex-col items-center justify-center h-64">
      <ShieldAlert className="w-10 h-10 text-red-500 mb-4" />
      <p className="text-red-700 font-medium">{error}</p>
      <button onClick={fetchUsers} className="mt-4 px-4 py-2 bg-white rounded-lg border border-red-200 text-red-700 hover:bg-red-50">Retry</button>
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Users className="w-8 h-8 text-[#1F8A5B]" />
        <h1 className="text-3xl font-bold text-[#17201B]">Users & Roles</h1>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-[#E5E9E5] overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-[#F5F8F5] border-b border-[#E5E9E5]">
                <th className="p-4 text-sm font-semibold text-[#68736D]">User</th>
                <th className="p-4 text-sm font-semibold text-[#68736D]">Email</th>
                <th className="p-4 text-sm font-semibold text-[#68736D]">Role</th>
                <th className="p-4 text-sm font-semibold text-[#68736D]">Green Credits</th>
                <th className="p-4 text-sm font-semibold text-[#68736D]">Status</th>
                <th className="p-4 text-sm font-semibold text-[#68736D]">Joined</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E5E9E5]">
              {users.length === 0 ? (
                <tr><td colSpan={6} className="p-8 text-center text-[#68736D]">No users found.</td></tr>
              ) : (
                users.map((u) => (
                  <tr key={u.id} className="hover:bg-gray-50">
                    <td className="p-4 font-medium text-[#17201B]">{u.name}</td>
                    <td className="p-4 text-sm text-[#68736D]">{u.email}</td>
                    <td className="p-4">
                      <span className="inline-flex px-2.5 py-1 text-xs font-semibold uppercase rounded-full bg-blue-50 text-blue-700 border border-blue-200">
                        {u.role}
                      </span>
                    </td>
                    <td className="p-4 font-bold text-[#38A169]">{u.green_credits}</td>
                    <td className="p-4">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded-full ${u.status === 'Active' ? 'bg-green-50 text-green-700' : 'bg-gray-100 text-gray-700'}`}>
                        {u.status === 'Active' && <BadgeCheck className="w-3.5 h-3.5" />}
                        {u.status}
                      </span>
                    </td>
                    <td className="p-4 text-sm text-[#68736D]">{new Date(u.joined).toLocaleDateString()}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
