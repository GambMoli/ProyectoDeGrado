import { useEffect, useRef, useState } from "react";
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

import { extractMathCandidateForPreview, MathContent, MathFormula, plainMathToLatex } from "../../../components";

interface ComposerProps {
  disabled: boolean;
  isOcrLoading?: boolean;
  openFormulaPanelTrigger?: string;
  pendingText?: string | null;
  selectedFile: File | null;
  onClearFile: () => void;
  onOpenAttach: () => void;
  onPendingTextApplied?: () => void;
  onSubmit: (message: string) => Promise<void>;
}

const formulaSnippets = [
  { label: "Integral", value: "∫ x^2 dx", preview: "\\int x^2\\,dx" },
  { label: "Por partes", value: "∫ x e^x dx", preview: "\\int x e^x\\,dx" },
  { label: "Derivada", value: "d/dx (x^3 + 2x)", preview: "\\frac{d}{dx}(x^3 + 2x)" },
  { label: "Limite", value: "lim x->0 sin(x)/x", preview: "\\lim_{x \\to 0} \\sin(x)/x" },
  { label: "Ecuacion", value: "x^2 + 3x = 10", preview: "x^2 + 3x = 10" },
  { label: "Raiz", value: "sqrt(x^2 + 1)", preview: "\\sqrt{x^2 + 1}" },
];

export function Composer({
  disabled,
  isOcrLoading,
  openFormulaPanelTrigger,
  pendingText,
  selectedFile,
  onClearFile,
  onOpenAttach,
  onPendingTextApplied,
  onSubmit,
}: ComposerProps) {
  const [message, setMessage] = useState("");
  const [isFormulaPanelOpen, setIsFormulaPanelOpen] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  const isDisabled = disabled || Boolean(isOcrLoading);

  useEffect(() => {
    if (openFormulaPanelTrigger) {
      setIsFormulaPanelOpen(true);
    }
  }, [openFormulaPanelTrigger]);

  useEffect(() => {
    if (pendingText != null) {
      setMessage(pendingText);
      onPendingTextApplied?.();
      setTimeout(() => textareaRef.current?.focus(), 0);
    }
  }, [pendingText]);

  async function handleSubmit() {
    if (isDisabled || (!message.trim() && !selectedFile)) {
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

  const hasBlockMath = /\\\[[\s\S]*?\\\]/.test(message);
  const previewCandidate = hasBlockMath ? null : extractMathCandidateForPreview(message);
  const previewLatex = previewCandidate ? plainMathToLatex(previewCandidate) : null;
  const showPreview = hasBlockMath || Boolean(previewLatex);

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5 }}>
      <Box sx={{ display: "flex", alignItems: "center", gap: 1, flexWrap: "wrap" }}>
        <Button
          size="small"
          startIcon={<FunctionsIcon />}
          onClick={() => setIsFormulaPanelOpen((value) => !value)}
          variant={isFormulaPanelOpen ? "contained" : "text"}
        >
          Insertar formula
        </Button>
        <Button size="small" startIcon={<AttachFileIcon />} onClick={onOpenAttach} color="inherit">
          Adjuntar PNG o JPEG
        </Button>
        <Typography variant="caption" sx={{ ml: { xs: 0, md: "auto" }, color: "success.main", fontWeight: 700 }}>
          Sistema disponible
        </Typography>
      </Box>

      {isFormulaPanelOpen ? (
        <Paper sx={{ p: 2.5, bgcolor: "background.default" }}>
          <Grid container spacing={1.5}>
            {formulaSnippets.map((snippet) => (
              <Grid item xs={12} sm={6} lg={4} key={snippet.label}>
                <Button
                  fullWidth
                  onClick={() => insertFormulaTemplate(snippet.value)}
                  sx={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "flex-start",
                    minHeight: 116,
                    p: 2,
                    gap: 1,
                    bgcolor: "background.paper",
                    border: "1px solid",
                    borderColor: "divider",
                    color: "text.primary",
                    "&:hover": {
                      bgcolor: "background.paper",
                      borderColor: "primary.main",
                    },
                  }}
                >
                  <Typography
                    variant="caption"
                    sx={{
                      fontWeight: 800,
                      color: "primary.main",
                      textTransform: "uppercase",
                      letterSpacing: "0.08em",
                    }}
                  >
                    {snippet.label}
                  </Typography>
                  <Box sx={{ width: "100%", overflowX: "auto", textAlign: "left" }}>
                    <MathFormula expression={snippet.preview} displayMode />
                  </Box>
                </Button>
              </Grid>
            ))}
          </Grid>
          <Typography variant="caption" sx={{ mt: 1.5, display: "block", color: "text.secondary" }}>
            El asistente entiende entradas como `∫ x^2 dx`, `d/dx (x^3)` o `lim x-&gt;0 sin(x)/x`.
          </Typography>
        </Paper>
      ) : null}

      {selectedFile ? (
        <Box>
          <Chip
            label={selectedFile.name}
            onDelete={onClearFile}
            deleteIcon={<CloseIcon sx={{ fontSize: "14px !important" }} />}
            sx={{
              bgcolor: "primary.light",
              color: "primary.main",
              fontWeight: 700,
              "& .MuiChip-deleteIcon": {
                color: "primary.main",
              },
            }}
          />
        </Box>
      ) : null}

      {showPreview ? (
        <Paper sx={{ p: 2.5, bgcolor: "background.default" }}>
          <Typography
            variant="caption"
            sx={{
              fontWeight: 800,
              color: "primary.main",
              mb: 1,
              display: "block",
              textTransform: "uppercase",
              letterSpacing: "0.08em",
            }}
          >
            Vista previa matematica
          </Typography>
          <Box sx={{ overflowX: "auto" }}>
            {hasBlockMath ? (
              <MathContent content={message} />
            ) : (
              <MathFormula expression={previewLatex!} displayMode />
            )}
          </Box>
        </Paper>
      ) : null}

      <Paper
        sx={{
          display: "flex",
          alignItems: "flex-end",
          gap: 1.5,
          p: 1.5,
          bgcolor: "background.default",
          borderColor: "divider",
        }}
      >
        <TextField
          fullWidth
          multiline
          maxRows={6}
          placeholder="Escribe tu consulta matematica aqui..."
          value={message}
          disabled={isDisabled}
          onChange={(event) => setMessage(event.target.value)}
          onKeyDown={handleKeyDown}
          inputRef={textareaRef}
          variant="standard"
          InputProps={{
            disableUnderline: true,
            sx: { fontSize: "0.98rem", py: 0.5 },
          }}
        />
        <Tooltip title="Enviar mensaje">
          <span>
            <IconButton
              onClick={() => void handleSubmit()}
              disabled={isDisabled || (!message.trim() && !selectedFile)}
              color="primary"
              sx={{
                bgcolor: "primary.main",
                color: "#FFFFFF",
                borderRadius: 2,
                p: 1.5,
                "&:hover": { bgcolor: "primary.dark" },
                "&.Mui-disabled": { bgcolor: "action.disabledBackground", color: "action.disabled" },
              }}
            >
              <SendIcon fontSize="small" />
            </IconButton>
          </span>
        </Tooltip>
      </Paper>
    </Box>
  );
}
