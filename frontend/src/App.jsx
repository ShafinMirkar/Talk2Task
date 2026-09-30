import {
  Show,
  SignIn,
  SignUp,
  UserButton,
} from "@clerk/react";

import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  Link,
} from "react-router-dom";

import Home from "./components/Home";


// ============================================================
// SIGNED-OUT LANDING
// ============================================================

function SignedOutLanding() {
  return (
    <Show
      when="signed-out"
      fallback={<Navigate to="/dashboard" replace />}
    >
      <div className="auth-page">
        <div className="auth-container">
          <h1>Talk2Task</h1>

          <p>
            turns meeting discussions into actionable tasks,
            so nothing important gets forgotten
          </p>

          <div className="auth-buttons">
            <Link to="/sign-in">Sign In</Link>
            <Link to="/sign-up">Create Account</Link>
          </div>
        </div>
      </div>
    </Show>
  );
}


// ============================================================
// SIGN IN / SIGN UP
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
// DASHBOARD (the Talk2Task workflow)
// ============================================================

function Dashboard() {
  return (
    <Show
      when="signed-in"
      fallback={<Navigate to="/sign-in" replace />}
    >
      <div className="app">
        <div className="user-corner">
          <UserButton />
        </div>

        <Home />
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
        <Route path="/" element={<SignedOutLanding />} />
        <Route path="/sign-in/*" element={<SignInPage />} />
        <Route path="/sign-up/*" element={<SignUpPage />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
