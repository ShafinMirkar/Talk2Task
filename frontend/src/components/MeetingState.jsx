import { useEffect, useState } from "react";

// "label", "label.", "label..", "label..." — width stays fixed.
function Dots({ label }) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => setCount((n) => (n + 1) % 4), 500);
    return () => clearInterval(timer);
  }, []);

  return (
    <span>
      {label}
      {".".repeat(count)}
      <span style={{ visibility: "hidden" }}>{".".repeat(3 - count)}</span>
    </span>
  );
}

export default function MeetingState({
  text,
  dotsLabel,
  error = false,
  children,
}) {
  return (
    <div className="screen" role="status" aria-live="polite">
      <p className={`state-text${error ? " state-error" : ""}`}>{text}</p>

      {dotsLabel && (
        <p className="state-sub">
          <Dots label={dotsLabel} />
        </p>
      )}

      {children && <div className="state-actions">{children}</div>}
    </div>
  );
}
