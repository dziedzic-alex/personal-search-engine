import { useState } from "react";
import "./Login.css";
import { useAuth } from "./AuthContext.tsx";
import { Link, Navigate, useNavigate } from "react-router-dom";

function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const { user, login } = useAuth();

  if (user) {
    return <Navigate to="/" replace />;
  }

  const handleLogin = async () => {
    setIsSubmitting(true);
    setError(null);

    try {
      await login(email, password);
      void navigate("/", { replace: true });
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError(
          "Failed to login (You might be stupid, or the server is down)",
        );
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="login">
      <h1>Login</h1>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (!e.currentTarget.reportValidity()) return;
          void handleLogin();
        }}
      >
        <input
          name="email"
          type="email"
          required
          autoComplete="email"
          placeholder="Email"
          value={email}
          onChange={(e) => {
            setEmail(e.target.value);
          }}
        />
        <input
          name="password"
          type="password"
          required
          autoComplete="current-password"
          placeholder="Password"
          value={password}
          onChange={(e) => {
            setPassword(e.target.value);
          }}
        />
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Logging in..." : "Login"}
        </button>
      </form>
      <p>
        Don't have an account? <Link to="/signup">Sign up</Link>
      </p>
      {error && <p>{error}</p>}
    </div>
  );
}

export default Login;
