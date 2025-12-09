import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

const containerStyle: React.CSSProperties = {
  height: "100vh",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  background: "linear-gradient(135deg, #0f172a, #2563eb)",
};

const cardStyle: React.CSSProperties = {
  width: 360,
  padding: "2rem",
  borderRadius: 16,
  background: "#fff",
  boxShadow: "0 25px 50px -12px rgba(15, 23, 42, 0.6)",
};

const LoginPage = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setIsLoading(true);
    setError(null);
    try {
      await login(username, password);
      navigate("/");
    } catch (err) {
      console.error(err);
      setError("Invalid credentials");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={containerStyle}>
      <form onSubmit={handleSubmit} style={cardStyle}>
        <h1 style={{ marginTop: 0, textAlign: "center" }}>Cold Chain Monitoring</h1>
        <p style={{ textAlign: "center", marginTop: 0, color: "#64748b" }}>
          Monitor vaccine refrigerators in real time
        </p>
        <label htmlFor="username">Username</label>
        <input
          id="username"
          type="text"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          style={{ width: "100%", marginBottom: "1rem", padding: "0.5rem" }}
          required
        />
        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          style={{ width: "100%", marginBottom: "1rem", padding: "0.5rem" }}
          required
        />
        {error && <p style={{ color: "#ef4444" }}>{error}</p>}
        <button
          type="submit"
          disabled={isLoading}
          style={{
            width: "100%",
            padding: "0.75rem",
            background: "#2563eb",
            color: "#fff",
            border: "none",
            borderRadius: 8,
            cursor: "pointer",
          }}
        >
          {isLoading ? "Signing in..." : "Login"}
        </button>
      </form>
    </div>
  );
};

export default LoginPage;

