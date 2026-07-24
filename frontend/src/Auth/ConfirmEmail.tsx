import { Navigate, useNavigate, useSearchParams } from "react-router-dom";
import { useEffect, useRef } from "react";
import LoadingPage from "../Ui/LoadingPage/LoadingPage";
import { useAuth } from "./AuthContext";
import { notify } from "../Ui/Notification/notify";

function ConfirmEmail() {
  const { verifyEmail } = useAuth();
  const navigate = useNavigate();
  const [queryParams] = useSearchParams();
  const token = queryParams.get("token");
  const userId = queryParams.get("user_id");
  const verifyInProgress = useRef(false);

  useEffect(() => {
    if (!token || !userId || verifyInProgress.current) {
      return;
    }

    const verify = async () => {
      try {
        await verifyEmail(token, userId);
        notify({
          message: "Email verified successfully",
          variant: "success",
        });
      } catch (error) {
        notify({
          message:
            error instanceof Error
              ? error.message
              : "Failed to verify email. Please login to try again.",
          variant: "error",
          durationMs: 10000,
        });
        void navigate("/login", { replace: true });
      }
    };

    verifyInProgress.current = true;
    void verify();
  }, [token, userId, verifyEmail, navigate]);

  if (!token || !userId) {
    return <Navigate to="/login" replace />;
  }

  return <LoadingPage />;
}

export default ConfirmEmail;
