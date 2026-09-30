function formatDue(value) {
  if (!value) return null;

  // ISO date (YYYY-MM-DD) -> readable; anything else is shown as-is.
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
  if (!match) return value;

  const date = new Date(Number(match[1]), Number(match[2]) - 1, Number(match[3]));

  return date.toLocaleDateString(undefined, {
    weekday: "long",
    month: "short",
    day: "numeric",
  });
}

export default function TaskReview({
  tasks,
  decisions,
  onDecide,
  onSubmit,
  onBack,
  error,
}) {
  if (tasks.length === 0) {
    return (
      <div className="screen">
        <p className="state-text">No tasks were found in this meeting.</p>
        <div className="state-actions">
          <button className="btn" onClick={onBack}>
            Back
          </button>
        </div>
      </div>
    );
  }

  const remaining = tasks.filter((task) => !decisions[task._id]).length;
  const allReviewed = remaining === 0;

  return (
    <div className="review">
      <h1>Tasks</h1>

      {tasks.map((task) => {
        const decision = decisions[task._id];
        const due = formatDue(task.due_date);

        return (
          <article className="task" key={task._id}>
            <h2>{task.task}</h2>

            <p className="task-meta">
              {task.assignee || <span className="dim">Unassigned</span>}
              <br />
              {due ? `Due: ${due}` : <span className="dim">No deadline mentioned</span>}
              {!decision && (
                <>
                  <br />
                  <span className="dim">Needs your review</span>
                </>
              )}
            </p>

            <div className="task-actions">
              <button
                className={`btn ghost${decision === "approved" ? " chosen" : ""}`}
                aria-pressed={decision === "approved"}
                onClick={() => onDecide(task._id, "approved")}
              >
                {decision === "approved" ? "✓ Approved" : "Approve"}
              </button>

              <button
                className={`btn ghost${decision === "rejected" ? " chosen" : ""}`}
                aria-pressed={decision === "rejected"}
                onClick={() => onDecide(task._id, "rejected")}
              >
                {decision === "rejected" ? "× Rejected" : "Reject"}
              </button>
            </div>
          </article>
        );
      })}

      <div className="review-footer">
        <p>
          {allReviewed
            ? "All reviewed ✓"
            : `${remaining} ${remaining === 1 ? "task" : "tasks"} left to review`}
        </p>

        <button className="btn" onClick={onSubmit} disabled={!allReviewed}>
          Continue
        </button>

        {error && (
          <p className="form-error" role="alert">
            {error}
          </p>
        )}
      </div>
    </div>
  );
}
