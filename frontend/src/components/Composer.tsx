import { useRef, useState } from "react";
import type { KeyboardEvent } from "react";

import { AttachmentIcon, CloseIcon, FormulaIcon, SendIcon } from "./Icons";
import { extractMathCandidateForPreview, MathFormula, plainMathToLatex } from "./MathContent";

interface ComposerProps {
  disabled: boolean;
  selectedFile: File | null;
  onClearFile: () => void;
  onOpenAttach: () => void;
  onSubmit: (message: string) => Promise<void>;
}

const formulaSnippets = [
  { label: "Integral", value: "∫ x^2 dx", preview: "\\int x^2\\,dx" },
  { label: "Por Partes", value: "∫ x e^x dx", preview: "\\int x e^x\\,dx" },
  { label: "Derivada", value: "d/dx (x^3 + 2x)", preview: "\\frac{d}{dx}(x^3 + 2x)" },
  { label: "Limite", value: "lim x->0 sin(x)/x", preview: "\\lim_{x \\to 0} \\sin(x)/x" },
  { label: "Ecuacion", value: "x^2 + 3x = 10", preview: "x^2 + 3x = 10" },
  { label: "Raiz", value: "sqrt(x^2 + 1)", preview: "\\sqrt{x^2 + 1}" },
];

export function Composer({
  disabled,
  selectedFile,
  onClearFile,
  onOpenAttach,
  onSubmit,
}: ComposerProps) {
  const [message, setMessage] = useState("");
  const [isFormulaPanelOpen, setIsFormulaPanelOpen] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  async function handleSubmit() {
    if (disabled || (!message.trim() && !selectedFile)) {
      return;
    }

    await onSubmit(message.trim());
    setMessage("");
    setIsFormulaPanelOpen(false);
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void handleSubmit();
    }
  }

  function insertFormulaTemplate(template: string) {
    const textarea = textareaRef.current;
    const selectionStart = textarea?.selectionStart ?? message.length;
    const selectionEnd = textarea?.selectionEnd ?? message.length;
    const prefix = message.slice(0, selectionStart);
    const suffix = message.slice(selectionEnd);
    const glue = prefix && !prefix.endsWith(" ") && !prefix.endsWith("\n") ? " " : "";
    const nextValue = `${prefix}${glue}${template}${suffix}`;
    const cursorPosition = (prefix + glue + template).length;
    setMessage(nextValue);
    requestAnimationFrame(() => {
      textareaRef.current?.focus();
      textareaRef.current?.setSelectionRange(cursorPosition, cursorPosition);
    });
  }

  const previewCandidate = extractMathCandidateForPreview(message);
  const previewLatex = previewCandidate ? plainMathToLatex(previewCandidate) : null;

  return (
    <div className="composer">
      <div className="composer__tools">
        <button
          className={`composer__tool ${isFormulaPanelOpen ? "is-active" : ""}`}
          type="button"
          onClick={() => setIsFormulaPanelOpen((value) => !value)}
        >
          <FormulaIcon className="composer__tool-icon" />
          <span>Insertar formula</span>
        </button>
        <button className="composer__tool" type="button" onClick={onOpenAttach}>
          <AttachmentIcon className="composer__tool-icon" />
          <span>PNG/JPEG</span>
        </button>
        <span className="composer__presence" aria-hidden="true" />
      </div>

      {isFormulaPanelOpen ? (
        <div className="composer__formula-panel">
          <div className="composer__formula-grid">
            {formulaSnippets.map((snippet) => (
              <button
                key={snippet.label}
                type="button"
                className="composer__formula-chip"
                onClick={() => insertFormulaTemplate(snippet.value)}
              >
                <span>{snippet.label}</span>
                <MathFormula
                  expression={snippet.preview}
                  displayMode
                  className="composer__formula-chip-preview"
                />
              </button>
            ))}
          </div>

          <div className="composer__formula-help">
            <p>El asistente entiende entradas como `∫ x^2 dx`, `d/dx (x^3)` o `lim x-&gt;0 sin(x)/x`.</p>
          </div>
        </div>
      ) : null}

      {selectedFile ? (
        <div className="composer__file-chip">
          <span>{selectedFile.name}</span>
          <button type="button" onClick={onClearFile} aria-label="Quitar archivo adjunto">
            <CloseIcon className="composer__file-chip-icon" />
          </button>
        </div>
      ) : null}

      {previewLatex ? (
        <div className="composer__preview-card">
          <span className="composer__preview-label">Vista previa</span>
          <MathFormula expression={previewLatex} displayMode className="composer__preview-formula" />
        </div>
      ) : null}

      <div className="composer__box">
        <textarea
          ref={textareaRef}
          className="composer__textarea"
          placeholder="Escribe tu consulta matematica aqui..."
          value={message}
          disabled={disabled}
          onChange={(event) => setMessage(event.target.value)}
          onKeyDown={handleKeyDown}
          rows={2}
        />

        <button
          className="composer__send"
          type="button"
          disabled={disabled || (!message.trim() && !selectedFile)}
          onClick={() => void handleSubmit()}
          aria-label={disabled ? "Procesando mensaje" : "Enviar mensaje"}
        >
          <SendIcon className="composer__send-icon" />
        </button>
      </div>
    </div>
  );
}
