import type { ReactNode } from "react";

export function AlignmentMetric({
  label,
  value,
  detail,
  icon,
}: {
  label: string;
  value: string;
  detail: string;
  icon?: ReactNode;
}) {
  return (
    <div className="metric">
      <span className="metric-label">
        {icon}
        {label}
      </span>
      <strong>{value}</strong>
      <small>{detail}</small>
    </div>
  );
}
