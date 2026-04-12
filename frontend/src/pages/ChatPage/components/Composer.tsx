import { useRef, useState } from "react";
import type { KeyboardEvent } from "react";
import AttachFileIcon from "@mui/icons-material/AttachFile";
import CloseIcon from "@mui/icons-material/Close";
import FunctionsIcon from "@mui/icons-material/Functions";
import SendIcon from "@mui/icons-material/Send";
import {
  Box,
  Button,
  Chip,
  Grid,
  IconButton,
  Paper,
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";

import { extractMathCandidateForPreview, MathFormula, plainMathToLatex } from "../../../components";

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

  function handleKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void handleSubmit();
    }
  }

  function insertFormulaTemplate(template: string) {
    const textarea = textareaRef.current;
    if (!textarea) {
      return;
    }

    const selectionStart = textarea.selectionStart ?? message.length;
    const selectionEnd = textarea.selectionEnd ?? message.length;
    const prefix = message.slice(0, selectionStart);
    const suffix = message.slice(selectionEnd);
    const glue = prefix && !prefix.endsWith(" ") && !prefix.endsWith("\n") ? " " : "";
    const nextValue = `${prefix}${glue}${template}${suffix}`;
    const cursorPosition = (prefix + glue + template).length;

    setMessage(nextValue);

    setTimeout(() => {
      textarea.focus();
      textarea.setSelectionRange(cursorPosition, cursorPosition);
    }, 0);
  }

  const previewCandidate = extractMathCandidateForPreview(message);
  const previewLatex = previewCandidate ? plainMathToLatex(previewCandidate) : null;

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5 }}>
      <Box sx={{ display: "flex", alignItems: "center", gap: 2, px: 0.5 }}>
        <Button
          size="small"
          startIcon={<FunctionsIcon />}
          onClick={() => setIsFormulaPanelOpen((value) => !value)}
          sx={{
            color: isFormulaPanelOpen ? "#1E3A8A" : "#6B7280",
            textTransform: "none",
            fontWeight: 700,
            fontSize: "0.75rem",
            bgcolor: isFormulaPanelOpen ? "#EFF6FF" : "transparent",
            "&:hover": { bgcolor: "#F3F4F6" },
          }}
        >
          Insertar formula
        </Button>
        <Button
          size="small"
          startIcon={<AttachFileIcon />}
          onClick={onOpenAttach}
          sx={{
            color: "#6B7280",
            textTransform: "none",
            fontWeight: 700,
            fontSize: "0.75rem",
            "&:hover": { bgcolor: "#F3F4F6" },
          }}
        >
          PNG/JPEG
        </Button>
        <Box sx={{ ml: "auto", width: 8, height: 8, borderRadius: "50%", bgcolor: "#10B981" }} />
      </Box>

      {isFormulaPanelOpen ? (
        <Paper
          elevation={0}
          sx={{
            p: 2,
            borderRadius: 3,
            bgcolor: "#F9FAFB",
            border: "1px solid #E5E7EB",
          }}
        >
          <Grid container spacing={1.5}>
            {formulaSnippets.map((snippet) => (
              <Grid item xs={6} sm={4} key={snippet.label}>
                <Button
                  fullWidth
                  onClick={() => insertFormulaTemplate(snippet.value)}
                  sx={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "flex-start",
                    p: 1.5,
                    borderRadius: 2,
                    bgcolor: "#fff",
                    border: "1px solid #E5E7EB",
                    textTransform: "none",
                    color: "inherit",
                    "&:hover": { borderColor: "#1E3A8A", bgcolor: "#fff" },
                  }}
                >
                  <Typography
                    variant="caption"
                    sx={{
                      fontWeight: 800,
                      color: "#1E3A8A",
                      mb: 1,
                      textTransform: "uppercase",
                    }}
                  >
                    {snippet.label}
                  </Typography>
                  <Box sx={{ width: "100%", overflowX: "auto" }}>
                    <MathFormula expression={snippet.preview} displayMode />
                  </Box>
                </Button>
              </Grid>
            ))}
          </Grid>
          <Typography variant="caption" sx={{ mt: 1.5, display: "block", color: "#6B7280" }}>
            El asistente entiende entradas como `∫ x^2 dx`, `d/dx (x^3)` o `lim x-&gt;0 sin(x)/x`.
          </Typography>
        </Paper>
      ) : null}

      {selectedFile ? (
        <Box sx={{ px: 0.5 }}>
          <Chip
            label={selectedFile.name}
            onDelete={onClearFile}
            deleteIcon={<CloseIcon sx={{ fontSize: "14px !important" }} />}
            sx={{
              bgcolor: "#EFF6FF",
              color: "#1E3A8A",
              fontWeight: 700,
              borderRadius: "8px",
              "& .MuiChip-deleteIcon": {
                color: "#1E3A8A",
                "&:hover": { color: "#1E40AF" },
              },
            }}
          />
        </Box>
      ) : null}

      {previewLatex ? (
        <Paper
          elevation={0}
          sx={{
            p: 2,
            borderRadius: 3,
            bgcolor: "#F9FAFB",
            border: "1px solid #E5E7EB",
          }}
        >
          <Typography
            variant="caption"
            sx={{
              fontWeight: 800,
              color: "#1E3A8A",
              mb: 1,
              display: "block",
              textTransform: "uppercase",
            }}
          >
            Vista previa
          </Typography>
          <Box sx={{ overflowX: "auto" }}>
            <MathFormula expression={previewLatex} displayMode />
          </Box>
        </Paper>
      ) : null}

      <Box
        sx={{
          display: "flex",
          alignItems: "flex-end",
          gap: 1.5,
          p: 1.5,
          bgcolor: "#fff",
          borderRadius: 4,
          border: "1px solid #E5E7EB",
          boxShadow: "0 4px 12px rgba(0,0,0,0.05)",
          "&:focus-within": { borderColor: "#1E3A8A" },
        }}
      >
        <TextField
          fullWidth
          multiline
          maxRows={6}
          placeholder="Escribe tu consulta matematica aqui..."
          value={message}
          disabled={disabled}
          onChange={(event) => setMessage(event.target.value)}
          onKeyDown={handleKeyDown}
          inputRef={textareaRef}
          variant="standard"
          InputProps={{
            disableUnderline: true,
            sx: { fontSize: "0.95rem", py: 0.5 },
          }}
        />
        <Tooltip title="Enviar mensaje">
          <span>
            <IconButton
              onClick={() => void handleSubmit()}
              disabled={disabled || (!message.trim() && !selectedFile)}
              sx={{
                bgcolor: "#1E3A8A",
                color: "#fff",
                borderRadius: "12px",
                p: 1.5,
                "&:hover": { bgcolor: "#1E40AF" },
                "&.Mui-disabled": { bgcolor: "#F3F4F6", color: "#9CA3AF" },
              }}
            >
              <SendIcon fontSize="small" />
            </IconButton>
          </span>
        </Tooltip>
      </Box>
    </Box>
  );
}
