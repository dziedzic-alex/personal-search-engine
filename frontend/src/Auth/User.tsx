type UserPlan = "free" | "basic" | "pro" | "ultra";

interface User {
  id: number;
  firstName: string;
  email: string;
  plan: UserPlan;
}

export type { User };
