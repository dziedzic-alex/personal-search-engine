export function formatSecondsAsTimer(seconds: number): string {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${String(minutes)}:${String(remainingSeconds).padStart(2, "0")}`;
}

export function validatePassword(
  password: string,
  confirmPassword: string,
): string | null {
  if (password.includes(" ")) {
    return "Password cannot contain spaces";
  }

  if (password !== confirmPassword) {
    return "Passwords do not match";
  }

  return null;
}
