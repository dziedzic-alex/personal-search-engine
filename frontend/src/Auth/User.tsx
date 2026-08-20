type UserPlan = "free" | "basic" | "pro" | "ultra";

interface User {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  plan: UserPlan;
}

export type { User, UserPlan };
