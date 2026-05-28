"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Bell, Search, User, LogOut } from "lucide-react";
import { motion } from "framer-motion";
import { useAuth } from "@/hooks/useAuth";
import { useState } from "react";

const workflowTabs = [
  { label: "Scan", href: "/scan" },
  { label: "Threat Analysis", href: "/threat" },
  { label: "Attack Simulation", href: "/attack" },
  { label: "Patch Generation", href: "/patches" },
];

export default function TopNav() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout, isAuthenticated } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);

  // Don't show nav on login page
  if (pathname === '/login' || pathname === '/unauthorized') {
    return null;
  }

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  return (
    <header className="border-b border-[var(--border)] bg-[var(--surface)] px-4 py-3 md:px-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <nav className="flex flex-wrap gap-3">
          {workflowTabs.map((tab) => {
            const isActive = pathname === tab.href;
            return (
              <div key={tab.href} className="relative">
                <Link
                  href={tab.href}
                  className={`text-xs uppercase tracking-[0.22em] font-mono pb-2 ${
                    isActive
                      ? "text-[var(--primary)]"
                      : "text-[var(--text-secondary)]"
                  }`}
                >
                  {tab.label}
                </Link>
                {isActive ? (
                  <motion.div
                    layoutId="workflow-underline"
                    className="absolute left-0 right-0 -bottom-1 h-0.5 bg-[var(--primary)]"
                  />
                ) : null}
              </div>
            );
          })}
        </nav>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 border border-[var(--border)] rounded-[var(--radius)] px-3 py-2">
            <Search className="h-4 w-4 text-[var(--text-secondary)]" />
            <input
              className="bg-transparent text-xs font-mono tracking-[0.14em] text-[var(--text-primary)] placeholder:text-[var(--text-secondary)] focus:outline-none"
              placeholder="SEARCH LOGS"
            />
          </div>
          <button className="h-9 w-9 border border-[var(--border)] rounded-[var(--radius)] flex items-center justify-center">
            <Bell className="h-4 w-4" />
          </button>
          
          {isAuthenticated && user ? (
            <div className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="h-9 w-9 border border-[var(--border)] rounded-[var(--radius)] flex items-center justify-center hover:border-blue-500"
              >
                <User className="h-4 w-4" />
              </button>
              
              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-lg shadow-lg z-50">
                  <div className="p-3 border-b border-[var(--border-color)]">
                    <p className="text-sm font-medium">{user.username}</p>
                    <p className="text-xs text-[var(--text-secondary)]">{user.email}</p>
                    <p className="text-xs text-[var(--text-secondary)] mt-1 capitalize">Role: {user.role}</p>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="w-full px-4 py-2 text-sm text-red-300 hover:bg-red-900 hover:bg-opacity-30 flex items-center gap-2 transition-colors"
                  >
                    <LogOut className="h-4 w-4" />
                    Logout
                  </button>
                </div>
              )}
            </div>
          ) : (
            <Link
              href="/login"
              className="h-9 w-9 border border-[var(--border)] rounded-[var(--radius)] flex items-center justify-center hover:border-blue-500"
            >
              <User className="h-4 w-4" />
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}
