import { useEffect } from "react";

const VISIBLE_MS = 6000;

function Toast({ toast, onDismiss }) {
  useEffect(() => {
    const timer = setTimeout(() => onDismiss(toast.id), VISIBLE_MS);
    return () => clearTimeout(timer);
  }, [toast.id, onDismiss]);

  return (
    <div className="toast">
      <small>{toast.title}</small>
      {toast.issueKey && <strong>{toast.issueKey}</strong>}
      <span>{toast.text}</span>
    </div>
  );
}

export default function Notification({ toasts, onDismiss }) {
  return (
    <div className="toasts" role="status" aria-live="polite">
      {toasts.map((toast) => (
        <Toast key={toast.id} toast={toast} onDismiss={onDismiss} />
      ))}
    </div>
  );
}
