import React, { useEffect, useState } from "react";
import { DetectorCard } from "./components/DetectorCard";
import { FileUpload } from "./components/FileUpload";
import { IncidentList } from "./components/IncidentList";

export type DetectorType = "fire" | "flood" | "social-distance";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api";
const AUTH_STORAGE_KEY = "resq-operator";

interface OperatorSession {
  id: number;
  name: string;
  email: string;
  role: string;
  is_staff: boolean;
}

const readStoredOperator = (): OperatorSession | null => {
  try {
    const saved = localStorage.getItem(AUTH_STORAGE_KEY);
    return saved ? (JSON.parse(saved) as OperatorSession) : null;
  } catch {
    localStorage.removeItem(AUTH_STORAGE_KEY);
    return null;
  }
};

export const App: React.FC = () => {
  const [operator, setOperator] = useState<OperatorSession | null>(readStoredOperator);
  const [checkingAuth, setCheckingAuth] = useState(Boolean(operator));
  const [loading, setLoading] = useState<DetectorType | null>(null);
  const [lastResponse, setLastResponse] = useState<any | null>(null);
  const [refreshIncidents, setRefreshIncidents] = useState(0);

  useEffect(() => {
    if (!operator) {
      setCheckingAuth(false);
      return;
    }

    let isCurrent = true;

    fetch(`${API_BASE}/auth/me/`, {
      credentials: "include",
    })
      .then(async (response) => {
        if (!response.ok) {
          throw new Error("Session expired");
        }
        return response.json();
      })
      .then((data: { operator: OperatorSession }) => {
        if (!isCurrent) return;
        localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(data.operator));
        setOperator(data.operator);
      })
      .catch(() => {
        if (!isCurrent) return;
        localStorage.removeItem(AUTH_STORAGE_KEY);
        setOperator(null);
      })
      .finally(() => {
        if (isCurrent) {
          setCheckingAuth(false);
        }
      });

    return () => {
      isCurrent = false;
    };
  }, []);

  async function triggerDetector(
    type: DetectorType,
    videoPath: string,
  ): Promise<void> {
    setLoading(type);
    setLastResponse(null);

    try {
      const endpoint =
        type === "fire"
          ? "detect/fire/"
          : type === "flood"
          ? "detect/flood/"
          : "detect/social-distance/";

      const res = await fetch(`${API_BASE}/${endpoint}`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ video_path: videoPath }),
      });

      const data = await res.json();
      setLastResponse(data);
    } catch (err) {
      console.error(err);
      setLastResponse({ error: String(err) });
    } finally {
      setLoading(null);
    }
  }

  const handleUploadComplete = () => {
    setRefreshIncidents((prev) => prev + 1);
  };

  const responseLabel = lastResponse?.error
    ? "Request failed"
    : lastResponse
    ? "Latest API response"
    : "Waiting for analysis";

  const handleLogin = async (email: string, password: string) => {
    const response = await fetch(`${API_BASE}/auth/login/`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(data.detail || "Login failed.");
    }

    localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(data.operator));
    setOperator(data.operator);
  };

  const handleLogout = () => {
    fetch(`${API_BASE}/auth/logout/`, {
      method: "POST",
      credentials: "include",
    }).catch(() => undefined);
    localStorage.removeItem(AUTH_STORAGE_KEY);
    setOperator(null);
    setLastResponse(null);
  };

  if (checkingAuth) {
    return (
      <main className="login-page">
        <div className="auth-loading">Checking operator session...</div>
      </main>
    );
  }

  if (!operator) {
    return <LoginPage onLogin={handleLogin} />;
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="brand-block">
            <span className="eyebrow">Emergency response intelligence</span>
            <h1>Resq Command Center</h1>
            <p>
              Detect incidents, estimate severity, and coordinate relief decisions from
              one operational dashboard.
            </p>
          </div>

          <div className="status-strip" aria-label="System status">
            <div className="status-item">
              <span className="status-value">3</span>
              <span className="status-label">Detectors</span>
            </div>
            <div className="status-item">
              <span className="status-value">Live</span>
              <span className="status-label">Backend</span>
            </div>
            <div className="status-item">
              <span className="status-value">REST</span>
              <span className="status-label">API mode</span>
            </div>
          </div>

          <div className="operator-bar" aria-label="Signed in operator">
            <div className="operator-chip">
              <span className="operator-avatar">{operator.name.slice(0, 1).toUpperCase()}</span>
              <span>
                <span className="operator-name">{operator.name}</span>
                <span className="operator-role">{operator.role}</span>
              </span>
            </div>
            <button type="button" className="button header-button" onClick={handleLogout}>
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="app-main">
        <section className="workspace">
          <FileUpload apiBase={API_BASE} onUploadComplete={handleUploadComplete} />

          <aside className="side-stack">
            <section className="panel compact-panel">
              <div className="section-heading">
                <span className="eyebrow">Manual detector run</span>
                <h2>Video Path Analysis</h2>
              </div>

              <div className="detector-stack">
                <DetectorCard
                  title="City Fire"
                  type="fire"
                  placeholder="C:/path/to/fire_video.mp4"
                  loading={loading === "fire"}
                  onTrigger={triggerDetector}
                />
                <DetectorCard
                  title="Flood"
                  type="flood"
                  placeholder="C:/path/to/flood_video.mp4"
                  loading={loading === "flood"}
                  onTrigger={triggerDetector}
                />
                <DetectorCard
                  title="Crowd Safety"
                  type="social-distance"
                  placeholder="C:/path/to/crowd_video.mp4"
                  loading={loading === "social-distance"}
                  onTrigger={triggerDetector}
                />
              </div>
            </section>

            <section className="panel response-panel">
              <div className="panel-header">
                <div>
                  <span className="eyebrow">Diagnostics</span>
                  <h2>{responseLabel}</h2>
                </div>
                {lastResponse && (
                  <span className={lastResponse.error ? "pill danger" : "pill success"}>
                    {lastResponse.error ? "Error" : "OK"}
                  </span>
                )}
              </div>
              <pre className="code">
                {lastResponse ? JSON.stringify(lastResponse, null, 2) : "--"}
              </pre>
            </section>
          </aside>
        </section>

        <section className="panel incidents-panel">
          <IncidentList apiBase={API_BASE} refreshKey={refreshIncidents} />
        </section>
      </main>
    </div>
  );
};

interface LoginPageProps {
  onLogin: (email: string, password: string) => Promise<void>;
}

const LoginPage: React.FC<LoginPageProps> = ({ onLogin }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    const trimmedEmail = email.trim();
    if (!trimmedEmail || !password.trim()) {
      setError("Enter your operator email and password to continue.");
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      await onLogin(trimmedEmail, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="login-page">
      <section className="login-hero" aria-labelledby="login-title">
        <div className="login-copy">
          <span className="eyebrow">Emergency response intelligence</span>
          <h1 id="login-title">Resq Command Center</h1>
          <p>
            Sign in to review disaster media, run AI detectors, and coordinate
            incident response from a focused operations dashboard.
          </p>
        </div>

        <form className="login-panel" onSubmit={handleSubmit}>
          <div className="section-heading">
            <span className="eyebrow">Operator access</span>
            <h2>Login</h2>
          </div>

          <div className="form-group">
            <label htmlFor="login-email">Email</label>
            <input
              id="login-email"
              type="email"
              autoComplete="email"
              placeholder="commander@resq.local"
              value={email}
              onChange={(event) => {
                setEmail(event.target.value);
                setError(null);
              }}
              disabled={submitting}
            />
          </div>

          <div className="form-group">
            <label htmlFor="login-password">Password</label>
            <input
              id="login-password"
              type="password"
              autoComplete="current-password"
              placeholder="Enter password"
              value={password}
              onChange={(event) => {
                setPassword(event.target.value);
                setError(null);
              }}
              disabled={submitting}
            />
          </div>

          {error && <div className="alert error-message">{error}</div>}

          <button type="submit" className="button primary" disabled={submitting}>
            {submitting ? "Signing in" : "Sign In"}
          </button>
        </form>
      </section>
    </main>
  );
};
