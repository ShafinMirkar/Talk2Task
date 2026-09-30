import { useState } from "react";

const STEPS = [
  "Enter the meeting URL",
  "Bot joins and listens",
  "AI analyzes the transcript",
  "Review tasks",
  "Tasks pushed to Jira",
];

export default function Landing({ onStart, busy, error }) {
  const [url, setUrl] = useState("");

  function handleSubmit(event) {
    event.preventDefault();
    if (!url.trim() || busy) return;
    onStart(url.trim());
  }

  return (
    <div className="landing">
      <h1>Talk2Task</h1>

      <p className="tagline">
        turns meeting discussions into actionable tasks, so nothing important
        gets forgotten
      </p>

      <p className="explain">
        For example, after a meeting someone might say, “Shafin will fix the
        login issue by Friday.” Normally, someone has to remember that, write
        it down, create a Jira ticket, assign it, and set the deadline.
      </p>

      <p className="explain">
        Talk2Task automates that whole process: it listens to the meeting →
        understands the commitments → turns them into tasks → lets you approve
        them → creates the Jira tickets.
      </p>

      <form className="meeting-form" onSubmit={handleSubmit}>
        <input
          type="url"
          value={url}
          onChange={(event) => setUrl(event.target.value)}
          placeholder="Paste meeting URL"
          aria-label="Meeting URL"
          aria-invalid={Boolean(error)}
          autoComplete="off"
        />

        {error && (
          <p className="form-error" role="alert">
            {error}
          </p>
        )}

        <button className="btn" type="submit" disabled={busy || !url.trim()}>
          {busy ? "Starting..." : "Start Meeting"}
        </button>
      </form>

      <section className="steps" aria-labelledby="how-it-works">
        <h2 id="how-it-works">How it works</h2>
        <ol>
          {STEPS.map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ol>
      </section>
    </div>
  );
}
