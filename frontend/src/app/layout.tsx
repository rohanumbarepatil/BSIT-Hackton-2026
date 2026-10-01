import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/layout/Sidebar";
import TopHeader from "@/components/layout/TopHeader";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "WasteSense AI",
  description: "Intelligent Waste. Responsible Future.",
};

import { AuthProvider } from "@/context/AuthContext";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-[#F7F8F5] text-[#17201B] flex h-screen overflow-hidden`}>
        <AuthProvider>
          {/* Sidebar */}
          <div className="hidden md:flex md:w-64 md:flex-col fixed h-full z-10">
            <Sidebar />
          </div>
          
          {/* Main Content */}
          <main className="md:pl-64 flex flex-col w-full h-full">
            <TopHeader />
            <div className="flex-1 overflow-y-auto bg-[#F7F8F5]">
              <div className="p-8">
                {children}
              </div>
            </div>
          </main>
        </AuthProvider>
      </body>
    </html>
  );
}
