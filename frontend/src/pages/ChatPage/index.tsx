import { Box, Paper, Typography } from "@mui/material";

import { StatusBanner } from "../../components";
import { MainLayout } from "../../layouts/MainLayout";
import { AttachExerciseModal } from "./components/AttachExerciseModal";
import { AttachShortcutButton } from "./components/AttachShortcutButton";
import { ChatMessage } from "./components/ChatMessage";
import { Composer } from "./components/Composer";
import { EmptyConversationState } from "./components/EmptyConversationState";
import { HistoryDrawer } from "./components/HistoryDrawer";
import { useChatPage } from "./hooks/useChatPage";

export function ChatPage() {
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
  } = useChatPage();

  return (
    <MainLayout onOpenHistory={openHistory} onOpenAttach={openAttachModal}>
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
            sx={{
              px: { xs: 3, md: 4 },
              py: 2.5,
              borderBottom: "1px solid",
              borderColor: "divider",
              bgcolor: "background.paper",
            }}
          >
            <Typography variant="overline" sx={{ color: "primary.main", fontWeight: 800, letterSpacing: "0.12em" }}>
              Cubik IA
            </Typography>
            <Typography variant="h6" sx={{ color: "text.primary" }}>
              Espacio de Conversacion
            </Typography>
            <Typography variant="body2" sx={{ color: "text.secondary", maxWidth: 760 }}>
              Resuelve ejercicios, adjunta imagenes y revisa formulas con una interfaz mas limpia y academica.
            </Typography>
          </Box>

          <Box
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
              selectedFile={selectedFile}
              onClearFile={clearSelectedFile}
              onOpenAttach={openAttachModal}
              onSubmit={handleComposerSubmit}
            />
          </Box>
        </Paper>

        <AttachShortcutButton onClick={openAttachModal} />
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
