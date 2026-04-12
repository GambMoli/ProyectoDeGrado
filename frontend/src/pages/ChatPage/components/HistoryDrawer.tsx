import AddIcon from "@mui/icons-material/Add";
import CloseIcon from "@mui/icons-material/Close";
import {
  Box,
  Button,
  CircularProgress,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Typography,
} from "@mui/material";

import type { ConversationSummary } from "../../../types/api";

interface HistoryDrawerProps {
  activeConversationId: string | null;
  conversations: ConversationSummary[];
  isLoading: boolean;
  isOpen: boolean;
  onClose: () => void;
  onNewConversation: () => void;
  onSelectConversation: (conversationId: string) => void;
}

export function HistoryDrawer({
  activeConversationId,
  conversations,
  isLoading,
  isOpen,
  onClose,
  onNewConversation,
  onSelectConversation,
}: HistoryDrawerProps) {
  return (
    <Drawer
      anchor="left"
      open={isOpen}
      onClose={onClose}
      variant="temporary"
      PaperProps={{
        sx: {
          width: 320,
          boxSizing: "border-box",
          bgcolor: "#fff",
          borderRight: "1px solid #E5E7EB",
        },
      }}
    >
      <Box sx={{ display: "flex", flexDirection: "column", height: "100%", p: 3 }}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, mb: 3 }}>
          <Button
            variant="contained"
            fullWidth
            onClick={onNewConversation}
            startIcon={<AddIcon />}
            sx={{
              bgcolor: "#1E3A8A",
              color: "#fff",
              borderRadius: "10px",
              textTransform: "none",
              fontWeight: 700,
              py: 1,
              boxShadow: "none",
              "&:hover": {
                bgcolor: "#1E40AF",
                boxShadow: "0 4px 12px rgba(30,58,138,0.2)",
              },
            }}
          >
            Nuevo chat
          </Button>
          <IconButton
            onClick={onClose}
            sx={{
              bgcolor: "#F3F4F6",
              color: "#6B7280",
              borderRadius: "10px",
              "&:hover": { bgcolor: "#E5E7EB" },
            }}
          >
            <CloseIcon fontSize="small" />
          </IconButton>
        </Box>

        <Box sx={{ flexGrow: 1, overflowY: "auto" }}>
          <Typography
            variant="overline"
            sx={{
              fontWeight: 800,
              color: "#9CA3AF",
              letterSpacing: "0.1em",
              mb: 2,
              display: "block",
            }}
          >
            Contenidos recientes
          </Typography>

          {isLoading ? (
            <Box sx={{ display: "flex", justifyContent: "center", mt: 4 }}>
              <CircularProgress size={24} sx={{ color: "#1E3A8A" }} />
            </Box>
          ) : conversations.length === 0 ? (
            <Typography
              variant="body2"
              sx={{ color: "#9CA3AF", textAlign: "center", mt: 4, px: 2 }}
            >
              Tus conversaciones apareceran aqui despues del primer mensaje.
            </Typography>
          ) : (
            <List disablePadding>
              {conversations.map((conversation) => (
                <ListItem key={conversation.id} disablePadding sx={{ mb: 1 }}>
                  <ListItemButton
                    selected={conversation.id === activeConversationId}
                    onClick={() => {
                      onSelectConversation(conversation.id);
                      onClose();
                    }}
                    sx={{
                      borderRadius: "8px",
                      py: 1.2,
                      px: 2,
                      bgcolor:
                        conversation.id === activeConversationId ? "#EFF6FF" : "transparent",
                      color:
                        conversation.id === activeConversationId ? "#1E3A8A" : "#4B5563",
                      "&.Mui-selected": {
                        bgcolor: "#EFF6FF",
                        color: "#1E3A8A",
                        "&:hover": { bgcolor: "#E0EFFF" },
                      },
                      "&:hover": { bgcolor: "#F3F4F6" },
                    }}
                  >
                    <Box
                      sx={{
                        mr: 1.5,
                        width: 10,
                        height: 10,
                        borderRadius: "2px",
                        border: "2px solid",
                        borderColor:
                          conversation.id === activeConversationId ? "#1E3A8A" : "#D1D5DB",
                        bgcolor:
                          conversation.id === activeConversationId ? "#1E3A8A" : "transparent",
                      }}
                    />
                    <ListItemText
                      primary={conversation.title}
                      primaryTypographyProps={{
                        fontSize: "0.875rem",
                        fontWeight: conversation.id === activeConversationId ? 700 : 600,
                        noWrap: true,
                      }}
                    />
                  </ListItemButton>
                </ListItem>
              ))}
            </List>
          )}
        </Box>
      </Box>
    </Drawer>
  );
}
