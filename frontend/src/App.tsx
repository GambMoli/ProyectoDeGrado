import { useEffect, useState } from "react";

import {
  getConversation,
  getConversations,
  sendChatMessage,
  uploadExerciseImage,
} from "./api/client";
import { AttachExerciseModal } from "./components/AttachExerciseModal";
import { ChatMessage } from "./components/ChatMessage";
import { Composer } from "./components/Composer";
import { HistoryDrawer } from "./components/HistoryDrawer";
import { BrandIcon, MenuIcon, UploadIcon } from "./components/Icons";
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

function WelcomeBubble() {
  return (
    <article className="chat-message chat-message--assistant">
      <div className="chat-message__avatar" aria-hidden="true">
        <BrandIcon className="chat-message__avatar-icon" />
      </div>
      <div className="chat-message__stack">
        <div className="chat-bubble chat-bubble--assistant chat-bubble--welcome">
          <p>
            ¡Hola! Soy tu asistente de <strong>Cubik IA</strong>. Estoy listo para ayudarte con
            calculos matematicos complejos, algebra, calculo o estadistica. ¿Que problema
            resolveremos hoy?
          </p>
        </div>
      </div>
    </article>
  );
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
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [isAttachModalOpen, setIsAttachModalOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
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
        nextError instanceof Error ? nextError.message : "No se pudo cargar la conversacion.";
      setError(message);
    } finally {
      setIsConversationLoading(false);
    }
  }

  async function handleComposerSubmit(message: string) {
    setError(null);
    setIsSubmitting(true);

    try {
      const response = selectedFile
        ? await uploadExerciseImage({
            file: selectedFile,
            userId,
            conversationId: activeConversationId,
            prompt: message,
          })
        : await sendChatMessage({
            user_id: userId,
            conversation_id: activeConversationId,
            message,
          });

      setSelectedFile(null);
      await loadConversation(response.conversation_id);
      await refreshConversations(response.conversation_id);
    } catch (nextError) {
      const nextMessage =
        nextError instanceof Error ? nextError.message : "No se pudo enviar el mensaje.";
      setError(nextMessage);
    } finally {
      setIsSubmitting(false);
    }
  }

  function handleNewConversation() {
    setError(null);
    setSelectedFile(null);
    setActiveConversationId(null);
    setActiveConversation(null);
    setIsHistoryOpen(false);
  }

  const hasMessages = Boolean(activeConversation && activeConversation.messages.length > 0);

  return (
    <>
      <div className="app-shell">
        <Sidebar
          onOpenAttach={() => setIsAttachModalOpen(true)}
          onOpenHistory={() => setIsHistoryOpen(true)}
        />

        <main className={`app-main ${isAttachModalOpen ? "is-dimmed" : ""}`}>
          <header className="topbar">
            <button
              className="topbar__icon-button"
              type="button"
              onClick={() => setIsHistoryOpen(true)}
              aria-label="Abrir historial"
            >
              <MenuIcon className="topbar__icon" />
            </button>

            <div className="topbar__brand">
              <BrandIcon className="topbar__brand-icon" />
              <span>Cubik IA</span>
            </div>
          </header>

          {error ? <StatusBanner tone="error" message={error} /> : null}

          <section className="chat-shell">
            <div className="chat-scroll">
              {isConversationLoading ? (
                <div className="chat-loading">Cargando conversacion...</div>
              ) : (
                <div className="chat-list">
                  {!hasMessages ? <WelcomeBubble /> : null}
                  {activeConversation?.messages.map((message) => (
                    <ChatMessage key={message.id} message={message} />
                  ))}
                </div>
              )}
            </div>

            <button
              className="chat-shell__floating-upload"
              type="button"
              onClick={() => setIsAttachModalOpen(true)}
              aria-label="Adjuntar ejercicio"
            >
              <UploadIcon className="chat-shell__floating-upload-icon" />
            </button>

            <Composer
              disabled={isSubmitting}
              selectedFile={selectedFile}
              onClearFile={() => setSelectedFile(null)}
              onOpenAttach={() => setIsAttachModalOpen(true)}
              onSubmit={handleComposerSubmit}
            />
          </section>
        </main>
      </div>

      <HistoryDrawer
        activeConversationId={activeConversationId}
        conversations={conversations}
        isLoading={isHistoryLoading}
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        onNewConversation={handleNewConversation}
        onSelectConversation={(conversationId) => {
          setError(null);
          setActiveConversationId(conversationId);
        }}
      />

      <AttachExerciseModal
        isOpen={isAttachModalOpen}
        selectedFile={selectedFile}
        onClose={() => setIsAttachModalOpen(false)}
        onSelectFile={(file) => {
          setSelectedFile(file);
          setIsAttachModalOpen(false);
        }}
      />
    </>
  );
}
