"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  AlertTriangle,
  Bug,
  FileText,
  LifeBuoy,
  Settings,
  Shield,
  Terminal,
} from "lucide-react";

const primaryNav = [
  { label: "Overview", href: "/", icon: Activity },
  { label: "Scan", href: "/scan", icon: Terminal },
  { label: "Agents", href: "/dashboard", icon: Shield },
  { label: "Patches", href: "/patches", icon: Bug },
  { label: "Reports", href: "/reports", icon: FileText },
];

const secondaryNav = [
  { label: "Settings", href: "/settings", icon: Settings },
  { label: "Support", href: "/support", icon: LifeBuoy },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-full md:w-[72px] lg:w-[240px] border-b md:border-b-0 md:border-r border-[var(--border)] bg-[var(--surface)] flex md:flex-col">
      <div className="flex-1 px-4 py-4 md:px-3 md:py-6">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 border border-[var(--border)] rounded-[var(--radius)] flex items-center justify-center">
            <AlertTriangle className="h-5 w-5 text-[var(--primary)]" />
          </div>
          <div className="hidden lg:block">
            <p className="text-sm font-semibold tracking-[0.12em]">SENTINELOS</p>
            <p className="text-[11px] uppercase tracking-[0.28em] text-[var(--text-secondary)]">
              Digital Command Center
            </p>
          </div>
        </div>

        <div className="mt-6 grid gap-2">
          {primaryNav.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 border border-[var(--border)] rounded-[var(--radius)] px-3 py-2 text-xs uppercase tracking-[0.2em] font-mono transition-colors ${
                  isActive
                    ? "border-[var(--primary)] text-[var(--primary)] border-l-4"
                    : "text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
                }`}
              >
                <Icon className="h-4 w-4" />
                <span className="hidden lg:inline">{item.label}</span>
              </Link>
            );
          })}
        </div>

        <div className="mt-6">
          <button className="hud-button hud-button-primary w-full">
            System Agents
          </button>
        </div>
      </div>

      <div className="border-t border-[var(--border)] px-4 py-4 md:px-3 md:py-4 grid gap-2">
        {secondaryNav.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 border border-[var(--border)] rounded-[var(--radius)] px-3 py-2 text-[10px] uppercase tracking-[0.2em] font-mono transition-colors ${
                isActive
                  ? "border-[var(--primary)] text-[var(--primary)] border-l-4"
                  : "text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
              }`}
            >
              <Icon className="h-4 w-4" />
              <span className="hidden lg:inline">{item.label}</span>
            </Link>
          );
        })}
      </div>
    </aside>
  );
}
