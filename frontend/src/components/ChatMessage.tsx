import type { Message } from "../types/api";
import { BotAvatarIcon, UserAvatarIcon } from "./Icons";

interface ChatMessageProps {
  message: Message;
}

function renderParagraphs(content: string) {
  return content
    .split(/\n{2,}|\n/)
    .map((paragraph) => paragraph.trim())
    .filter(Boolean)
    .map((paragraph, index) => <p key={`${paragraph}-${index}`}>{paragraph}</p>);
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isAssistantLike = message.role !== "user";
  const bubbleTone = isAssistantLike ? "assistant" : "user";
  const exercise = isAssistantLike ? message.exercise : null;
  const resolution = exercise?.resolution ?? null;
  const shouldShowBody =
    !isAssistantLike || !resolution || message.content.trim().length < 180;

  return (
    <article className={`chat-message chat-message--${bubbleTone}`}>
      <div className="chat-message__avatar" aria-hidden="true">
        {isAssistantLike ? (
          <BotAvatarIcon className="chat-message__avatar-icon" />
        ) : (
          <UserAvatarIcon className="chat-message__avatar-icon" />
        )}
      </div>

      <div className="chat-message__stack">
        {shouldShowBody ? (
          <div className={`chat-bubble chat-bubble--${bubbleTone}`}>
            <div className="chat-bubble__content">{renderParagraphs(message.content)}</div>
          </div>
        ) : null}

        {resolution ? (
          <section className="solution-card">
            <h3>Resolucion Paso a Paso:</h3>

            <ol className="solution-card__steps">
              {resolution.steps.map((step, index) => (
                <li key={`${step}-${index}`}>{step}</li>
              ))}
            </ol>

            <div className="solution-card__formula">
              <strong>{exercise?.extracted_expression ?? "Resultado"}</strong>
              <span>{resolution.final_result}</span>
            </div>

            <div className="solution-card__explanation">
              {renderParagraphs(resolution.explanation)}
            </div>

            {exercise?.error_message ? (
              <p className="solution-card__error">{exercise.error_message}</p>
            ) : null}
          </section>
        ) : null}
      </div>
    </article>
  );
}
