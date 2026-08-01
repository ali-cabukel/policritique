import { clearToken, getToken } from "./auth-storage";
import type {
  Constituency,
  Election,
  ElectionResult,
  Manifesto,
  ManifestoDetail,
  Member,
  MemberDetail,
  Paginated,
  Party,
  TokenResponse,
  User,
} from "./types";
import { ApiError } from "./types";

const API_BASE = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";
const API_PREFIX = "/api";

async function parseError(response: Response): Promise<string> {
  try {
    const data = await response.json();
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail)) {
      return data.detail.map((item: { msg?: string }) => item.msg ?? "Error").join(", ");
    }
    return response.statusText || "Request failed";
  } catch {
    return response.statusText || "Request failed";
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  authenticated = true,
): Promise<T> {
  const headers = new Headers(options.headers);

  if (authenticated) {
    const token = getToken();
    if (!token) {
      throw new ApiError("Not authenticated", 401);
    }
    headers.set("Authorization", `Bearer ${token}`);
  }

  if (
    options.body &&
    !(options.body instanceof FormData) &&
    !(options.body instanceof URLSearchParams) &&
    !headers.has("Content-Type")
  ) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE}${API_PREFIX}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    if (response.status === 401 && authenticated) {
      clearToken();
    }
    throw new ApiError(await parseError(response), response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  const body = new URLSearchParams({ username: email, password });
  return request<TokenResponse>("/auth/jwt/login", { method: "POST", body }, false);
}

export async function register(email: string, password: string): Promise<User> {
  return request<User>(
    "/auth/register",
    { method: "POST", body: JSON.stringify({ email, password }) },
    false,
  );
}

export async function getCurrentUser(): Promise<User> {
  return request<User>("/users/me");
}

export async function listParties(limit = 50, offset = 0): Promise<Paginated<Party>> {
  return request<Paginated<Party>>(`/parties?limit=${limit}&offset=${offset}`);
}

export async function listElections(limit = 50, offset = 0): Promise<Paginated<Election>> {
  return request<Paginated<Election>>(`/elections?limit=${limit}&offset=${offset}`);
}

export async function listElectionResults(
  electionId: number,
  limit = 100,
  offset = 0,
): Promise<Paginated<ElectionResult>> {
  return request<Paginated<ElectionResult>>(
    `/elections/${electionId}/results?limit=${limit}&offset=${offset}`,
  );
}

export async function listConstituencies(
  params: { limit?: number; offset?: number; name?: string } = {},
): Promise<Paginated<Constituency>> {
  const search = new URLSearchParams();
  if (params.limit) search.set("limit", String(params.limit));
  if (params.offset) search.set("offset", String(params.offset));
  if (params.name) search.set("name", params.name);
  const query = search.toString();
  return request<Paginated<Constituency>>(`/constituencies${query ? `?${query}` : ""}`);
}

export async function listMembers(
  params: { limit?: number; offset?: number; current_only?: boolean } = {},
): Promise<Paginated<Member>> {
  const search = new URLSearchParams();
  if (params.limit) search.set("limit", String(params.limit));
  if (params.offset) search.set("offset", String(params.offset));
  if (params.current_only) search.set("current_only", "true");
  const query = search.toString();
  return request<Paginated<Member>>(`/members${query ? `?${query}` : ""}`);
}

export async function getMember(memberId: number): Promise<MemberDetail> {
  return request<MemberDetail>(`/members/${memberId}`);
}

export async function listManifestos(
  params: { limit?: number; offset?: number; party_id?: number; election_id?: number } = {},
): Promise<Paginated<Manifesto>> {
  const search = new URLSearchParams();
  if (params.limit) search.set("limit", String(params.limit));
  if (params.offset) search.set("offset", String(params.offset));
  if (params.party_id) search.set("party_id", String(params.party_id));
  if (params.election_id) search.set("election_id", String(params.election_id));
  const query = search.toString();
  return request<Paginated<Manifesto>>(`/manifestos${query ? `?${query}` : ""}`);
}

export async function getManifesto(manifestoId: number): Promise<ManifestoDetail> {
  return request<ManifestoDetail>(`/manifestos/${manifestoId}`);
}
