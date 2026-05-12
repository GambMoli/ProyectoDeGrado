import { useEffect, useRef, useState } from "react";
import type { ChangeEvent } from "react";
import CameraAltOutlinedIcon from "@mui/icons-material/CameraAltOutlined";
import CloudUploadOutlinedIcon from "@mui/icons-material/CloudUploadOutlined";
import CloseIcon from "@mui/icons-material/Close";
import CheckIcon from "@mui/icons-material/Check";
import ImageOutlinedIcon from "@mui/icons-material/ImageOutlined";
import {
  Box,
  Button,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Typography,
} from "@mui/material";

const MAX_FILES = 2;

interface AttachExerciseModalProps {
  isLoading?: boolean;
  isOpen: boolean;
  onClose: () => void;
  onConfirmFiles: (files: File[]) => void;
}

export function AttachExerciseModal({
  isLoading = false,
  isOpen,
  onClose,
  onConfirmFiles,
}: AttachExerciseModalProps) {
  const uploadInputRef = useRef<HTMLInputElement | null>(null);
  const cameraInputRef = useRef<HTMLInputElement | null>(null);
  const [pendingFiles, setPendingFiles] = useState<File[]>([]);

  const isAtLimit = pendingFiles.length >= MAX_FILES || isLoading;

  useEffect(() => {
    if (!isOpen) {
      setPendingFiles([]);
    }
  }, [isOpen]);

  function handleFileSelection(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }
    setPendingFiles((prev) => {
      if (prev.length >= MAX_FILES) return prev;
      return [...prev, file];
    });
    event.target.value = "";
  }

  function removeFile(index: number) {
    setPendingFiles((prev) => prev.filter((_, i) => i !== index));
  }

  function handleConfirm() {
    if (pendingFiles.length === 0) return;
    onConfirmFiles(pendingFiles);
  }

  const confirmLabel =
    pendingFiles.length === 0
      ? "Confirmar"
      : pendingFiles.length === 1
        ? "Confirmar (1 imagen)"
        : "Confirmar (2 imágenes)";

  return (
    <Dialog
      open={isOpen}
      onClose={onClose}
      maxWidth="xs"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 2.5,
          p: 1,
          boxShadow: "none",
        },
      }}
    >
      <DialogTitle
        sx={{
          m: 0,
          p: 2,
          pb: 1,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <Box>
          <Typography variant="overline" sx={{ color: "primary.main", fontWeight: 800, letterSpacing: "0.12em" }}>
            Cubik IA
          </Typography>
          <Typography variant="h6" sx={{ color: "text.primary" }}>
            Adjuntar ejercicio
          </Typography>
        </Box>
        <IconButton aria-label="close" onClick={onClose} disabled={isLoading} sx={{ color: "text.secondary" }}>
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <DialogContent sx={{ p: 2 }}>
        <Box sx={{ display: "flex", gap: 2, mb: pendingFiles.length > 0 ? 2 : 3, flexDirection: { xs: "column", sm: "row" } }}>
          <Box
            component="button"
            onClick={() => !isAtLimit && uploadInputRef.current?.click()}
            disabled={isAtLimit}
            sx={{
              flex: 1,
              border: "1px dashed",
              borderColor: isAtLimit ? "action.disabled" : "divider",
              borderRadius: 2,
              p: 3,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              bgcolor: "background.default",
              cursor: isAtLimit ? "not-allowed" : "pointer",
              opacity: isAtLimit ? 0.45 : 1,
              transition: "all 0.2s ease",
              "&:hover": isAtLimit
                ? {}
                : { borderColor: "primary.main", bgcolor: "primary.light" },
            }}
          >
            <Box
              sx={{
                bgcolor: isAtLimit ? "action.disabled" : "primary.main",
                color: "white",
                borderRadius: 2,
                p: 1.5,
                mb: 2,
                display: "flex",
              }}
            >
              <CloudUploadOutlinedIcon />
            </Box>
            <Typography variant="subtitle2" sx={{ fontWeight: 800, color: isAtLimit ? "text.disabled" : "text.primary", mb: 0.5 }}>
              Subir archivo
            </Typography>
            <Typography variant="caption" sx={{ color: "text.secondary", fontWeight: 600 }}>
              Imagen desde el equipo
            </Typography>
          </Box>

          <Box
            component="button"
            onClick={() => !isAtLimit && cameraInputRef.current?.click()}
            disabled={isAtLimit}
            sx={{
              flex: 1,
              border: "1px dashed",
              borderColor: isAtLimit ? "action.disabled" : "divider",
              borderRadius: 2,
              p: 3,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              bgcolor: "background.default",
              cursor: isAtLimit ? "not-allowed" : "pointer",
              opacity: isAtLimit ? 0.45 : 1,
              transition: "all 0.2s ease",
              "&:hover": isAtLimit
                ? {}
                : { borderColor: "primary.main", bgcolor: "primary.light" },
            }}
          >
            <Box
              sx={{
                bgcolor: isAtLimit ? "action.disabled" : "primary.main",
                color: "white",
                borderRadius: 2,
                p: 1.5,
                mb: 2,
                display: "flex",
              }}
            >
              <CameraAltOutlinedIcon />
            </Box>
            <Typography variant="subtitle2" sx={{ fontWeight: 800, color: isAtLimit ? "text.disabled" : "text.primary", mb: 0.5 }}>
              Usar camara
            </Typography>
            <Typography variant="caption" sx={{ color: "text.secondary", fontWeight: 600 }}>
              Captura directa
            </Typography>
          </Box>
        </Box>

        {pendingFiles.length > 0 ? (
          <Box sx={{ mb: 2, display: "flex", flexDirection: "column", gap: 1 }}>
            {pendingFiles.map((file, index) => (
              <Box
                key={`${file.name}-${index}`}
                sx={{
                  display: "flex",
                  alignItems: "center",
                  gap: 1,
                  p: 1.25,
                  borderRadius: 1.5,
                  bgcolor: "background.default",
                  border: "1px solid",
                  borderColor: "divider",
                }}
              >
                <ImageOutlinedIcon sx={{ color: "primary.main", fontSize: 18, flexShrink: 0 }} />
                <Typography
                  variant="caption"
                  sx={{
                    flexGrow: 1,
                    fontWeight: 700,
                    color: "text.primary",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                >
                  {file.name}
                </Typography>
                <Chip
                  label={`Img ${index + 1}`}
                  size="small"
                  sx={{ bgcolor: "primary.light", color: "primary.main", fontWeight: 700, fontSize: "0.65rem" }}
                />
                <IconButton
                  size="small"
                  onClick={() => removeFile(index)}
                  sx={{ color: "text.secondary", p: 0.25 }}
                >
                  <CloseIcon sx={{ fontSize: 16 }} />
                </IconButton>
              </Box>
            ))}
          </Box>
        ) : null}

        <Typography
          variant="caption"
          sx={{ color: "text.secondary", fontWeight: 600, display: "block" }}
        >
          Formatos: PNG y JPEG · Máximo {MAX_FILES} imágenes
          {isAtLimit ? " · Límite alcanzado" : ` · ${MAX_FILES - pendingFiles.length} restante${MAX_FILES - pendingFiles.length === 1 ? "" : "s"}`}
        </Typography>
      </DialogContent>

      <DialogActions sx={{ p: 2, pt: 1, gap: 1 }}>
        <Button onClick={onClose} variant="text" color="inherit" disabled={isLoading}>
          Cancelar
        </Button>
        <Button
          onClick={handleConfirm}
          disabled={isLoading || pendingFiles.length === 0}
          variant="contained"
          startIcon={
            isLoading
              ? <CircularProgress size={16} color="inherit" />
              : <CheckIcon />
          }
        >
          {isLoading ? "Procesando..." : confirmLabel}
        </Button>
      </DialogActions>

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
    </Dialog>
  );
}
