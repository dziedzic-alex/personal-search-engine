import { useState } from "react";
import Card from "../Ui/Card/Card";
import FormField from "../Ui/FormField/FormField";
import Stack from "../Ui/Layout/Stack";
import TextInput from "../Ui/TextInput/TextInput";
import Header from "../Ui/Typography/Header";
import Button from "../Ui/Buttons/Button";
import { Link, Navigate, useNavigate, useSearchParams } from "react-router-dom";
import Body from "../Ui/Typography/Body";
import { notify } from "../Ui/Notification/notify";
import { validatePassword } from "./AuthUtils";

function ResetPassword() {
  const navigate = useNavigate();
  const [queryParams] = useSearchParams();
  const token = queryParams.get("token");
  const userId = queryParams.get("user_id");

  const [password, setPassword] = useState<string>("");
  const [confirmPassword, setConfirmPassword] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  if (!token || !userId) {
    return <Navigate to="/login" replace />;
  }

  const handleReset = async () => {
    setIsSubmitting(true);
    setError(null);

    try {
      const response = await fetch("/api/auth/reset-password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ token, userId, newPassword: password }),
      });

      if (response.status === 400) {
        throw new Error(
          "Invalid or expired URL. Please request another password reset.",
        );
      } else if (response.status === 404) {
        throw new Error(
          "User associated with URL not found. Please ensure you have an account and try again.",
        );
      } else if (!response.ok) {
        throw new Error("Failed to reset password. Please try again.");
      }

      notify({
        message:
          "Password reset successfully. Please login with your new password.",
        variant: "success",
      });
      void navigate("/login", { replace: true });
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Failed to reset password. Please try again.",
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="auth-form-container">
      <Card className="auth-form-card">
        <Header>Reset Password</Header>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (!e.currentTarget.reportValidity()) return;

            const error = validatePassword(password, confirmPassword);
            if (error) {
              setError(error);
              return;
            }

            void handleReset();
          }}
        >
          <Stack>
            <FormField label="New Password">
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
            <FormField label="Confirm New Password">
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
              loadingText="Resetting..."
            >
              Reset Password
            </Button>
            <div className="auth-form-footer">
              <Body>
                Changed your mind? <Link to="/login">Back to login</Link>
              </Body>
            </div>
          </Stack>
        </form>
      </Card>
    </div>
  );
}

export default ResetPassword;
