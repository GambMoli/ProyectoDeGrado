import { useRef } from "react";
import type { ChangeEvent } from "react";
import { 
  Dialog, 
  DialogTitle, 
  DialogContent, 
  DialogActions, 
  IconButton, 
  Typography, 
  Box, 
  Button,
  Paper
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import CloudUploadOutlinedIcon from "@mui/icons-material/CloudUploadOutlined";
import CameraAltOutlinedIcon from "@mui/icons-material/CameraAltOutlined";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";

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
    if (!file) return;

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
        sx: { borderRadius: 4, p: 1, boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1)" }
      }}
    >
      <DialogTitle sx={{ m: 0, p: 2, pb: 1, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <Typography variant="h6" sx={{ color: "#1E3A8A", fontWeight: 800, fontSize: "1.1rem" }}>
          Adjuntar Ejercicio
        </Typography>
        <IconButton aria-label="close" onClick={onClose} sx={{ color: "#9CA3AF" }}>
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      
      <DialogContent sx={{ p: 2 }}>
        <Box sx={{ display: "flex", gap: 2, mb: 3 }}>
          {/* Upload from device */}
          <Box 
            component="button"
            onClick={() => uploadInputRef.current?.click()}
            sx={{ 
              flex: 1, 
              border: "2px dashed #E5E7EB", 
              borderRadius: 4, 
              p: 3, 
              display: "flex", 
              flexDirection: "column", 
              alignItems: "center",
              bgcolor: "transparent",
              cursor: "pointer",
              transition: "all 0.2s",
              "&:hover": { borderColor: "#1E3A8A", bgcolor: "#EFF6FF" }
            }}
          >
            <Box sx={{ bgcolor: "#1E3A8A", color: "white", borderRadius: "50%", p: 1.5, mb: 2, display: "flex" }}>
              <CloudUploadOutlinedIcon />
            </Box>
            <Typography variant="subtitle2" sx={{ fontWeight: 800, color: "#1F2937", mb: 0.5 }}>
              Subir archivo
            </Typography>
            <Typography variant="caption" sx={{ color: "#6B7280", fontWeight: 600 }}>
              Archivos locales
            </Typography>
          </Box>

          {/* Camera */}
          <Box 
            component="button"
            onClick={() => cameraInputRef.current?.click()}
            sx={{ 
              flex: 1, 
              border: "2px dashed #E5E7EB", 
              borderRadius: 4, 
              p: 3, 
              display: "flex", 
              flexDirection: "column", 
              alignItems: "center",
              bgcolor: "transparent",
              cursor: "pointer",
              transition: "all 0.2s",
              "&:hover": { borderColor: "#1E3A8A", bgcolor: "#EFF6FF" }
            }}
          >
            <Box sx={{ bgcolor: "#1E3A8A", color: "white", borderRadius: "50%", p: 1.5, mb: 2, display: "flex" }}>
              <CameraAltOutlinedIcon />
            </Box>
            <Typography variant="subtitle2" sx={{ fontWeight: 800, color: "#1F2937", mb: 0.5 }}>
              Usar Cámara
            </Typography>
            <Typography variant="caption" sx={{ color: "#6B7280", fontWeight: 600 }}>
              Captura directa
            </Typography>
          </Box>
        </Box>

        <Paper elevation={0} sx={{ bgcolor: "#F9FAFB", borderRadius: 3, p: 2, display: "flex", gap: 1.5, alignItems: "center" }}>
          <InfoOutlinedIcon sx={{ color: "#1E3A8A" }} />
          <Box>
            <Typography variant="caption" sx={{ fontWeight: 700, color: "#4B5563", display: "block" }}>
              Formatos permitidos:
            </Typography>
            <Typography variant="caption" sx={{ fontWeight: 800, color: "#1E3A8A" }}>
              {selectedFile ? selectedFile.name : "PNG Y JPEG"}
            </Typography>
          </Box>
        </Paper>
      </DialogContent>

      <DialogActions sx={{ p: 2, pt: 1 }}>
        <Button 
          onClick={onClose} 
          sx={{ 
            color: "#4B5563", 
            fontWeight: 700, 
            textTransform: "none",
            "&:hover": { bgcolor: "#F3F4F6" }
          }}
        >
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
