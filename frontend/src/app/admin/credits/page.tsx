"use client";

import { useEffect, useState } from "react";
import { getAdminCreditsOverview, getAdminCreditsStudents, getCreditHistory } from "@/lib/api";
import { Loader2, Leaf, ShieldAlert, Award, Users, CheckCircle, Calendar, ArrowLeft } from "lucide-react";

export default function AdminCreditsPage() {
  const [overview, setOverview] = useState<any>(null);
  const [students, setStudents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  
  // Student Detail View State
  const [selectedStudent, setSelectedStudent] = useState<any>(null);
  const [studentHistory, setStudentHistory] = useState<any[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError("");
      const [overviewData, studentsData] = await Promise.all([
        getAdminCreditsOverview(),
        getAdminCreditsStudents()
      ]);
      setOverview(overviewData);
      const normalizedStudents = Array.isArray(studentsData) 
        ? studentsData 
        : Array.isArray(studentsData?.items) 
          ? studentsData.items 
          : Array.isArray(studentsData?.students) 
            ? studentsData.students 
            : [];
      setStudents(normalizedStudents);
    } catch (err: any) {
      setError(err.message || "Failed to load green credits data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleStudentClick = async (student: any) => {
    setSelectedStudent(student);
    setLoadingHistory(true);
    try {
      const history = await getCreditHistory(student.id);
      const normalizedHistory = Array.isArray(history) 
        ? history 
        : Array.isArray(history?.history) 
          ? history.history 
          : Array.isArray(history?.items) 
            ? history.items 
            : [];
      setStudentHistory(normalizedHistory);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoadingHistory(false);
    }
  };

  if (loading) return (
    <div className="flex h-64 items-center justify-center">
      <Loader2 className="w-8 h-8 animate-spin text-[#1F8A5B]" />
    </div>
  );

  if (error) return (
    <div className="bg-red-50 p-6 rounded-xl border border-red-100 flex flex-col items-center justify-center h-64">
      <ShieldAlert className="w-10 h-10 text-red-500 mb-4" />
      <p className="text-red-700 font-medium">{error}</p>
      <button onClick={fetchData} className="mt-4 px-4 py-2 bg-white rounded-lg border border-red-200 text-red-700 hover:bg-red-50">Retry</button>
    </div>
  );
  
  if (selectedStudent) {
    return (
      <div className="space-y-6">
        <button 
          onClick={() => setSelectedStudent(null)}
          className="flex items-center gap-2 text-sm font-medium text-[#68736D] hover:text-[#17201B] transition"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Distribution
        </button>
        
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-[#E5E9E5] flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-[#17201B]">{selectedStudent.name}</h2>
            <p className="text-[#68736D]">{selectedStudent.email}</p>
          </div>
          <div className="text-right">
            <p className="text-sm font-semibold text-[#68736D] uppercase">Current Green Credits</p>
            <p className="text-4xl font-bold text-[#38A169]">{selectedStudent.total_credits}</p>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-[#E5E9E5] overflow-hidden">
          <div className="p-5 border-b border-[#E5E9E5]">
            <h3 className="text-lg font-bold text-[#17201B]">Credit History</h3>
          </div>
          
          {loadingHistory ? (
             <div className="flex p-8 justify-center"><Loader2 className="w-6 h-6 animate-spin text-[#1F8A5B]" /></div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-[#F5F8F5] border-b border-[#E5E9E5]">
                    <th className="p-4 text-sm font-semibold text-[#68736D]">Date</th>
                    <th className="p-4 text-sm font-semibold text-[#68736D]">Action</th>
                    <th className="p-4 text-sm font-semibold text-[#68736D]">Credits</th>
                    <th className="p-4 text-sm font-semibold text-[#68736D]">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#E5E9E5]">
                  {studentHistory.length === 0 ? (
                    <tr><td colSpan={4} className="p-8 text-center text-[#68736D]">No transactions found.</td></tr>
                  ) : (
                    studentHistory.map((txn, idx) => (
                      <tr key={idx} className="hover:bg-gray-50">
                        <td className="p-4 text-sm text-[#68736D]">
                          {new Date(txn.timestamp || txn.created_at || Date.now()).toLocaleDateString(undefined, { month: 'short', day: '2-digit' })}
                        </td>
                        <td className="p-4 text-sm font-medium text-[#17201B]">{txn.reason || txn.action}</td>
                        <td className="p-4 font-bold text-[#38A169]">+{txn.points}</td>
                        <td className="p-4">
                          <span className="inline-flex px-2.5 py-1 text-xs font-semibold rounded-full bg-green-50 text-green-700">
                            Verified
                          </span>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-3">
        <Leaf className="w-8 h-8 text-[#1F8A5B]" />
        <h1 className="text-3xl font-bold text-[#17201B]">Green Credits Analytics</h1>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-2xl shadow-soft border border-[#E5E9E5]">
          <h3 className="text-sm font-semibold text-[#68736D] uppercase flex items-center gap-2"><Award className="w-4 h-4"/> Total Awarded</h3>
          <p className="text-3xl font-bold mt-2 text-[#17201B]">{overview?.total_awarded || 0}</p>
        </div>
        <div className="bg-white p-6 rounded-2xl shadow-soft border border-[#E5E9E5]">
          <h3 className="text-sm font-semibold text-[#68736D] uppercase flex items-center gap-2"><Users className="w-4 h-4"/> Students Participating</h3>
          <p className="text-3xl font-bold mt-2 text-[#17201B]">{overview?.students_participating || 0}</p>
        </div>
        <div className="bg-white p-6 rounded-2xl shadow-soft border border-[#E5E9E5]">
          <h3 className="text-sm font-semibold text-[#68736D] uppercase flex items-center gap-2"><CheckCircle className="w-4 h-4"/> Verified Disposals</h3>
          <p className="text-3xl font-bold mt-2 text-[#17201B]">{overview?.verified_disposals || 0}</p>
        </div>
        <div className="bg-[#1F8A5B]/10 p-6 rounded-2xl shadow-soft border border-[#1F8A5B]/20">
          <h3 className="text-sm font-semibold text-[#1F8A5B] uppercase flex items-center gap-2"><Calendar className="w-4 h-4"/> Credits Today</h3>
          <p className="text-3xl font-bold mt-2 text-[#12372A]">{overview?.credits_today || 0}</p>
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-[#E5E9E5] overflow-hidden">
        <div className="p-5 border-b border-[#E5E9E5]">
          <h2 className="text-lg font-bold text-[#17201B]">Student Credit Distribution</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-[#F5F8F5] border-b border-[#E5E9E5]">
                <th className="p-4 text-sm font-semibold text-[#68736D]">Rank</th>
                <th className="p-4 text-sm font-semibold text-[#68736D]">Student</th>
                <th className="p-4 text-sm font-semibold text-[#68736D]">Email</th>
                <th className="p-4 text-sm font-semibold text-[#68736D]">Total Credits</th>
                <th className="p-4 text-sm font-semibold text-[#68736D]">Verified Disposals</th>
                <th className="p-4 text-sm font-semibold text-[#68736D]">Last Activity</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E5E9E5]">
              {students.length === 0 ? (
                <tr><td colSpan={6} className="p-8 text-center text-[#68736D]">No verified disposals yet.</td></tr>
              ) : (
                students.map((student) => (
                  <tr key={student.id} onClick={() => handleStudentClick(student)} className="hover:bg-gray-50 cursor-pointer transition">
                    <td className="p-4">
                      <span className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold ${student.rank === 1 ? 'bg-yellow-100 text-yellow-700' : student.rank === 2 ? 'bg-gray-200 text-gray-700' : student.rank === 3 ? 'bg-amber-100 text-amber-700' : 'text-[#68736D]'}`}>
                        {student.rank}
                      </span>
                    </td>
                    <td className="p-4 font-medium text-[#17201B]">{student.name}</td>
                    <td className="p-4 text-sm text-[#68736D]">{student.email}</td>
                    <td className="p-4 font-bold text-[#38A169]">{student.total_credits}</td>
                    <td className="p-4 font-medium text-[#17201B]">{student.verified_disposals}</td>
                    <td className="p-4 text-sm text-[#68736D]">
                      {student.last_activity ? new Date(student.last_activity).toLocaleDateString(undefined, { month: 'short', day: '2-digit' }) : 'Never'}
                    </td>
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
