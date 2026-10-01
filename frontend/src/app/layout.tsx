import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import AppShell from "@/components/layout/AppShell";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "WasteSense AI",
  description: "Intelligent Waste. Responsible Future.",
};

import { AuthProvider } from "@/context/AuthContext";
import RouteGuard from "@/components/layout/RouteGuard";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-[#F7F8F5] text-[#17201B] flex h-screen overflow-hidden`}>
        <AuthProvider>
          <RouteGuard>
            <AppShell>
              {children}
            </AppShell>
          </RouteGuard>
        </AuthProvider>
      </body>
    </html>
  );
}
