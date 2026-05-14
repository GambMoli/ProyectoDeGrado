import { useEffect, useRef, useState } from "react";
import type { KeyboardEvent } from "react";
import AttachFileIcon from "@mui/icons-material/AttachFile";
import CloseIcon from "@mui/icons-material/Close";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
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
  readonly disabled: boolean;
  readonly isOcrLoading?: boolean;
  readonly openFormulaPanelTrigger?: string;
  readonly pendingText?: string | null;
  readonly selectedFile: File | null;
  readonly onClearFile: () => void;
  readonly onOpenAttach: () => void;
  readonly onPendingTextApplied?: () => void;
  readonly onSubmit: (message: string) => Promise<void>;
}

const formulaSnippets = [
  { label: "Integral", value: "∫ x^2 dx", preview: String.raw`\int x^2\,dx` },
  { label: "Por partes", value: "∫ x e^x dx", preview: String.raw`\int x e^x\,dx` },
  { label: "Derivada", value: "d/dx (x^3 + 2x)", preview: String.raw`\frac{d}{dx}(x^3 + 2x)` },
  { label: "Limite", value: "lim x->0 sin(x)/x", preview: String.raw`\lim_{x \to 0} \sin(x)/x` },
  { label: "Ecuacion", value: "x^2 + 3x = 10", preview: "x^2 + 3x = 10" },
  { label: "Raiz", value: "sqrt(x^2 + 1)", preview: String.raw`\sqrt{x^2 + 1}` },
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
  const [isRenderingMode, setIsRenderingMode] = useState(false);
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

  useEffect(() => {
    if (!message) {
      setIsRenderingMode(false);
    }
  }, [message]);

  async function handleSubmit() {
    if (isDisabled || (!message.trim() && !selectedFile)) {
      return;
    }

    await onSubmit(message.trim());
    setMessage("");
    setIsRenderingMode(false);
    setIsFormulaPanelOpen(false);
  }

  function handleKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void handleSubmit();
    }
  }

  function switchToEditMode() {
    setIsRenderingMode(false);
    setTimeout(() => textareaRef.current?.focus(), 0);
  }

  function insertFormulaTemplate(template: string) {
    if (isRenderingMode) {
      setIsRenderingMode(false);
      setTimeout(() => doInsertFormulaTemplate(template), 0);
      return;
    }
    doInsertFormulaTemplate(template);
  }

  function doInsertFormulaTemplate(template: string) {
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
  const mathSignal = /[=^+\-/*()∫√π∂∑∏²³⁴⁵⁶⁷⁸⁹αβγδθλμσφω]|\\(?:int|frac|sqrt|sin|cos|tan|lim)/;
  const messageLines = message.split("\n").map((l) => l.trim()).filter(Boolean);
  const mathLines = messageLines.filter((l) => mathSignal.test(l));
  const isMultiLineMath = mathLines.length > 1;
  const previewCandidate = (hasBlockMath || isMultiLineMath) ? null : extractMathCandidateForPreview(message);
  const previewLatex = previewCandidate ? plainMathToLatex(previewCandidate) : null;
  const showPreview = !isRenderingMode && (hasBlockMath || isMultiLineMath || Boolean(previewLatex));

  function renderPreviewContent() {
    if (isMultiLineMath) {
      return (
        <Box sx={{ display: "flex", flexDirection: "column", gap: 0.5 }}>
          {mathLines.map((line) => (
            <MathFormula key={line} expression={line} source="plain" displayMode />
          ))}
        </Box>
      );
    }
    if (hasBlockMath) {
      return <MathContent content={message} />;
    }
    return <MathFormula expression={previewLatex!} displayMode />;
  }

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
            {renderPreviewContent()}
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
        {isRenderingMode ? (
          <Box
            sx={{
              flex: 1,
              minHeight: 48,
              cursor: "text",
              position: "relative",
              py: 0.5,
              pr: 4,
              overflowX: "auto",
              "& .math-content": { fontSize: "0.98rem" },
            }}
            onClick={switchToEditMode}
          >
            <MathContent content={message} />
            <Tooltip title="Editar">
              <IconButton
                size="small"
                onClick={(e) => { e.stopPropagation(); switchToEditMode(); }}
                sx={{
                  position: "absolute",
                  top: 0,
                  right: 0,
                  color: "text.disabled",
                  p: 0.5,
                  "&:hover": { color: "primary.main" },
                }}
              >
                <EditOutlinedIcon sx={{ fontSize: 16 }} />
              </IconButton>
            </Tooltip>
          </Box>
        ) : (
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
        )}
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
