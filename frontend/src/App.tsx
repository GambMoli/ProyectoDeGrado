import { useEffect, useState } from "react";

import { getConversation, getConversations, sendChatMessage, uploadExerciseImage } from "./api/client";
import { ChatMessage } from "./components/ChatMessage";
import { Composer } from "./components/Composer";
import { Sidebar } from "./components/Sidebar";
import { StatusBanner } from "./components/StatusBanner";
import type { ConversationDetail, ConversationSummary } from "./types/api";

const USER_STORAGE_KEY = "calc-tutor-user-id";
const CONVERSATION_STORAGE_KEY = "calc-tutor-conversation-id";

function createUserId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `student-${Math.random().toString(36).slice(2, 10)}`;
}

export default function App() {
  const [userId] = useState<string>(() => localStorage.getItem(USER_STORAGE_KEY) ?? createUserId());
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(
    () => localStorage.getItem(CONVERSATION_STORAGE_KEY)
  );
  const [activeConversation, setActiveConversation] = useState<ConversationDetail | null>(null);
  const [isHistoryLoading, setIsHistoryLoading] = useState(false);
  const [isConversationLoading, setIsConversationLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    localStorage.setItem(USER_STORAGE_KEY, userId);
  }, [userId]);

  useEffect(() => {
    if (activeConversationId) {
      localStorage.setItem(CONVERSATION_STORAGE_KEY, activeConversationId);
      return;
    }
    localStorage.removeItem(CONVERSATION_STORAGE_KEY);
  }, [activeConversationId]);

  useEffect(() => {
    void refreshConversations();
  }, []);

  useEffect(() => {
    if (!activeConversationId) {
      setActiveConversation(null);
      return;
    }
    void loadConversation(activeConversationId);
  }, [activeConversationId]);

  async function refreshConversations(preferredConversationId?: string) {
    setIsHistoryLoading(true);
    try {
      const items = await getConversations(userId);
      setConversations(items);

      if (preferredConversationId) {
        setActiveConversationId(preferredConversationId);
      } else if (items.length > 0 && !activeConversationId) {
        setActiveConversationId(items[0].id);
      } else if (
        activeConversationId &&
        !items.some((conversation) => conversation.id === activeConversationId)
      ) {
        setActiveConversationId(items[0]?.id ?? null);
      }
    } catch (nextError) {
      const message =
        nextError instanceof Error ? nextError.message : "No se pudo cargar el historial.";
      setError(message);
    } finally {
      setIsHistoryLoading(false);
    }
  }

  async function loadConversation(conversationId: string) {
    setIsConversationLoading(true);
    try {
      const detail = await getConversation(conversationId, userId);
      setActiveConversation(detail);
    } catch (nextError) {
      const message =
        nextError instanceof Error ? nextError.message : "No se pudo cargar la conversación.";
      setError(message);
    } finally {
      setIsConversationLoading(false);
    }
  }

  async function handleComposerSubmit(payload: { message: string; file: File | null }) {
    setError(null);
    setIsSubmitting(true);

    try {
      const response = payload.file
        ? await uploadExerciseImage({
            file: payload.file,
            userId,
            conversationId: activeConversationId,
            prompt: payload.message,
          })
        : await sendChatMessage({
            user_id: userId,
            conversation_id: activeConversationId,
            message: payload.message,
          });

      await loadConversation(response.conversation_id);
      await refreshConversations(response.conversation_id);
    } catch (nextError) {
      const message =
        nextError instanceof Error ? nextError.message : "No se pudo enviar el mensaje.";
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  }

  function handleNewConversation() {
    setError(null);
    setActiveConversationId(null);
    setActiveConversation(null);
  }

  return (
    <div className="app-shell">
      <Sidebar
        conversations={conversations}
        activeConversationId={activeConversationId}
        isLoading={isHistoryLoading}
        onSelectConversation={(conversationId) => {
          setError(null);
          setActiveConversationId(conversationId);
        }}
        onNewConversation={handleNewConversation}
      />

      <main className="workspace">
        <header className="workspace__header">
          <div>
            <p className="workspace__eyebrow">Asistente pedagógico</p>
            <h2>Resuelve cálculo paso a paso con texto o imagen</h2>
          </div>
          <div className="workspace__badge-group">
            <span className="workspace__badge">FastAPI + SymPy</span>
            <span className="workspace__badge">Ollama opcional</span>
            <span className="workspace__badge">OCR desacoplado</span>
          </div>
        </header>

        {error ? <StatusBanner tone="error" message={error} /> : null}

        <section className="workspace__chat">
          {isConversationLoading ? (
            <div className="workspace__empty">Cargando conversación...</div>
          ) : activeConversation && activeConversation.messages.length > 0 ? (
            <div className="message-list">
              {activeConversation.messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
            </div>
          ) : (
            <div className="workspace__empty workspace__empty--hero">
              <p className="workspace__empty-title">Empieza con una duda real de cálculo</p>
              <p>
                Ejemplos: <strong>derivada de x^3</strong>, <strong>integral de x^2 dx</strong> o
                una foto del ejercicio.
              </p>
            </div>
          )}
        </section>

        <Composer disabled={isSubmitting} onSubmit={handleComposerSubmit} />
      </main>
    </div>
  );
}
