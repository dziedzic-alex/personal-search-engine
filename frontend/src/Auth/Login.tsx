import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import Button from "../Ui/Button";
import Card from "../Ui/Card";
import FormField from "../Ui/FormField/FormField";
import Stack from "../Ui/Layout/Stack";
import TextInput from "../Ui/TextInput/TextInput";
import Body from "../Ui/Typography/Body";
import Header from "../Ui/Typography/Header";

import { useAuth } from "./AuthContext";

import "./AuthForm.css";

function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const { login } = useAuth();

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
        setError("Failed to login. Please try again.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="auth-form-container">
      <Card className="auth-form-card">
        <Header>Login</Header>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (!e.currentTarget.reportValidity()) return;
            void handleLogin();
          }}
        >
          <Stack>
            <FormField label="Email">
              <TextInput
                name="email"
                type="email"
                required
                autoComplete="email"
                placeholder="Email"
                value={email}
                onChange={setEmail}
              />
            </FormField>
            <FormField label="Password">
              <TextInput
                name="password"
                type="password"
                required
                autoComplete="current-password"
                placeholder="Password"
                value={password}
                onChange={setPassword}
              />
            </FormField>
            {error && <Body variant="error">{error}</Body>}
            <Button
              type="submit"
              isLoading={isSubmitting}
              loadingText="Logging in..."
              isDisabled={isSubmitting}
            >
              Login
            </Button>
            <div className="auth-form-footer">
              <Body>
                Don't have an account? <Link to="/signup">Sign up</Link>
              </Body>
            </div>
          </Stack>
        </form>
      </Card>
    </div>
  );
}

export default Login;
