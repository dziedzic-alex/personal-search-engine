import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import Button from "../Ui/Buttons/Button";
import Card from "../Ui/Card/Card";
import FormField from "../Ui/FormField/FormField";
import Stack from "../Ui/Layout/Stack";
import TextInput from "../Ui/TextInput/TextInput";
import Body from "../Ui/Typography/Body";
import Header from "../Ui/Typography/Header";

import { useAuth } from "./AuthContext";

import "./AuthForm.css";

function Signup() {
  const { signup } = useAuth();
  const navigate = useNavigate();

  const [firstName, setFirstName] = useState<string>("");
  const [lastName, setLastName] = useState<string>("");
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [confirmPassword, setConfirmPassword] = useState<string>("");

  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setError(null);

    try {
      const userEmail = await signup(firstName, lastName, email, password);
      void navigate("/verify-email", { state: userEmail });
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Failed to signup. Please try again.",
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
    <div className="auth-form-container">
      <Card className="auth-form-card">
        <Header>Sign up</Header>
        <form
          onSubmit={(e) => {
            e.preventDefault();

            if (!e.currentTarget.reportValidity()) return;
            if (!customValidation()) return;

            void handleSubmit();
          }}
        >
          <Stack>
            <FormField label="First Name">
              <TextInput
                name="first-name"
                type="text"
                required
                autoComplete="given-name"
                placeholder="First Name"
                value={firstName}
                onChange={setFirstName}
              />
            </FormField>
            <FormField label="Last Name">
              <TextInput
                name="last-name"
                type="text"
                required
                autoComplete="family-name"
                placeholder="Last Name"
                value={lastName}
                onChange={setLastName}
              />
            </FormField>
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
                autoComplete="new-password"
                minLength={8}
                placeholder="Password"
                value={password}
                onChange={setPassword}
              />
            </FormField>
            <FormField label="Confirm Password">
              <TextInput
                name="confirm-password"
                type="password"
                required
                autoComplete="new-password"
                placeholder="Confirm Password"
                value={confirmPassword}
                onChange={setConfirmPassword}
              />
            </FormField>
            {error && <Body variant="error">{error}</Body>}
            <Button
              type="submit"
              isDisabled={isSubmitting}
              isLoading={isSubmitting}
              loadingText="Signing up..."
            >
              Sign up
            </Button>
            <div className="auth-form-footer">
              <Body>
                Already have an account? <Link to="/login">Log in</Link>
              </Body>
            </div>
          </Stack>
        </form>
      </Card>
    </div>
  );
}

export default Signup;
