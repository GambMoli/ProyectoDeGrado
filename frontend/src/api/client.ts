import type {
  AuthResponse,
  AuthUser,
  ChatRequest,
  ChatResponse,
  ConversationDetail,
  ConversationSummary,
  LoginPayload,
  OcrResponse,
  ReportsOverview,
  RegisterPayload,
  StudentReportListItem,
  StudentReportSummary,
  StudentWeeklyActivity,
  TopicReportSummary,
  TopicTrend,
} from "../types/api";

const baseUrl = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") ??
  "http://localhost:8000/api";
const AUTH_TOKEN_STORAGE_KEY = "calc-tutor-auth-token";
const AUTH_USER_STORAGE_KEY = "calc-tutor-auth-user";

function formatErrorDetail(detail: unknown): string | null {
  if (!detail) {
    return null;
  }

  if (typeof detail === "string") {
    const cleaned = detail.trim();
    return cleaned || null;
  }

  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => formatErrorDetail(item))
      .filter((item): item is string => Boolean(item));
    if (!messages.length) {
      return null;
    }
    return Array.from(new Set(messages)).join(" ");
  }

  if (typeof detail === "object") {
    const maybeValidation = detail as {
      msg?: unknown;
      loc?: unknown;
      detail?: unknown;
      error?: unknown;
      message?: unknown;
    };

    if (typeof maybeValidation.msg === "string") {
      const location = Array.isArray(maybeValidation.loc)
        ? maybeValidation.loc
            .filter((part) => typeof part === "string" || typeof part === "number")
            .join(".")
        : "";
      return location ? `${location}: ${maybeValidation.msg}` : maybeValidation.msg;
    }

    return (
      formatErrorDetail(maybeValidation.detail) ??
      formatErrorDetail(maybeValidation.error) ??
      formatErrorDetail(maybeValidation.message)
    );
  }

  return null;
}

function getAuthHeaders(init?: HeadersInit): Headers {
  const headers = new Headers(init);
  const token = localStorage.getItem(AUTH_TOKEN_STORAGE_KEY);
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  return headers;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, {
    ...init,
    headers: getAuthHeaders(init?.headers),
  });
  if (!response.ok) {
    const fallbackMessage = `La solicitud fallo con estado ${response.status}.`;
    try {
      const data = (await response.json()) as { detail?: unknown; error?: unknown; message?: unknown };
      const message =
        formatErrorDetail(data.detail) ??
        formatErrorDetail(data.error) ??
        formatErrorDetail(data.message) ??
        fallbackMessage;
      throw new Error(message);
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error(fallbackMessage);
    }
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

export function sendChatMessage(payload: ChatRequest): Promise<ChatResponse> {
  return request<ChatResponse>("/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

export function extractImageText(files: File[]): Promise<OcrResponse> {
  const formData = new FormData();
  for (const file of files) {
    formData.append("files", file);
  }
  return request<OcrResponse>("/upload-exercise-image", {
    method: "POST",
    body: formData,
  });
}

export function getConversations(): Promise<ConversationSummary[]> {
  return request<ConversationSummary[]>("/conversations");
}

export function getConversation(conversationId: string): Promise<ConversationDetail> {
  return request<ConversationDetail>(`/conversations/${conversationId}`);
}

export function registerRequest(payload: RegisterPayload): Promise<AuthResponse> {
  return request<AuthResponse>("/auth/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

export function loginRequest(payload: LoginPayload): Promise<AuthResponse> {
  return request<AuthResponse>("/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

export function getCurrentUser(): Promise<AuthUser> {
  return request<AuthUser>("/auth/me");
}

export function logoutRequest(): Promise<void> {
  return request<void>("/auth/logout", {
    method: "POST",
  });
}

export function storeAuth(response: AuthResponse): void {
  localStorage.setItem(AUTH_TOKEN_STORAGE_KEY, response.access_token);
  localStorage.setItem(AUTH_USER_STORAGE_KEY, JSON.stringify(response.user));
}

export function clearStoredAuth(): void {
  localStorage.removeItem(AUTH_TOKEN_STORAGE_KEY);
  localStorage.removeItem(AUTH_USER_STORAGE_KEY);
}

export function getStoredAuthToken(): string | null {
  return localStorage.getItem(AUTH_TOKEN_STORAGE_KEY);
}

function buildQuery(params: Record<string, string | undefined>): string {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value && value.trim()) {
      query.set(key, value);
    }
  });
  const text = query.toString();
  return text ? `?${text}` : "";
}

export function getReportsOverview(params: {
  start: string;
  end: string;
}): Promise<ReportsOverview> {
  return request<ReportsOverview>(`/reports/overview${buildQuery(params)}`);
}

export function getReportStudents(params: {
  start: string;
  end: string;
  search?: string;
}): Promise<StudentReportListItem[]> {
  return request<StudentReportListItem[]>(`/reports/students${buildQuery(params)}`);
}

export function getStudentReportSummary(params: {
  userId: string;
  start: string;
  end: string;
}): Promise<StudentReportSummary> {
  return request<StudentReportSummary>(
    `/reports/students/${params.userId}/summary${buildQuery({ start: params.start, end: params.end })}`
  );
}

export function getStudentWeeklyActivity(params: {
  userId: string;
  start: string;
  end: string;
}): Promise<StudentWeeklyActivity> {
  return request<StudentWeeklyActivity>(
    `/reports/students/${params.userId}/weekly-activity${buildQuery({ start: params.start, end: params.end })}`
  );
}

export function getTopicReportSummaries(params: {
  start: string;
  end: string;
}): Promise<TopicReportSummary[]> {
  return request<TopicReportSummary[]>(`/reports/topics/summary${buildQuery(params)}`);
}

export function getTopicTrend(params: {
  topic: string;
  start: string;
  end: string;
  days?: number;
}): Promise<TopicTrend> {
  return request<TopicTrend>(
    `/reports/topics/${params.topic}/trend${buildQuery({
      start: params.start,
      end: params.end,
      days: params.days ? String(params.days) : undefined,
    })}`
  );
}
