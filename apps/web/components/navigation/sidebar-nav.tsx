import {
  Bookmark,
  BriefcaseBusiness,
  Compass,
  FileCheck2,
  Settings,
  SlidersHorizontal,
  UserRound,
} from "lucide-react";

const items = [
  ["Discover", Compass],
  ["Saved", Bookmark],
  ["Applications", BriefcaseBusiness],
  ["Evidence", FileCheck2],
  ["Profile", UserRound],
  ["Preferences", SlidersHorizontal],
  ["Settings", Settings],
] as const;

export function SidebarNav() {
  return (
    <nav aria-label="Primary navigation" className="sidebar-nav">
      {items.map(([label, Icon], index) => (
        <a
          key={label}
          href={index === 0 ? "/" : `#${label.toLowerCase()}`}
          aria-current={index === 0 ? "page" : undefined}
          title={label}
        >
          <Icon aria-hidden="true" size={20} />
          <span>{label}</span>
        </a>
      ))}
    </nav>
  );
}
