import { useState } from "react";
import { Link, useNavigate, Navigate } from "react-router-dom";

import "./Signup.css";
import { useAuth } from "./AuthContext";

function Signup() {
  const { user, signup } = useAuth();
  const navigate = useNavigate();

  const [firstName, setFirstName] = useState<string>("");
  const [lastName, setLastName] = useState<string>("");
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [confirmPassword, setConfirmPassword] = useState<string>("");

  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const [error, setError] = useState<string | null>(null);

  if (user) {
    return <Navigate to="/" replace />;
  }

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setError(null);

    try {
      await signup(firstName, lastName, email, password);
      void navigate("/", { replace: true });
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Failed to signup (You might be stupid, or the server is down)",
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const customValidation = (): boolean => {
    if (password.includes(" ")) {
      setError("Password cannot contain spaces");
      return false;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return false;
    }

    if (firstName.includes(" ")) {
      setError("First name cannot contain spaces");
      return false;
    }

    if (lastName.includes(" ")) {
      setError("Last name cannot contain spaces");
      return false;
    }

    return true;
  };

  return (
    <div className="signup">
      <h1>Signup</h1>
      <form
        onSubmit={(e) => {
          e.preventDefault();

          if (!e.currentTarget.reportValidity()) return;
          if (!customValidation()) return;

          void handleSubmit();
        }}
      >
        <input
          name="first-name"
          type="text"
          required
          autoComplete="given-name"
          placeholder="First Name"
          value={firstName}
          onChange={(e) => {
            setFirstName(e.target.value);
          }}
        />
        <input
          name="last-name"
          type="text"
          required
          autoComplete="family-name"
          placeholder="Last Name"
          value={lastName}
          onChange={(e) => {
            setLastName(e.target.value);
          }}
        />
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
          autoComplete="new-password"
          minLength={8}
          placeholder="Password"
          value={password}
          onChange={(e) => {
            setPassword(e.target.value);
          }}
        />
        <input
          name="confirm-password"
          type="password"
          required
          autoComplete="new-password"
          placeholder="Confirm Password"
          value={confirmPassword}
          onChange={(e) => {
            setConfirmPassword(e.target.value);
          }}
        />
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Signing up..." : "Signup"}
        </button>
      </form>
      <p>
        Already have an account? <Link to="/login">Login</Link>
      </p>
      {error && <p>{error}</p>}
    </div>
  );
}

export default Signup;
