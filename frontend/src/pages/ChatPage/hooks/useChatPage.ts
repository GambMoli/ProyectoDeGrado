import { useEffect, useMemo, useState } from "react";

import {
  getConversation,
  getConversations,
  sendChatMessage,
  uploadExerciseImage,
} from "../../../api/client";
import { useAuth } from "../../../context";
import type { ConversationDetail, ConversationSummary } from "../../../types/api";

export function useChatPage() {
  const { user } = useAuth();
  const conversationStorageKey = useMemo(
    () => (user ? `calc-tutor-conversation-id:${user.id}` : "calc-tutor-conversation-id"),
    [user],
  );

  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(
    () => localStorage.getItem(conversationStorageKey),
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
    if (activeConversationId) {
      localStorage.setItem(conversationStorageKey, activeConversationId);
      return;
    }
    localStorage.removeItem(conversationStorageKey);
  }, [activeConversationId, conversationStorageKey]);

  useEffect(() => {
    setActiveConversationId(localStorage.getItem(conversationStorageKey));
  }, [conversationStorageKey]);

  useEffect(() => {
    void refreshConversations();
  }, [user?.id]);

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
      const items = await getConversations();
      setConversations(items);

      if (preferredConversationId) {
        setActiveConversationId(preferredConversationId);
        return;
      }

      if (items.length > 0 && !activeConversationId) {
        setActiveConversationId(items[0].id);
        return;
      }

      if (
        activeConversationId &&
        !items.some((conversation) => conversation.id === activeConversationId)
      ) {
        setActiveConversationId(items[0]?.id ?? null);
      }
    } catch (nextError) {
      const message =
        nextError instanceof Error ? nextError.message : "No se pudo cargar el historial.";
      setError(message);
    } finally {
      setIsHistoryLoading(false);
    }
  }

  async function loadConversation(conversationId: string) {
    setIsConversationLoading(true);
    try {
      const detail = await getConversation(conversationId);
      setActiveConversation(detail);
    } catch (nextError) {
      const message =
        nextError instanceof Error ? nextError.message : "No se pudo cargar la conversacion.";
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
            conversationId: activeConversationId,
            prompt: message,
          })
        : await sendChatMessage({
            conversation_id: activeConversationId,
            message,
          });

      setSelectedFile(null);
      await loadConversation(response.conversation_id);
      await refreshConversations(response.conversation_id);
    } catch (nextError) {
      const message =
        nextError instanceof Error ? nextError.message : "No se pudo enviar el mensaje.";
      setError(message);
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

  function handleSelectConversation(conversationId: string) {
    setError(null);
    setActiveConversationId(conversationId);
  }

  return {
    activeConversation,
    activeConversationId,
    conversations,
    error,
    hasMessages: Boolean(activeConversation && activeConversation.messages.length > 0),
    isAttachModalOpen,
    isConversationLoading,
    isHistoryLoading,
    isHistoryOpen,
    isSubmitting,
    selectedFile,
    clearError: () => setError(null),
    clearSelectedFile: () => setSelectedFile(null),
    closeAttachModal: () => setIsAttachModalOpen(false),
    closeHistory: () => setIsHistoryOpen(false),
    handleComposerSubmit,
    handleNewConversation,
    handleSelectConversation,
    openAttachModal: () => setIsAttachModalOpen(true),
    openHistory: () => setIsHistoryOpen(true),
    setSelectedFile,
  };
}
