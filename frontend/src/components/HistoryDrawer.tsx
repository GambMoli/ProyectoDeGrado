import { useEffect } from "react";

import type { ConversationSummary } from "../types/api";
import { CloseIcon, PlusIcon } from "./Icons";

interface HistoryDrawerProps {
  activeConversationId: string | null;
  conversations: ConversationSummary[];
  isLoading: boolean;
  isOpen: boolean;
  onClose: () => void;
  onNewConversation: () => void;
  onSelectConversation: (conversationId: string) => void;
}

export function HistoryDrawer({
  activeConversationId,
  conversations,
  isLoading,
  isOpen,
  onClose,
  onNewConversation,
  onSelectConversation,
}: HistoryDrawerProps) {
  useEffect(() => {
    if (!isOpen) {
      return undefined;
    }

    function handleEscape(event: KeyboardEvent) {
      if (event.key === "Escape") {
        onClose();
      }
    }

    window.addEventListener("keydown", handleEscape);
    return () => window.removeEventListener("keydown", handleEscape);
  }, [isOpen, onClose]);

  return (
    <div
      className={`history-drawer ${isOpen ? "is-open" : ""}`}
      aria-hidden={!isOpen}
      onClick={onClose}
    >
      <aside
        className="history-drawer__panel"
        onClick={(event) => event.stopPropagation()}
        aria-label="Historial de chats"
      >
        <div className="history-drawer__header">
          <button className="history-drawer__new" type="button" onClick={onNewConversation}>
            <PlusIcon className="history-drawer__new-icon" />
            <span>Nuevo Chat</span>
          </button>
          <button className="history-drawer__close" type="button" onClick={onClose} aria-label="Cerrar historial">
            <CloseIcon className="history-drawer__close-icon" />
          </button>
        </div>

        <div className="history-drawer__section">
          <span className="history-drawer__label">Historial</span>

          {isLoading ? <p className="history-drawer__empty">Cargando conversaciones...</p> : null}

          {!isLoading && conversations.length === 0 ? (
            <p className="history-drawer__empty">
              Tus conversaciones apareceran aqui despues del primer mensaje.
            </p>
          ) : null}

          {!isLoading && conversations.length > 0 ? (
            <div className="history-drawer__list">
              {conversations.map((conversation) => (
                <button
                  key={conversation.id}
                  className={`history-drawer__item ${
                    conversation.id === activeConversationId ? "is-active" : ""
                  }`}
                  type="button"
                  onClick={() => {
                    onSelectConversation(conversation.id);
                    onClose();
                  }}
                >
                  <span className="history-drawer__item-mark" aria-hidden="true" />
                  <span className="history-drawer__item-text">{conversation.title}</span>
                </button>
              ))}
            </div>
          ) : null}
        </div>
      </aside>
    </div>
  );
}
