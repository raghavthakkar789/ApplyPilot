"use client";
import { useState } from "react";
import { csrfHeaders } from "@/lib/csrf-client";

export function ManualJobDialog({ onCreated }: { onCreated: () => void }) {
  const [open, setOpen] = useState(false);
  const [status, setStatus] = useState("");
  return (
    <div>
      <button
        className="manual-job-trigger"
        type="button"
        onClick={() => setOpen(true)}
      >
        Add manual job
      </button>
      {open ? (
        <div className="dialog-overlay">
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="manual-job-title"
            className="dialog-card"
          >
            <h2 id="manual-job-title">Add a manual job</h2>
            <p>
              Manually entered — source not automatically verified. URLs are
              stored but never fetched.
            </p>
            <form
              onSubmit={async (event) => {
                event.preventDefault();
                const body = Object.fromEntries(
                  new FormData(event.currentTarget),
                );
                const response = await fetch("/api/manual-jobs", {
                  method: "POST",
                  credentials: "same-origin",
                  headers: {
                    ...csrfHeaders(),
                    "Content-Type": "application/json",
                  },
                  body: JSON.stringify(body),
                });
                if (response.ok) {
                  setOpen(false);
                  onCreated();
                } else setStatus("The manual job could not be saved.");
              }}
            >
              <label>
                Title
              <input name="title" required maxLength={255} autoFocus />
              </label>
              <label>
                Employer
                <input name="employer" required maxLength={160} />
              </label>
              <label>
                Location
                <input name="location" maxLength={255} />
              </label>
              <label>
                Description
                <textarea name="description" maxLength={200000} />
              </label>
              <label>
                Source URL
                <input name="source_url" type="url" />
              </label>
              <div className="dialog-actions">
                <button type="button" onClick={() => setOpen(false)}>
                  Cancel
                </button>
                <button type="submit">Save manual job</button>
              </div>
            </form>
            {status ? <p role="alert">{status}</p> : null}
          </div>
        </div>
      ) : null}
    </div>
  );
}
