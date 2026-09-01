import type { ReactNode } from "react";

export function EvidenceSection({
  title,
  count,
  children,
}: {
  title: string;
  count?: number;
  children: ReactNode;
}) {
  return (
    <section className="evidence-section">
      <h3>
        {title}
        {count !== undefined && <span>{count}</span>}
      </h3>
      {children}
    </section>
  );
}
