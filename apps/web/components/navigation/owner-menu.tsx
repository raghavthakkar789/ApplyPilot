import { ChevronUp, CircleUserRound } from "lucide-react";

export function OwnerMenu() {
  return (
    <button
      className="owner-menu"
      type="button"
      aria-label="Open owner and session menu"
    >
      <CircleUserRound aria-hidden="true" size={22} />
      <span>
        <strong>Local owner</strong>
        <small>Private workspace</small>
      </span>
      <ChevronUp aria-hidden="true" size={16} />
    </button>
  );
}
