import ChatBubbleOutlineIcon from "@mui/icons-material/ChatBubbleOutline";
import { Box, Typography } from "@mui/material";

export function EmptyConversationState() {
  return (
    <Box sx={{ display: "flex", gap: 2, mb: 3 }}>
      <Box
        sx={{
          width: 40,
          height: 40,
          borderRadius: "50%",
          bgcolor: "#EFF6FF",
          color: "#1E3A8A",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexShrink: 0,
        }}
      >
        <ChatBubbleOutlineIcon fontSize="small" />
      </Box>

      <Box
        sx={{
          bgcolor: "#F3F4F6",
          color: "#1F2937",
          p: 2.5,
          borderRadius: 3,
          borderTopLeftRadius: 4,
          maxWidth: "75%",
        }}
      >
        <Typography variant="body2" sx={{ fontSize: "0.95rem" }}>
          Hola. Soy tu asistente de <strong>Cubik IA</strong>. Estoy listo para ayudarte con
          calculo, algebra, estadistica y otros ejercicios matematicos. Que problema resolvemos
          hoy?
        </Typography>
      </Box>
    </Box>
  );
}
