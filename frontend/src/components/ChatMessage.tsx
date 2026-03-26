import type { Message } from "../types/api";
import { formatTimestamp, labelForExerciseStatus, labelForProblemType, labelForRole } from "../utils/formatters";

interface ChatMessageProps {
  message: Message;
}

function renderParagraphs(content: string) {
  return content.split(/\n{2,}|\n/).map((paragraph, index) => (
    <p key={`${paragraph}-${index}`}>{paragraph}</p>
  ));
}

export function ChatMessage({ message }: ChatMessageProps) {
  const exercise = message.role === "assistant" ? message.exercise : null;

  return (
    <article className={`message message--${message.role}`}>
      <div className="message__head">
        <div>
          <span className="message__role">{labelForRole(message.role)}</span>
          <span className="message__time">{formatTimestamp(message.created_at)}</span>
        </div>
        <span className={`pill pill--${message.status}`}>{message.status.split("_").join(" ")}</span>
      </div>

      <div className="message__body">{renderParagraphs(message.content)}</div>

      {exercise ? (
        <div className="exercise-panel">
          <div className="exercise-panel__grid">
            <section className="exercise-card">
              <span className="exercise-card__label">Ejercicio detectado</span>
              <h3>{exercise.extracted_expression ?? "No identificado con claridad"}</h3>
              <dl className="exercise-card__list">
                <div>
                  <dt>Tipo</dt>
                  <dd>{labelForProblemType(exercise.detected_problem_type)}</dd>
                </div>
                <div>
                  <dt>Estado</dt>
                  <dd>{labelForExerciseStatus(exercise.status)}</dd>
                </div>
                {exercise.variable ? (
                  <div>
                    <dt>Variable</dt>
                    <dd>{exercise.variable}</dd>
                  </div>
                ) : null}
                {exercise.limit_point ? (
                  <div>
                    <dt>Punto</dt>
                    <dd>{exercise.limit_point}</dd>
                  </div>
                ) : null}
              </dl>
            </section>

            <section className="exercise-card">
              <span className="exercise-card__label">Solución</span>
              <h3>{exercise.resolution?.final_result ?? "Sin resultado final"}</h3>
              {exercise.resolution ? (
                <p className="exercise-card__muted">Entrada interpretada por SymPy: {exercise.resolution.sympy_input}</p>
              ) : null}
              {exercise.ocr_text ? (
                <p className="exercise-card__muted">Texto OCR: {exercise.ocr_text}</p>
              ) : null}
            </section>
          </div>

          {exercise.resolution ? (
            <section className="exercise-card exercise-card--steps">
              <span className="exercise-card__label">Pasos base y explicación</span>
              <ol className="steps-list">
                {exercise.resolution.steps.map((step, index) => (
                  <li key={`${step}-${index}`}>{step}</li>
                ))}
              </ol>
              <div className="exercise-card__explanation">{renderParagraphs(exercise.resolution.explanation)}</div>
              <p className="exercise-card__muted">
                Fuente de explicación: {exercise.resolution.explanation_source}
              </p>
            </section>
          ) : null}

          {exercise.parse_notes.length > 0 ? (
            <div className="exercise-notes">
              {exercise.parse_notes.map((note, index) => (
                <span key={`${note}-${index}`} className="exercise-notes__item">
                  {note}
                </span>
              ))}
            </div>
          ) : null}

          {exercise.error_message ? (
            <div className="status-banner status-banner--error">{exercise.error_message}</div>
          ) : null}
        </div>
      ) : null}
    </article>
  );
}
