import { useEffect, useMemo, useState } from "react";

import {
  getConversation,
  getConversations,
  sendChatMessage,
  uploadExerciseImage,
} from "../../../api/client";
import { useAuth } from "../../../context";
import type { ConversationDetail, ConversationSummary, Message } from "../../../types/api";

export function useChatPage({ startNew = false } = {}) {
  const { user } = useAuth();
  const conversationStorageKey = useMemo(
    () => (user ? `calc-tutor-conversation-id:${user.id}` : "calc-tutor-conversation-id"),
    [user],
  );

  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(
    () => (startNew ? null : localStorage.getItem(conversationStorageKey)),
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

      if (items.length > 0 && !activeConversationId && !startNew) {
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

  async function loadConversation(conversationId: string, silent = false) {
    if (!silent) setIsConversationLoading(true);
    try {
      const detail = await getConversation(conversationId);
      setActiveConversation(detail);
    } catch (nextError) {
      const message =
        nextError instanceof Error ? nextError.message : "No se pudo cargar la conversacion.";
      setError(message);
    } finally {
      if (!silent) setIsConversationLoading(false);
    }
  }

  async function handleComposerSubmit(message: string) {
    setError(null);
    setIsSubmitting(true);

    const optimisticMessage: Message = {
      id: `optimistic-${Date.now()}`,
      role: "user",
      content: message || (selectedFile ? selectedFile.name : ""),
      source_type: selectedFile ? "image" : "text",
      status: "received",
      error_message: null,
      created_at: new Date().toISOString(),
      exercise: null,
    };

    setActiveConversation((prev) => {
      if (prev) {
        return { ...prev, messages: [...prev.messages, optimisticMessage] };
      }
      const now = new Date().toISOString();
      return {
        id: "optimistic",
        user_id: "",
        title: "",
        summary: null,
        created_at: now,
        updated_at: now,
        messages: [optimisticMessage],
      };
    });

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
      await loadConversation(response.conversation_id, true);
      await refreshConversations(response.conversation_id);
    } catch (nextError) {
      const errorMessage =
        nextError instanceof Error ? nextError.message : "No se pudo enviar el mensaje.";
      setActiveConversation((prev) =>
        prev
          ? { ...prev, messages: prev.messages.filter((m) => m.id !== optimisticMessage.id) }
          : prev,
      );
      setError(errorMessage);
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
