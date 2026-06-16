let getAccessToken: () => string | null = () => null;
let refreshAccessToken: () => Promise<void> = () => Promise.resolve();
let clearSession: () => void = () => null;
let navigateToLogin: () => void = () => null;

export function configureApiClient(config: {
  getAccessToken: () => string | null;
  refreshAccessToken: () => Promise<void>;
  clearSession: () => void;
  navigateToLogin: () => void;
}) {
  getAccessToken = config.getAccessToken;
  refreshAccessToken = config.refreshAccessToken;
  clearSession = config.clearSession;
  navigateToLogin = config.navigateToLogin;
}

export async function apiFetch(
  path: string,
  options: RequestInit = {},
): Promise<Response> {
  const headers = new Headers(options.headers);

  let accessToken = getAccessToken();
  if (accessToken) {
    headers.set("Authorization", `Bearer ${accessToken}`);
  }
  options.headers = headers;

  try {
    let response: Response = await fetch(path, options);

    if (response.status !== 401 && response.status !== 403) {
      return response;
    }

    await refreshAccessToken();
    accessToken = getAccessToken();
    if (accessToken) {
      headers.set("Authorization", `Bearer ${accessToken}`);
    }

    response = await fetch(path, options);
    if (response.status === 401 || response.status === 403) {
      clearSession();
      navigateToLogin();
      throw new Error("Unauthorized");
    }

    return response;
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error("Request failed", { cause: error });
  }
}
