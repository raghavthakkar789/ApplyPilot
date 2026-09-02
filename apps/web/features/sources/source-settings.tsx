"use client";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { csrfHeaders } from "@/lib/csrf-client";

interface Entry {
  id: string;
  provider: string;
  employer_name: string;
  board_identifier: string;
  state: string;
  enabled: boolean;
}
interface DuplicateCandidate {
  id: string;
  left_job_id: string;
  right_job_id: string;
  reasons: string[];
  status: string;
}
export function SourceSettings() {
  const [entries, setEntries] = useState<Entry[]>([]);
  const [duplicates, setDuplicates] = useState<DuplicateCandidate[]>([]);
  const [status, setStatus] = useState("");
  const [provider, setProvider] = useState("greenhouse");
  const [deduplicationReason, setDeduplicationReason] = useState("");
  useEffect(() => {
    fetch("/api/source-registry", { credentials: "same-origin" })
      .then((r) => r.json())
      .then(setEntries)
      .catch(() => setStatus("Source registry could not be loaded."));
    fetch("/api/job-deduplication", { credentials: "same-origin" })
      .then((r) => r.json())
      .then(setDuplicates)
      .catch(() => setStatus("Deduplication review could not be loaded."));
  }, []);
  async function addRegistry(form: FormData) {
    setStatus("Validating the reviewed board through its official API…");
    const response = await fetch("/api/source-registry", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json", ...csrfHeaders() },
      body: JSON.stringify({
        provider,
        employer_name: form.get("employer_name"),
        employer_domain: form.get("employer_domain"),
        board_identifier: form.get("board_identifier"),
        careers_url: form.get("careers_url"),
        verification_method: "Owner reviewed employer careers page",
      }),
    });
    if (response.ok) {
      const entry = (await response.json()) as Entry;
      setEntries((current) => [...current, entry]);
      setStatus(`Board validation finished with state: ${entry.state}.`);
    } else {
      setStatus("Board validation failed safely. No source was enabled.");
    }
  }
  async function sync(provider: string, entryId?: string) {
    setStatus("Synchronization requested…");
    const suffix = entryId ? `?entry_id=${entryId}` : "";
    const response = await fetch(`/api/source-sync/${provider}${suffix}`, {
      method: "POST",
      credentials: "same-origin",
      headers: csrfHeaders(),
    });
    setStatus(
      response.ok
        ? "Synchronization completed."
        : "Synchronization could not be completed.",
    );
  }
  async function resolveDuplicate(
    candidateId: string,
    action: "merge" | "split",
  ) {
    if (deduplicationReason.trim().length < 3) {
      setStatus("Enter a review reason before resolving a duplicate.");
      return;
    }
    const response = await fetch(
      `/api/job-deduplication/${candidateId}/${action}`,
      {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json", ...csrfHeaders() },
        body: JSON.stringify({ reason: deduplicationReason }),
      },
    );
    if (response.ok) {
      const resolved = (await response.json()) as DuplicateCandidate;
      setDuplicates((current) =>
        current.map((item) => (item.id === resolved.id ? resolved : item)),
      );
      setDeduplicationReason("");
      setStatus(
        action === "merge"
          ? "Jobs merged with provenance retained."
          : "Jobs kept separate.",
      );
    } else {
      setStatus("The deduplication decision could not be saved.");
    }
  }
  return (
    <AppShell>
      <main className="workspace">
        <header className="workspace-header">
          <div>
            <p className="eyebrow">Approved sources</p>
            <h1>Source registry</h1>
            <p>
              Only reviewed public ATS boards are enabled. No crawling or
              submission occurs.
            </p>
          </div>
        </header>
        <section className="role-summary">
          <h2>Add reviewed board</h2>
          <p>
            Confirm the employer, domain, careers page, and public board
            identifier. ApplyPilot never guesses or crawls for identifiers.
          </p>
          <form action={addRegistry} className="profile-form-grid">
            <label>
              Provider
              <select
                value={provider}
                onChange={(event) => setProvider(event.target.value)}
              >
                <option value="greenhouse">Greenhouse</option>
                <option value="lever">Lever</option>
                <option value="ashby">Ashby</option>
              </select>
            </label>
            <label>
              Employer name
              <input name="employer_name" required maxLength={160} />
            </label>
            <label>
              Verified employer domain
              <input
                name="employer_domain"
                required
                placeholder="example.com"
              />
            </label>
            <label>
              Public board identifier
              <input name="board_identifier" required pattern="[A-Za-z0-9-]+" />
            </label>
            <label>
              Employer careers URL
              <input name="careers_url" type="url" required />
            </label>
            <button type="submit">Review and validate board</button>
          </form>
        </section>
        <section className="role-summary">
          <h2>Registered boards</h2>
          {entries.length ? (
            entries.map((entry) => (
              <article key={entry.id}>
                <strong>{entry.employer_name}</strong>
                <p>
                  {entry.provider} · {entry.board_identifier} · {entry.state} ·{" "}
                  {entry.enabled ? "Enabled" : "Disabled"}
                </p>
                <button
                  type="button"
                  onClick={() => sync(entry.provider, entry.id)}
                >
                  Synchronize
                </button>
              </article>
            ))
          ) : (
            <p>No reviewed ATS boards are configured.</p>
          )}
        </section>
        <section className="role-summary">
          <h2>Deduplication review</h2>
          {duplicates.filter((item) => item.status === "pending").length ? (
            duplicates
              .filter((item) => item.status === "pending")
              .map((item) => (
                <article key={item.id}>
                  <strong>Possible duplicate jobs</strong>
                  <p>{item.reasons.join(" · ")}</p>
                  <p>
                    {item.left_job_id} and {item.right_job_id}
                  </p>
                  <label>
                    Review reason
                    <input
                      value={deduplicationReason}
                      onChange={(event) =>
                        setDeduplicationReason(event.target.value)
                      }
                      minLength={3}
                      maxLength={500}
                    />
                  </label>
                  <div>
                    <button
                      type="button"
                      onClick={() => resolveDuplicate(item.id, "merge")}
                    >
                      Confirm duplicate merge
                    </button>
                    <button
                      type="button"
                      onClick={() => resolveDuplicate(item.id, "split")}
                    >
                      Keep jobs separate
                    </button>
                  </div>
                </article>
              ))
          ) : (
            <p>No uncertain duplicate candidates require review.</p>
          )}
        </section>
        <section className="role-summary">
          <h2>Remotive</h2>
          <p>
            Global public feed. Every listing retains Source: Remotive and its
            supplied link.
          </p>
          <button type="button" onClick={() => sync("remotive")}>
            Synchronize Remotive
          </button>
        </section>
        {status ? <p role="status">{status}</p> : null}
      </main>
    </AppShell>
  );
}
