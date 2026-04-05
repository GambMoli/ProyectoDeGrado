import React, { useEffect, useState } from "react";
import { Box, Typography, Button } from "@mui/material";
import { MainLayout } from "../layouts/MainLayout";
import { getConversation, getConversations, sendChatMessage, uploadExerciseImage } from "../api/client";
import { AttachExerciseModal } from "../components/AttachExerciseModal";
import { ChatMessage } from "../components/ChatMessage";
import { Composer } from "../components/Composer";
import { HistoryDrawer } from "../components/HistoryDrawer";
import { StatusBanner } from "../components/StatusBanner";
import type { ConversationDetail, ConversationSummary } from "../types/api";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import ChatBubbleOutlineIcon from "@mui/icons-material/ChatBubbleOutline";

const USER_STORAGE_KEY = "calc-tutor-user-id";
const CONVERSATION_STORAGE_KEY = "calc-tutor-conversation-id";

function createUserId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `student-${Math.random().toString(36).slice(2, 10)}`;
}

export function ChatPage() {
  const [userId] = useState<string>(() => localStorage.getItem(USER_STORAGE_KEY) ?? createUserId());
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(
    () => localStorage.getItem(CONVERSATION_STORAGE_KEY)
  );
  const [activeConversation, setActiveConversation] = useState<ConversationDetail | null>(null);
  const [isHistoryLoading, setIsHistoryLoading] = useState(false);
  const [isConversationLoading, setIsConversationLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [isAttachModalOpen, setIsAttachModalOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    localStorage.setItem(USER_STORAGE_KEY, userId);
  }, [userId]);

  useEffect(() => {
    if (activeConversationId) {
      localStorage.setItem(CONVERSATION_STORAGE_KEY, activeConversationId);
      return;
    }
    localStorage.removeItem(CONVERSATION_STORAGE_KEY);
  }, [activeConversationId]);

  useEffect(() => {
    void refreshConversations();
  }, []);

  useEffect(() => {
    if (!activeConversationId) {
      setActiveConversation(null);
      return;
    }
    void loadConversation(activeConversationId);
  }, [activeConversationId]);

  async function refreshConversations(preferredConversationId?: string) {
    setIsHistoryLoading(true);
    try {
      const items = await getConversations(userId);
      setConversations(items);
      if (preferredConversationId) {
        setActiveConversationId(preferredConversationId);
      } else if (items.length > 0 && !activeConversationId) {
        setActiveConversationId(items[0].id);
      } else if (
        activeConversationId &&
        !items.some((conversation) => conversation.id === activeConversationId)
      ) {
        setActiveConversationId(items[0]?.id ?? null);
      }
    } catch (nextError) {
      const message = nextError instanceof Error ? nextError.message : "No se pudo cargar el historial.";
      setError(message);
    } finally {
      setIsHistoryLoading(false);
    }
  }

  async function loadConversation(conversationId: string) {
    setIsConversationLoading(true);
    try {
      const detail = await getConversation(conversationId, userId);
      setActiveConversation(detail);
    } catch (nextError) {
      const message = nextError instanceof Error ? nextError.message : "No se pudo cargar la conversacion.";
      setError(message);
    } finally {
      setIsConversationLoading(false);
    }
  }

  async function handleComposerSubmit(message: string) {
    setError(null);
    setIsSubmitting(true);
    try {
      const response = selectedFile
        ? await uploadExerciseImage({
            file: selectedFile,
            userId,
            conversationId: activeConversationId,
            prompt: message,
          })
        : await sendChatMessage({
            user_id: userId,
            conversation_id: activeConversationId,
            message,
          });

      setSelectedFile(null);
      await loadConversation(response.conversation_id);
      await refreshConversations(response.conversation_id);
    } catch (nextError) {
      const nextMessage = nextError instanceof Error ? nextError.message : "No se pudo enviar el mensaje.";
      setError(nextMessage);
    } finally {
      setIsSubmitting(false);
    }
  }

  function handleNewConversation() {
    setError(null);
    setSelectedFile(null);
    setActiveConversationId(null);
    setActiveConversation(null);
    setIsHistoryOpen(false);
  }

  const hasMessages = Boolean(activeConversation && activeConversation.messages.length > 0);

  return (
    <MainLayout
      onOpenHistory={() => setIsHistoryOpen(true)}
      onOpenAttach={() => setIsAttachModalOpen(true)}
    >
      <Box sx={{ display: "flex", flexDirection: "column", height: "100%", position: "relative" }}>
        {error && (
            <Box sx={{ p: 2 }}>
                <StatusBanner tone="error" message={error} />
            </Box>
        )}

        <Box sx={{ flexGrow: 1, overflowY: "auto", px: { xs: 2, md: 4 }, py: 3, display: "flex", flexDirection: "column", gap: 3 }}>
          {isConversationLoading ? (
            <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center", flexGrow: 1 }}>
                <Typography variant="body2" sx={{ color: "#6B7280", fontWeight: 600 }}>Cargando conversación...</Typography>
            </Box>
          ) : (
            <>
              {!hasMessages && (
                <Box sx={{ display: "flex", gap: 2, mb: 3 }}>
                   <Box sx={{ width: 40, height: 40, borderRadius: "50%", bgcolor: "#EFF6FF", color: "#1E3A8A", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                      <ChatBubbleOutlineIcon fontSize="small" />
                   </Box>
                   <Box sx={{ bgcolor: "#F3F4F6", color: "#1F2937", p: 2.5, borderRadius: 3, borderTopLeftRadius: 4, maxWidth: "75%" }}>
                      <Typography variant="body2" sx={{ fontSize: "0.95rem" }}>
                         ¡Hola! Soy tu asistente de <strong>Cubik IA</strong>. Estoy listo para ayudarte con cálculos matemáticos complejos, álgebra, cálculo o estadística. ¿Qué problema resolveremos hoy?
                      </Typography>
                   </Box>
                </Box>
              )}
              {activeConversation?.messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
            </>
          )}
        </Box>

        <Box sx={{ position: "absolute", right: 24, bottom: 120 }}>
            <Button
                variant="contained"
                onClick={() => setIsAttachModalOpen(true)}
                sx={{
                    minWidth: 50, width: 50, height: 50, borderRadius: 3, bgcolor: "#1E3A8A",
                    boxShadow: "0 10px 20px rgba(30,58,138,0.2)", "&:hover": { bgcolor: "#1E40AF" }
                }}
            >
                <UploadFileIcon />
            </Button>
        </Box>

        <Box sx={{ px: { xs: 2, md: 4 }, pb: { xs: 2, md: 4 }, pt: 1, bgcolor: "#F9FAFB" }}>
            <Composer
                disabled={isSubmitting}
                selectedFile={selectedFile}
                onClearFile={() => setSelectedFile(null)}
                onOpenAttach={() => setIsAttachModalOpen(true)}
                onSubmit={handleComposerSubmit}
            />
        </Box>
      </Box>

      {/* Legacy external components (history & attach) that use portals or absolute overlays. */}
      {/* Idealy we should also migrate these to MUI Dialogs */}
      <HistoryDrawer
        activeConversationId={activeConversationId}
        conversations={conversations}
        isLoading={isHistoryLoading}
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        onNewConversation={handleNewConversation}
        onSelectConversation={(conversationId) => {
          setError(null);
          setActiveConversationId(conversationId);
        }}
      />

      <AttachExerciseModal
        isOpen={isAttachModalOpen}
        selectedFile={selectedFile}
        onClose={() => setIsAttachModalOpen(false)}
        onSelectFile={(file) => {
          setSelectedFile(file);
          setIsAttachModalOpen(false);
        }}
      />
    </MainLayout>
  );
}
