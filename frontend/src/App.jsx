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

function Dashboard() {
  const { getToken } = useAuth();

  const testBackendAuth = async () => {
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
  };

  return (
    <Show
      when="signed-in"
      fallback={<Navigate to="/sign-in" replace />}
    >
      <div className="dashboard">
        <header className="header">
          <div className="logo">Talk2Task</div>
          <UserButton />
        </header>

        <main className="content">
          <h1>Dashboard</h1>

          <button onClick={testBackendAuth}>
            Test Backend Authentication
          </button>
        </main>
      </div>
    </Show>
  );
}


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