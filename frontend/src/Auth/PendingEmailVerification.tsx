import { useEffect, useState } from "react";
import { Link, Navigate, useLocation } from "react-router-dom";

import Button from "../Ui/Buttons/Button";
import Card from "../Ui/Card/Card";
import Stack from "../Ui/Layout/Stack";
import Body from "../Ui/Typography/Body";
import Header from "../Ui/Typography/Header";

import "./AuthForm.css";

const RESEND_COOLDOWN_SECONDS = 59;

function PendingEmailVerification() {
  const location = useLocation();
  const email = location.state as string | null;

  const [verificationEmailSent, setVerificationEmailSent] = useState(false);
  const [cooldownSeconds, setCooldownSeconds] = useState(0);
  const [isSendingVerificationEmail, setIsSendingVerificationEmail] =
    useState(false);
  const [error, setError] = useState<string | null>(null);

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

  if (!email) {
    return <Navigate to="/login" replace />;
  }

  const sendVerificationEmail = async () => {
    setIsSendingVerificationEmail(true);
    setError(null);

    try {
      const response = await fetch("/api/auth/send-verification-email", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email }),
      });

      if (!response.ok) {
        throw new Error("Failed to send verification email. Please try again.");
      }

      setVerificationEmailSent(true);
      setCooldownSeconds(RESEND_COOLDOWN_SECONDS);
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Failed to send verification email. Please try again.",
      );
    } finally {
      setIsSendingVerificationEmail(false);
    }
  };

  let resendButtonLabel = "Send verification email";
  if (cooldownSeconds > 0) {
    resendButtonLabel = `Resend in 0:${String(cooldownSeconds).padStart(2, "0")}`;
  } else if (verificationEmailSent) {
    resendButtonLabel = "Resend verification email";
  }

  return (
    <div className="auth-form-container">
      <Card className="auth-form-card">
        <Header>Verify your email</Header>
        <Stack>
          {verificationEmailSent ? (
            <Body>
              We sent a verification link to <strong>{email}</strong>. Check
              your inbox and click the link to finish signing up. Didn&apos;t
              get it? You can resend below.
            </Body>
          ) : (
            <Body>
              To finish signing up, verify <strong>{email}</strong>. We&apos;ll
              email you a link to confirm your address.
            </Body>
          )}
          {error && <Body variant="error">{error}</Body>}
          <Button
            onClick={() => void sendVerificationEmail()}
            isDisabled={isSendingVerificationEmail || cooldownSeconds > 0}
            isLoading={isSendingVerificationEmail}
            loadingText="Sending..."
          >
            {resendButtonLabel}
          </Button>
          <div className="auth-form-footer">
            <Body>
              Wrong account? <Link to="/login">Back to login</Link>
            </Body>
          </div>
        </Stack>
      </Card>
    </div>
  );
}

export default PendingEmailVerification;
