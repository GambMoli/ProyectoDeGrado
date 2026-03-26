import { useRef, useState } from "react";
import type { ChangeEvent, KeyboardEvent } from "react";

interface ComposerProps {
  disabled: boolean;
  onSubmit: (payload: { message: string; file: File | null }) => Promise<void>;
}

export function Composer({ disabled, onSubmit }: ComposerProps) {
  const [message, setMessage] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  async function handleSubmit() {
    if (disabled || (!message.trim() && !selectedFile)) {
      return;
    }

    await onSubmit({
      message: message.trim(),
      file: selectedFile,
    });
    setMessage("");
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void handleSubmit();
    }
  }

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const nextFile = event.target.files?.[0] ?? null;
    setSelectedFile(nextFile);
  }

  return (
    <div className="composer">
      <div className="composer__controls">
        <textarea
          className="composer__textarea"
          placeholder="Escribe tu duda o pega el ejercicio. Ejemplo: integral de x^2 dx"
          value={message}
          disabled={disabled}
          onChange={(event) => setMessage(event.target.value)}
          onKeyDown={handleKeyDown}
          rows={4}
        />

        <div className="composer__actions">
          <label className="button button--ghost composer__upload">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/png,image/jpeg,image/jpg,image/webp"
              disabled={disabled}
              onChange={handleFileChange}
            />
            Subir imagen
          </label>

          <button className="button button--primary" type="button" disabled={disabled} onClick={() => void handleSubmit()}>
            {disabled ? "Procesando..." : "Enviar"}
          </button>
        </div>
      </div>

      <div className="composer__footer">
        <span>
          Puedes enviar texto, imagen o ambos. Si subes una imagen borrosa, el sistema te pedirá una versión más clara.
        </span>
        {selectedFile ? <strong>Archivo listo: {selectedFile.name}</strong> : <strong>Sin imagen adjunta</strong>}
      </div>
    </div>
  );
}
