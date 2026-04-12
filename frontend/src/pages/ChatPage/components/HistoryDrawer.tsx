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
          bgcolor: "background.paper",
        },
      }}
    >
      <Box sx={{ display: "flex", flexDirection: "column", height: "100%", p: 3 }}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, mb: 3 }}>
          <Button variant="contained" fullWidth onClick={onNewConversation} startIcon={<AddIcon />}>
            Nuevo chat
          </Button>
          <IconButton
            onClick={onClose}
            sx={{
              borderRadius: 2,
              border: "1px solid",
              borderColor: "divider",
              bgcolor: "background.default",
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
              color: "text.secondary",
              letterSpacing: "0.12em",
              mb: 2,
              display: "block",
            }}
          >
            Conversaciones recientes
          </Typography>

          {isLoading ? (
            <Box sx={{ display: "flex", justifyContent: "center", mt: 4 }}>
              <CircularProgress size={24} color="primary" />
            </Box>
          ) : conversations.length === 0 ? (
            <Typography variant="body2" sx={{ color: "text.secondary", textAlign: "center", mt: 4, px: 2 }}>
              Tus conversaciones apareceran aqui despues del primer mensaje.
            </Typography>
          ) : (
            <List disablePadding sx={{ display: "grid", gap: 1 }}>
              {conversations.map((conversation) => (
                <ListItem key={conversation.id} disablePadding>
                  <ListItemButton
                    selected={conversation.id === activeConversationId}
                    onClick={() => {
                      onSelectConversation(conversation.id);
                      onClose();
                    }}
                    sx={{
                      borderRadius: 2,
                      py: 1.25,
                      px: 1.5,
                      alignItems: "flex-start",
                      bgcolor: conversation.id === activeConversationId ? "primary.light" : "transparent",
                      color: conversation.id === activeConversationId ? "primary.main" : "text.secondary",
                      "&.Mui-selected": {
                        bgcolor: "primary.light",
                        color: "primary.main",
                        "&:hover": { bgcolor: "primary.light" },
                      },
                      "&:hover": { bgcolor: "background.default" },
                    }}
                  >
                    <ListItemText
                      primary={conversation.title}
                      primaryTypographyProps={{
                        fontSize: "0.95rem",
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
