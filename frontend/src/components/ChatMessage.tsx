import type { Message } from "../types/api";
import { BotAvatarIcon, UserAvatarIcon } from "./Icons";
import { MathContent, MathFormula } from "./MathContent";

interface ChatMessageProps {
  message: Message;
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
            <div className="chat-bubble__content">
              <MathContent content={message.content} />
            </div>
          </div>
        ) : null}

        {resolution ? (
          <section className="solution-card">
            <h3>Resolucion Paso a Paso:</h3>

            <ol className="solution-card__steps">
              {resolution.steps.map((step, index) => (
                <li key={`${step}-${index}`}>
                  <MathContent content={step} />
                </li>
              ))}
            </ol>

            <div className="solution-card__formula">
              <span className="solution-card__formula-label">Expresion interpretada</span>
              {exercise?.extracted_expression ? (
                <MathFormula
                  expression={exercise.extracted_expression}
                  displayMode
                  source="plain"
                  className="solution-card__formula-render"
                />
              ) : null}
              <span className="solution-card__formula-label">Resultado</span>
              <MathFormula
                expression={resolution.final_result}
                displayMode
                source="plain"
                className="solution-card__formula-render"
              />
            </div>

            <div className="solution-card__explanation">
              <MathContent content={resolution.explanation} />
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
