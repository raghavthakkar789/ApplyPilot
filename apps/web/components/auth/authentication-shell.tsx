import { ShieldCheck } from "lucide-react";

export function AuthenticationShell({
  children,
  title,
  description,
}: {
  children: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <main className="auth-page">
      <section className="auth-panel" aria-labelledby="auth-title">
        <div className="auth-brand">
          <span>AP</span>
          <strong>ApplyPilot</strong>
        </div>
        <p className="eyebrow">Private owner workspace</p>
        <h1 id="auth-title">{title}</h1>
        <p className="auth-description">{description}</p>
        {children}
        <p className="auth-trust">
          <ShieldCheck aria-hidden="true" />
          Local, loopback-only access
        </p>
      </section>
    </main>
  );
}
