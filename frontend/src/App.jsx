import { useState } from "react";
import {
  Show,
  SignIn,
  SignUp,
  UserButton,
  useAuth,
} from "@clerk/react";

import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  Link,
} from "react-router-dom";


// ============================================================
// LANDING
// ============================================================

function Landing() {
  return (
    <Show
      when="signed-out"
      fallback={<Navigate to="/dashboard" replace />}
    >
      <div className="auth-page">
        <div className="auth-container">

          <h1>Talk2Task</h1>

          <p>
            Turn meeting conversations into
            actionable Jira tasks.
          </p>

          <div className="auth-buttons">

            <Link to="/sign-in">
              Sign In
            </Link>

            <Link to="/sign-up">
              Create Account
            </Link>

          </div>

        </div>
      </div>
    </Show>
  );
}


// ============================================================
// SIGN IN
// ============================================================

function SignInPage() {
  return (
    <div className="auth-page">
      <SignIn
        routing="path"
        path="/sign-in"
        fallbackRedirectUrl="/dashboard"
      />
    </div>
  );
}


// ============================================================
// SIGN UP
// ============================================================

function SignUpPage() {
  return (
    <div className="auth-page">
      <SignUp
        routing="path"
        path="/sign-up"
        fallbackRedirectUrl="/dashboard"
      />
    </div>
  );
}


// ============================================================
// TEST BACKEND AUTHENTICATION
// ============================================================

function BackendAuthTest() {
  const { getToken } = useAuth();

  const testBackendAuth = async () => {
    try {
      const token = await getToken();

      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/api/me`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      console.log("Backend /api/me:", data);

    } catch (error) {
      console.error(
        "Backend authentication test failed:",
        error
      );
    }
  };

  return (
    <button onClick={testBackendAuth}>
      Test Backend Authentication
    </button>
  );
}


// ============================================================
// TEST MEETING
// ============================================================

function TestMeeting() {
  const { getToken } = useAuth();

  const [meetingUrl, setMeetingUrl] = useState("");
  const [loading, setLoading] = useState(false);

  async function createMeeting() {
    if (!meetingUrl.trim()) {
      alert("Please enter a meeting URL");
      return;
    }

    try {
      setLoading(true);

      const token = await getToken();

      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/api/meetings`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },

          body: JSON.stringify({
            meeting_url: meetingUrl,
          }),
        }
      );

      const data = await response.json();

      console.log(
        "Create meeting status:",
        response.status
      );

      console.log(
        "Create meeting response:",
        data
      );

      if (!response.ok) {
        alert(
          data.detail ||
          "Failed to start meeting"
        );

        return;
      }

      alert("Meeting bot started!");

    } catch (error) {
      console.error(
        "Meeting request failed:",
        error
      );

      alert(
        "Could not connect to Talk2Task backend."
      );

    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h2>Add Meeting</h2>

      <input
        type="url"
        value={meetingUrl}
        onChange={(event) =>
          setMeetingUrl(event.target.value)
        }
        placeholder="Paste Google Meet or Teams URL"
      />

      <button
        onClick={createMeeting}
        disabled={loading}
      >
        {loading
          ? "Starting..."
          : "Start Meeting"}
      </button>
    </div>
  );
}

// ============================================================
// DASHBOARD
// ============================================================

function Dashboard() {
  return (
    <Show
      when="signed-in"
      fallback={<Navigate to="/sign-in" replace />}
    >
      <div className="dashboard">

        <header className="header">

          <div className="logo">
            Talk2Task
          </div>

          <UserButton />

        </header>


        <main className="content">

          <h1>
            Dashboard
          </h1>

          <p>
            Welcome to Talk2Task.
          </p>


          <div>

            <BackendAuthTest />

          </div>


          <div>

            <TestMeeting />

          </div>

        </main>

      </div>
    </Show>
  );
}


// ============================================================
// APP
// ============================================================

function App() {
  return (
    <BrowserRouter>

      <Routes>

        <Route
          path="/"
          element={<Landing />}
        />

        <Route
          path="/sign-in/*"
          element={<SignInPage />}
        />

        <Route
          path="/sign-up/*"
          element={<SignUpPage />}
        />

        <Route
          path="/dashboard"
          element={<Dashboard />}
        />

        <Route
          path="*"
          element={
            <Navigate
              to="/"
              replace
            />
          }
        />

      </Routes>

    </BrowserRouter>
  );
}


export default App;