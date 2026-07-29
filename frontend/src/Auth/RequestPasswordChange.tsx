import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import Button from "../Ui/Buttons/Button";
import Card from "../Ui/Card/Card";
import FormField from "../Ui/FormField/FormField";
import Stack from "../Ui/Layout/Stack";
import TextInput from "../Ui/TextInput/TextInput";
import Body from "../Ui/Typography/Body";
import Header from "../Ui/Typography/Header";


import { formatSecondsAsTimer } from "./AuthUtils";

const RESEND_COOLDOWN_SECONDS = 59;

function RequestPasswordChange() {
  const [inputEmail, setInputEmail] = useState<string>("");
  const [lastSentEmail, setLastSentEmail] = useState<string | null>(null);
  const [isSendingPasswordChangeEmail, setIsSendingPasswordChangeEmail] =
    useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [cooldownSeconds, setCooldownSeconds] = useState<number>(0);

  useEffect(() => {
    if (cooldownSeconds <= 0) {
      return;
    }

    const timer = setTimeout(() => {
      setCooldownSeconds((seconds) => seconds - 1);
    }, 1000);

    return () => {
      clearTimeout(timer);
    };
  }, [cooldownSeconds]);

  const handleRequestPasswordChange = async () => {
    setIsSendingPasswordChangeEmail(true);
    setError(null);

    try {
      const response = await fetch("/api/auth/request-password-change", {
        method: "POST",
        body: JSON.stringify({ email: inputEmail }),
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (response.status === 422) {
        throw new Error("Input must be a valid email address.");
      } else if (!response.ok) {
        throw new Error(
          "Failed to send password change email. Please try again.",
        );
      }

      setCooldownSeconds(RESEND_COOLDOWN_SECONDS);
      setLastSentEmail(inputEmail);
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Failed to send password change email. Please try again.",
      );
    } finally {
      setIsSendingPasswordChangeEmail(false);
    }
  };

  let resendButtonLabel = "Send password change email";
  if (cooldownSeconds > 0) {
    resendButtonLabel = `Resend in ${formatSecondsAsTimer(cooldownSeconds)}`;
  } else if (lastSentEmail) {
    resendButtonLabel = "Resend password change email";
  }

  return (
    <div className="auth-form-container">
      <Card className="auth-form-card">
        <Header>Request password change</Header>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (!e.currentTarget.reportValidity()) return;
            void handleRequestPasswordChange();
          }}
        >
          <Stack>
            {lastSentEmail ? (
              <Body>
                We sent a password change link to{" "}
                <strong>{lastSentEmail}</strong>. Check your inbox and click the
                link to reset your password. Didn&apos;t get it? You can resend
                below.
              </Body>
            ) : (
              <Body>
                Enter your email address below and we&apos;ll send you a link to
                reset your password.
              </Body>
            )}
            <FormField label="Email">
              <TextInput
                name="email"
                type="email"
                required
                autoComplete="email"
                placeholder="Email"
                value={inputEmail}
                onChange={setInputEmail}
              />
            </FormField>
            {error && <Body variant="error">{error}</Body>}
            <Button
              type="submit"
              isDisabled={isSendingPasswordChangeEmail || cooldownSeconds > 0}
              isLoading={isSendingPasswordChangeEmail}
              loadingText="Sending..."
            >
              {resendButtonLabel}
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

export default RequestPasswordChange;
