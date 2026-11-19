import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:5001";

export default function App() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function handleLogin(e) {
    e.preventDefault();
    setError("");
    setMessage("");

    const res = await fetch(`${API_URL}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    const data = await res.json();
    if (!res.ok) {
      setError(data.error || "Login failed");
      return;
    }

    setToken(data.token);
  }

  async function loadSecretNote() {
    setError("");
    setMessage("");

    const res = await fetch(`${API_URL}/secret-note`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const data = await res.json();
    if (!res.ok) {
      setError(data.error || "Could not load note");
      return;
    }

    setMessage(data.note);
  }

  function handleLogout() {
    setToken("");
    setMessage("");
    setError("");
    setPassword("");
  }

  if (!token) {
    return (
      <div className="auth-card">
        <div className="auth-header">
          <span className="auth-badge">Auth Demo</span>
          <h2>Student Login</h2>
          <p>Sign in with your account to access your dashboard</p>
        </div>

        <form onSubmit={handleLogin}>
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              placeholder="Enter username (student)"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              placeholder="Enter password (pass123)"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button type="submit" className="btn-primary">
            Log In
          </button>
        </form>

        {error && <div className="alert-error">{error}</div>}
      </div>
    );
  }

  return (
    <div className="auth-card">
      <div className="auth-header">
        <span className="auth-badge">Authenticated</span>
        <h2>Protected Dashboard</h2>
        <p>Your session token is active and verified</p>
      </div>

      <button onClick={loadSecretNote} className="btn-primary">
        Fetch Secret Note
      </button>
      <button onClick={handleLogout} className="btn-secondary">
        Log Out
      </button>

      {message && <div className="alert-success">{message}</div>}
      {error && <div className="alert-error">{error}</div>}
    </div>
  );
}