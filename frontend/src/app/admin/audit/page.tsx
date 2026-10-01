"use client";

import { useEffect, useState } from "react";
import { getAdminAuditLogs } from "@/lib/api";
import { Loader2, Activity, ShieldAlert } from "lucide-react";

export default function AdminAuditLogsPage() {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchLogs = async () => {
    try {
      setLoading(true);
      setError("");
      const data = await getAdminAuditLogs();
      const normalizedLogs = Array.isArray(data) 
        ? data 
        : Array.isArray(data?.items) 
          ? data.items 
          : Array.isArray(data?.events) 
            ? data.events 
            : [];
      setLogs(normalizedLogs);
    } catch (err: any) {
      setError(err.message || "Failed to load audit logs");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
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
      <button onClick={fetchLogs} className="mt-4 px-4 py-2 bg-white rounded-lg border border-red-200 text-red-700 hover:bg-red-50">Retry</button>
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Activity className="w-8 h-8 text-[#1F8A5B]" />
        <h1 className="text-3xl font-bold text-[#17201B]">Audit Logs</h1>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-[#E5E9E5] overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-[#F5F8F5] border-b border-[#E5E9E5]">
                <th className="p-4 text-sm font-semibold text-[#68736D]">Timestamp</th>
                <th className="p-4 text-sm font-semibold text-[#68736D]">Actor</th>
                <th className="p-4 text-sm font-semibold text-[#68736D]">Role</th>
                <th className="p-4 text-sm font-semibold text-[#68736D]">Action</th>
                <th className="p-4 text-sm font-semibold text-[#68736D]">Entity</th>
                <th className="p-4 text-sm font-semibold text-[#68736D]">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E5E9E5]">
              {logs.length === 0 ? (
                <tr><td colSpan={6} className="p-8 text-center text-[#68736D]">No audit activity recorded yet.</td></tr>
              ) : (
                logs.map((log, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="p-4 text-sm whitespace-nowrap text-[#68736D]">
                      {new Date(log.timestamp).toLocaleString(undefined, { 
                        day: '2-digit', month: 'short', year: 'numeric', 
                        hour: '2-digit', minute: '2-digit' 
                      })}
                    </td>
                    <td className="p-4 font-medium text-[#17201B]">{log.actor}</td>
                    <td className="p-4">
                      <span className="inline-flex px-2 py-0.5 text-[10px] font-bold uppercase rounded bg-gray-100 text-gray-600 border border-gray-200">
                        {log.role}
                      </span>
                    </td>
                    <td className="p-4 text-sm font-medium text-blue-700">{log.action}</td>
                    <td className="p-4 text-sm text-[#17201B]">{log.entity}</td>
                    <td className="p-4 text-sm text-[#68736D] max-w-md truncate">{log.details}</td>
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
