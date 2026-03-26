import type { ConversationSummary } from "../types/api";
import { formatTimestamp } from "../utils/formatters";

interface SidebarProps {
  conversations: ConversationSummary[];
  activeConversationId: string | null;
  isLoading: boolean;
  onSelectConversation: (conversationId: string) => void;
  onNewConversation: () => void;
}

export function Sidebar({
  conversations,
  activeConversationId,
  isLoading,
  onSelectConversation,
  onNewConversation,
}: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="sidebar__header">
        <div>
          <p className="sidebar__eyebrow">MVP Tutor de Cálculo</p>
          <h1>Tutor IA</h1>
        </div>
        <button className="button button--ghost" type="button" onClick={onNewConversation}>
          Nueva
        </button>
      </div>

      <div className="sidebar__panel">
        <div className="sidebar__panel-header">
          <h2>Historial</h2>
          {isLoading ? <span className="sidebar__hint">Actualizando...</span> : null}
        </div>

        {conversations.length === 0 ? (
          <div className="sidebar__empty">
            Tus conversaciones aparecerán aquí después del primer ejercicio resuelto.
          </div>
        ) : (
          <div className="conversation-list">
            {conversations.map((conversation) => (
              <button
                key={conversation.id}
                className={`conversation-list__item ${
                  conversation.id === activeConversationId ? "is-active" : ""
                }`}
                type="button"
                onClick={() => onSelectConversation(conversation.id)}
              >
                <span className="conversation-list__title">{conversation.title}</span>
                <span className="conversation-list__meta">
                  {conversation.summary ?? conversation.last_message_preview ?? "Sin resumen"}
                </span>
                <span className="conversation-list__footer">
                  <strong>{conversation.message_count} mensajes</strong>
                  <span>{formatTimestamp(conversation.updated_at)}</span>
                </span>
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="sidebar__footnote">
        El backend resuelve con SymPy, explica con plantillas u Ollama y deja el OCR desacoplado.
      </div>
    </aside>
  );
}
