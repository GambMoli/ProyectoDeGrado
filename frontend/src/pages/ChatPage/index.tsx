import { Box, Paper, Typography } from "@mui/material";
import { useEffect, useRef } from "react";
import { useLocation } from "react-router-dom";

import { StatusBanner } from "../../components";
import { MainLayout } from "../../layouts/MainLayout";
import { AttachExerciseModal } from "./components/AttachExerciseModal";
import { ChatMessage } from "./components/ChatMessage";
import { Composer } from "./components/Composer";
import { EmptyConversationState } from "./components/EmptyConversationState";
import { HistoryDrawer } from "./components/HistoryDrawer";
import { useChatPage } from "./hooks/useChatPage";

export function ChatPage() {
  const location = useLocation();
  const startNew = Boolean(location.state?.newConversation);
  const {
    activeConversation,
    activeConversationId,
    conversations,
    error,
    hasMessages,
    isAttachModalOpen,
    isConversationLoading,
    isHistoryLoading,
    isHistoryOpen,
    isSubmitting,
    selectedFile,
    clearSelectedFile,
    closeAttachModal,
    closeHistory,
    handleComposerSubmit,
    handleNewConversation,
    handleSelectConversation,
    openAttachModal,
    openHistory,
    setSelectedFile,
  } = useChatPage({ startNew });

  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const previousConversationIdRef = useRef<string | null>(null);
  const previousLastMessageIdRef = useRef<string | null>(null);
  const wasSubmittingRef = useRef(false);

  const lastMessageId =
    activeConversation && activeConversation.messages.length > 0
      ? activeConversation.messages[activeConversation.messages.length - 1].id
      : null;
  const openFormulaPanelTrigger = location.state?.openFormulaPanel ? location.key : undefined;

  function scrollToBottom(behavior: ScrollBehavior = "smooth") {
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        messagesEndRef.current?.scrollIntoView({ behavior, block: "end" });
      });
    });
  }

  useEffect(() => {
    if (isConversationLoading) {
      return;
    }

    const conversationChanged = previousConversationIdRef.current !== activeConversation?.id;
    const lastMessageChanged = previousLastMessageIdRef.current !== lastMessageId;

    if (conversationChanged) {
      scrollToBottom("instant");
    } else if (lastMessageChanged) {
      scrollToBottom("smooth");
    }

    previousConversationIdRef.current = activeConversation?.id ?? null;
    previousLastMessageIdRef.current = lastMessageId;
  }, [activeConversation?.id, isConversationLoading, lastMessageId]);

  useEffect(() => {
    if (wasSubmittingRef.current && !isSubmitting) {
      scrollToBottom("smooth");
    }
    wasSubmittingRef.current = isSubmitting;
  }, [isSubmitting]);

  return (
    <MainLayout onOpenHistory={openHistory} onOpenAttach={openAttachModal} onNewChat={handleNewConversation}>
      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          height: "100%",
          position: "relative",
          px: { xs: 2, md: 4 },
          py: { xs: 2, md: 3 },
          gap: 2,
          bgcolor: "background.default",
        }}
      >
        {error ? <StatusBanner tone="error" message={error} /> : null}

        <Paper
          sx={{
            flexGrow: 1,
            minHeight: 0,
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
            bgcolor: "background.paper",
          }}
        >
              <Box
                ref={messagesContainerRef}
                sx={{
                  flexGrow: 1,
                  overflowY: "auto",
                  px: { xs: 2, md: 4 },
                  py: 3,
                  display: "flex",
                  flexDirection: "column",
              gap: 3,
              bgcolor: "background.default",
            }}
          >
            {isConversationLoading ? (
              <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center", flexGrow: 1 }}>
                <Typography variant="body2" sx={{ color: "text.secondary", fontWeight: 600 }}>
                  Cargando conversacion...
                </Typography>
              </Box>
            ) : (
              <>
                {!hasMessages ? <EmptyConversationState /> : null}
                {activeConversation?.messages.map((message) => (
                  <ChatMessage key={message.id} message={message} />
                ))}
                <Box ref={messagesEndRef} sx={{ height: 1 }} />
              </>
            )}
          </Box>

          <Box
            sx={{
              px: { xs: 2, md: 4 },
              pb: { xs: 2, md: 3 },
              pt: 2,
              borderTop: "1px solid",
              borderColor: "divider",
              bgcolor: "background.paper",
            }}
          >
            <Composer
              disabled={isSubmitting}
              openFormulaPanelTrigger={openFormulaPanelTrigger}
              selectedFile={selectedFile}
              onClearFile={clearSelectedFile}
              onOpenAttach={openAttachModal}
              onSubmit={handleComposerSubmit}
            />
          </Box>
        </Paper>

      </Box>

      <HistoryDrawer
        activeConversationId={activeConversationId}
        conversations={conversations}
        isLoading={isHistoryLoading}
        isOpen={isHistoryOpen}
        onClose={closeHistory}
        onNewConversation={handleNewConversation}
        onSelectConversation={handleSelectConversation}
      />

      <AttachExerciseModal
        isOpen={isAttachModalOpen}
        selectedFile={selectedFile}
        onClose={closeAttachModal}
        onSelectFile={(file) => {
          setSelectedFile(file);
          closeAttachModal();
        }}
      />
    </MainLayout>
  );
}
