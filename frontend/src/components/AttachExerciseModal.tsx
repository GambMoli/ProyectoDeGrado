import { useEffect, useRef } from "react";
import type { ChangeEvent } from "react";

import { CameraIcon, CloseIcon, InfoIcon, UploadIcon } from "./Icons";

interface AttachExerciseModalProps {
  isOpen: boolean;
  selectedFile: File | null;
  onClose: () => void;
  onSelectFile: (file: File) => void;
}

export function AttachExerciseModal({
  isOpen,
  selectedFile,
  onClose,
  onSelectFile,
}: AttachExerciseModalProps) {
  const uploadInputRef = useRef<HTMLInputElement | null>(null);
  const cameraInputRef = useRef<HTMLInputElement | null>(null);

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

  function handleFileSelection(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    onSelectFile(file);
    event.target.value = "";
  }

  return (
    <div
      className={`attach-modal ${isOpen ? "is-open" : ""}`}
      aria-hidden={!isOpen}
      onClick={onClose}
    >
      <div className="attach-modal__dialog" onClick={(event) => event.stopPropagation()}>
        <div className="attach-modal__header">
          <h2>Adjuntar Ejercicio</h2>
          <button className="attach-modal__close" type="button" onClick={onClose} aria-label="Cerrar modal">
            <CloseIcon className="attach-modal__close-icon" />
          </button>
        </div>

        <div className="attach-modal__choices">
          <button
            className="attach-modal__choice"
            type="button"
            onClick={() => uploadInputRef.current?.click()}
          >
            <span className="attach-modal__choice-icon">
              <UploadIcon className="attach-modal__choice-svg" />
            </span>
            <strong>Subir desde dispositivo</strong>
            <span>Archivos locales</span>
          </button>

          <button
            className="attach-modal__choice"
            type="button"
            onClick={() => cameraInputRef.current?.click()}
          >
            <span className="attach-modal__choice-icon">
              <CameraIcon className="attach-modal__choice-svg" />
            </span>
            <strong>Usar Camara</strong>
            <span>Captura directa</span>
          </button>
        </div>

        <div className="attach-modal__info">
          <div className="attach-modal__info-icon">
            <InfoIcon className="attach-modal__info-svg" />
          </div>
          <div>
            <p>Formatos permitidos:</p>
            <strong>{selectedFile ? selectedFile.name : "PNG y JPEG"}</strong>
          </div>
        </div>

        <div className="attach-modal__footer">
          <button className="attach-modal__cancel" type="button" onClick={onClose}>
            Cancelar
          </button>
        </div>

        <input
          ref={uploadInputRef}
          type="file"
          accept="image/png,image/jpeg,image/jpg"
          hidden
          onChange={handleFileSelection}
        />
        <input
          ref={cameraInputRef}
          type="file"
          accept="image/png,image/jpeg,image/jpg"
          capture="environment"
          hidden
          onChange={handleFileSelection}
        />
      </div>
    </div>
  );
}
