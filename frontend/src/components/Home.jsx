import { useCallback, useEffect, useRef, useState } from "react";
import { useAuth } from "@clerk/react";

import {
  createMeeting,
  getMeetingStatus,
  getMeetingTasks,
  reviewActionItems,
} from "../api/api";

import Landing from "./Landing";
import MeetingState from "./MeetingState";
import TaskReview from "./TaskReview";
import Notification from "./Notification";

const POLL_MS = 3000;

// Vexa lifecycle + Talk2Task processing status -> user-facing stage.
function toStage(status) {
  switch (status) {
    case "active":
    case "stopping":
      return "listening";
    case "completed":
    case "analyzing":
      return "analyzing";
    case "processed":
      return "processed";
    case "failed":
      return "failed";
    default:
      // requested, joining, awaiting_admission, needs_help
      return "waiting";
  }
}

const POLLING_STAGES = ["waiting", "listening", "analyzing"];

export default function Home() {
  const { getToken, signOut } = useAuth();

  const [stage, setStage] = useState("landing");
  const [meetingId, setMeetingId] = useState(null);
  const [starting, setStarting] = useState(false);
  const [formError, setFormError] = useState("");
  const [tasks, setTasks] = useState([]);
  const [decisions, setDecisions] = useState({});
  const [reviewError, setReviewError] = useState("");
  const [toasts, setToasts] = useState([]);

  const toastId = useRef(0);

  const dismissToast = useCallback((id) => {
    setToasts((current) => current.filter((toast) => toast.id !== id));
  }, []);

  function notify(items) {
    const created = items.map((item) => ({
      id: ++toastId.current,
      ...item,
    }));
    setToasts((current) => [...current, ...created]);
  }

  function reset() {
    setStage("landing");
    setMeetingId(null);
    setTasks([]);
    setDecisions({});
    setFormError("");
    setReviewError("");
  }

  // ---------- start ----------

  async function startMeeting(url) {
    setFormError("");
    setStarting(true);

    try {
      const token = await getToken();
      const meeting = await createMeeting(token, url);

      setMeetingId(meeting._id);
      setStage("waiting");
    } catch (error) {
      if (error.status === 401) {
        signOut();
        return;
      }

      setFormError(
        error.status === 400
          ? "Enter a valid Google Meet or Teams URL."
          : "Couldn't start the meeting. Please try again."
      );
    } finally {
      setStarting(false);
    }
  }

  // ---------- tasks ----------

  async function loadTasks(id) {
    setStage("loadingTasks");

    try {
      const token = await getToken();
      const items = await getMeetingTasks(token, id);

      setTasks(items);
      setDecisions({});
      setReviewError("");
      setStage("review");
    } catch (error) {
      if (error.status === 401) {
        signOut();
        return;
      }

      setStage("tasksError");
    }
  }

  // ---------- polling ----------
  // One loop at a time: the effect only restarts when polling turns on/off
  // or the meeting changes, and each request waits for the previous one.

  const polling = POLLING_STAGES.includes(stage);

  useEffect(() => {
    if (!polling || !meetingId) return;

    let cancelled = false;
    let timer;

    async function tick() {
      try {
        const token = await getToken();
        const { status } = await getMeetingStatus(token, meetingId);

        if (cancelled) return;

        const next = toStage(status);

        if (next === "processed") {
          loadTasks(meetingId);
          return;
        }

        if (next === "failed") {
          setStage("failed");
          return;
        }

        setStage(next);
      } catch (error) {
        if (cancelled) return;

        if (error.status === 401) {
          signOut();
          return;
        }

        if (error.status === 404) {
          setStage("failed");
          return;
        }

        // Transient error: keep polling.
        console.warn("Status check failed, retrying:", error);
      }

      if (!cancelled) timer = setTimeout(tick, POLL_MS);
    }

    tick();

    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [polling, meetingId]);

  // ---------- review ----------

  function decide(id, decision) {
    setDecisions((current) => ({ ...current, [id]: decision }));
  }

  async function submitReview() {
    const approved = tasks
      .filter((task) => decisions[task._id] === "approved")
      .map((task) => task._id);

    const rejected = tasks
      .filter((task) => decisions[task._id] === "rejected")
      .map((task) => task._id);

    setReviewError("");
    setStage("submitting");

    try {
      const token = await getToken();
      const result = await reviewActionItems(token, approved, rejected);

      // Only announce what the backend confirmed.
      const created = result.jira_created || [];

      notify(
        created.length > 0
          ? created.map((item) => ({
              title: "Jira task created",
              issueKey: item.issue_key,
              text: item.task,
            }))
          : [{ title: "Review saved", text: "No tasks were sent to Jira." }]
      );

      reset();
    } catch (error) {
      if (error.status === 401) {
        signOut();
        return;
      }

      // Stay on the review screen with every decision intact.
      setReviewError("We couldn't create the Jira tasks. Please try again.");
      setStage("review");
    }
  }

  // ---------- render ----------

  let content;

  switch (stage) {
    case "waiting":
      content = <MeetingState text="admit the bot in the meet" />;
      break;

    case "listening":
      content = <MeetingState text="bot is listening in the meet" />;
      break;

    case "analyzing":
      content = (
        <MeetingState
          text="AI is analyzing the transcript"
          dotsLabel="creating action-items"
        />
      );
      break;

    case "failed":
      content = (
        <MeetingState text="We couldn't connect to the meeting." error>
          <button className="btn" onClick={reset}>
            Back
          </button>
        </MeetingState>
      );
      break;

    case "loadingTasks":
      content = <MeetingState text="Loading tasks..." />;
      break;

    case "tasksError":
      content = (
        <MeetingState text="Couldn't load tasks." error>
          <button className="btn" onClick={() => loadTasks(meetingId)}>
            Try again
          </button>
          <button className="btn ghost" onClick={reset}>
            Back
          </button>
        </MeetingState>
      );
      break;

    case "review":
      content = (
        <TaskReview
          tasks={tasks}
          decisions={decisions}
          onDecide={decide}
          onSubmit={submitReview}
          onBack={reset}
          error={reviewError}
        />
      );
      break;

    case "submitting":
      content = <MeetingState text="creating Jira tasks" dotsLabel="just a moment" />;
      break;

    default:
      content = (
        <Landing onStart={startMeeting} busy={starting} error={formError} />
      );
  }

  return (
    <>
      {content}
      <Notification toasts={toasts} onDismiss={dismissToast} />
    </>
  );
}
