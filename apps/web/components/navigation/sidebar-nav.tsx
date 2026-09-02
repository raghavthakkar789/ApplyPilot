"use client";

import {
  Bookmark,
  BriefcaseBusiness,
  Compass,
  Database,
  FileCheck2,
  Files,
  Settings,
  SlidersHorizontal,
  UserRound,
} from "lucide-react";
import { usePathname } from "next/navigation";

const items = [
  ["Discover", Compass, "/"],
  ["Saved", Bookmark, "#saved"],
  ["Applications", BriefcaseBusiness, "#applications"],
  ["Evidence", FileCheck2, "/evidence"],
  ["Resumes", Files, "/resumes"],
  ["Sources", Database, "/sources"],
  ["Profile", UserRound, "/profile"],
  ["Preferences", SlidersHorizontal, "#preferences"],
  ["Settings", Settings, "#settings"],
] as const;

export function SidebarNav() {
  const pathname = usePathname();
  return (
    <nav aria-label="Primary navigation" className="sidebar-nav">
      {items.map(([label, Icon, href]) => (
        <a
          key={label}
          href={href}
          aria-current={pathname === href ? "page" : undefined}
          title={label}
        >
          <Icon aria-hidden="true" size={20} />
          <span>{label}</span>
        </a>
      ))}
    </nav>
  );
}
