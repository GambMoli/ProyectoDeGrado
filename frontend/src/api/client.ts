import type { ChatRequest, ChatResponse, ConversationDetail, ConversationSummary } from "../types/api";

const baseUrl = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") ??
  "http://localhost:8000/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, init);
  if (!response.ok) {
    const fallbackMessage = `La solicitud fallo con estado ${response.status}.`;
    try {
      const data = (await response.json()) as { detail?: string };
      throw new Error(data.detail ?? fallbackMessage);
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error(fallbackMessage);
    }
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

export function uploadExerciseImage(payload: {
  file: File;
  userId: string;
  conversationId?: string | null;
  prompt?: string;
}): Promise<ChatResponse> {
  const formData = new FormData();
  formData.append("file", payload.file);
  formData.append("user_id", payload.userId);
  if (payload.conversationId) {
    formData.append("conversation_id", payload.conversationId);
  }
  if (payload.prompt?.trim()) {
    formData.append("prompt", payload.prompt.trim());
  }

  return request<ChatResponse>("/upload-exercise-image", {
    method: "POST",
    body: formData,
  });
}

export function getConversations(userId: string): Promise<ConversationSummary[]> {
  return request<ConversationSummary[]>(`/conversations?user_id=${encodeURIComponent(userId)}`);
}

export function getConversation(conversationId: string, userId: string): Promise<ConversationDetail> {
  return request<ConversationDetail>(
    `/conversations/${conversationId}?user_id=${encodeURIComponent(userId)}`
  );
}
