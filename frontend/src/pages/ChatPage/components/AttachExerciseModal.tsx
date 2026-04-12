import { useRef } from "react";
import type { ChangeEvent } from "react";
import CameraAltOutlinedIcon from "@mui/icons-material/CameraAltOutlined";
import CloudUploadOutlinedIcon from "@mui/icons-material/CloudUploadOutlined";
import CloseIcon from "@mui/icons-material/Close";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Paper,
  Typography,
} from "@mui/material";

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

  function handleFileSelection(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    onSelectFile(file);
    event.target.value = "";
  }

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
        <IconButton aria-label="close" onClick={onClose} sx={{ color: "text.secondary" }}>
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <DialogContent sx={{ p: 2 }}>
        <Box sx={{ display: "flex", gap: 2, mb: 3, flexDirection: { xs: "column", sm: "row" } }}>
          <Box
            component="button"
            onClick={() => uploadInputRef.current?.click()}
            sx={{
              flex: 1,
              border: "1px dashed",
              borderColor: "divider",
              borderRadius: 2,
              p: 3,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              bgcolor: "background.default",
              cursor: "pointer",
              transition: "all 0.2s ease",
              "&:hover": { borderColor: "primary.main", bgcolor: "primary.light" },
            }}
          >
            <Box
              sx={{
                bgcolor: "primary.main",
                color: "white",
                borderRadius: 2,
                p: 1.5,
                mb: 2,
                display: "flex",
              }}
            >
              <CloudUploadOutlinedIcon />
            </Box>
            <Typography variant="subtitle2" sx={{ fontWeight: 800, color: "text.primary", mb: 0.5 }}>
              Subir archivo
            </Typography>
            <Typography variant="caption" sx={{ color: "text.secondary", fontWeight: 600 }}>
              Imagen desde el equipo
            </Typography>
          </Box>

          <Box
            component="button"
            onClick={() => cameraInputRef.current?.click()}
            sx={{
              flex: 1,
              border: "1px dashed",
              borderColor: "divider",
              borderRadius: 2,
              p: 3,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              bgcolor: "background.default",
              cursor: "pointer",
              transition: "all 0.2s ease",
              "&:hover": { borderColor: "primary.main", bgcolor: "primary.light" },
            }}
          >
            <Box
              sx={{
                bgcolor: "primary.main",
                color: "white",
                borderRadius: 2,
                p: 1.5,
                mb: 2,
                display: "flex",
              }}
            >
              <CameraAltOutlinedIcon />
            </Box>
            <Typography variant="subtitle2" sx={{ fontWeight: 800, color: "text.primary", mb: 0.5 }}>
              Usar camara
            </Typography>
            <Typography variant="caption" sx={{ color: "text.secondary", fontWeight: 600 }}>
              Captura directa
            </Typography>
          </Box>
        </Box>

        <Paper
          sx={{
            bgcolor: "background.default",
            p: 2,
            display: "flex",
            gap: 1.5,
            alignItems: "center",
          }}
        >
          <InfoOutlinedIcon sx={{ color: "primary.main" }} />
          <Box>
            <Typography variant="caption" sx={{ fontWeight: 700, color: "text.secondary", display: "block" }}>
              Formatos permitidos
            </Typography>
            <Typography variant="caption" sx={{ fontWeight: 800, color: "primary.main" }}>
              {selectedFile ? selectedFile.name : "PNG y JPEG"}
            </Typography>
          </Box>
        </Paper>
      </DialogContent>

      <DialogActions sx={{ p: 2, pt: 1 }}>
        <Button onClick={onClose} variant="text" color="inherit">
          Cancelar
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
