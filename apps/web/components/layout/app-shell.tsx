"use client";

import { PanelLeft } from "lucide-react";
import Link from "next/link";
import { useState, type ReactNode } from "react";
import { OwnerMenu } from "@/components/navigation/owner-menu";
import { SidebarNav } from "@/components/navigation/sidebar-nav";

export function AppShell({ children }: { children: ReactNode }) {
  const [navigationOpen, setNavigationOpen] = useState(false);
  return (
    <div className="app-shell">
      <aside
        id="application-navigation"
        className="sidebar"
        aria-label="Application sidebar"
        data-drawer-open={navigationOpen}
      >
        <Link className="wordmark" href="/" aria-label="ApplyPilot home">
          <span>AP</span>
          <strong>ApplyPilot</strong>
        </Link>
        <SidebarNav />
        <OwnerMenu />
      </aside>
      <header className="mobile-header">
        <button
          type="button"
          aria-label={navigationOpen ? "Close navigation" : "Open navigation"}
          aria-controls="application-navigation"
          aria-expanded={navigationOpen}
          onClick={() => setNavigationOpen((open) => !open)}
        >
          <PanelLeft aria-hidden="true" />
        </button>
        <strong>ApplyPilot</strong>
      </header>
      {children}
    </div>
  );
}
