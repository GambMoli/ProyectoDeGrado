import { useRef, useState } from "react";
import type { KeyboardEvent } from "react";

import { AttachmentIcon, CloseIcon, FormulaIcon, SendIcon } from "./Icons";

interface ComposerProps {
  disabled: boolean;
  selectedFile: File | null;
  onClearFile: () => void;
  onOpenAttach: () => void;
  onSubmit: (message: string) => Promise<void>;
}

export function Composer({
  disabled,
  selectedFile,
  onClearFile,
  onOpenAttach,
  onSubmit,
}: ComposerProps) {
  const [message, setMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  async function handleSubmit() {
    if (disabled || (!message.trim() && !selectedFile)) {
      return;
    }

    await onSubmit(message.trim());
    setMessage("");
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void handleSubmit();
    }
  }

  function insertFormulaTemplate() {
    const nextValue = message ? `${message}  f(x) = ` : "f(x) = ";
    setMessage(nextValue);
    requestAnimationFrame(() => {
      textareaRef.current?.focus();
      textareaRef.current?.setSelectionRange(nextValue.length, nextValue.length);
    });
  }

  return (
    <div className="composer">
      <div className="composer__tools">
        <button className="composer__tool" type="button" onClick={insertFormulaTemplate}>
          <FormulaIcon className="composer__tool-icon" />
          <span>Insertar formula</span>
        </button>
        <button className="composer__tool" type="button" onClick={onOpenAttach}>
          <AttachmentIcon className="composer__tool-icon" />
          <span>PNG/JPEG</span>
        </button>
        <span className="composer__presence" aria-hidden="true" />
      </div>

      {selectedFile ? (
        <div className="composer__file-chip">
          <span>{selectedFile.name}</span>
          <button type="button" onClick={onClearFile} aria-label="Quitar archivo adjunto">
            <CloseIcon className="composer__file-chip-icon" />
          </button>
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
