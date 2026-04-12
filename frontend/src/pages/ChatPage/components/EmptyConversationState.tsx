import ChatBubbleOutlineIcon from "@mui/icons-material/ChatBubbleOutline";
import { Box, Paper, Typography } from "@mui/material";

export function EmptyConversationState() {
  return (
    <Paper
      sx={{
        p: { xs: 3, md: 4 },
        display: "flex",
        gap: 2,
        alignItems: "flex-start",
        bgcolor: "background.paper",
      }}
    >
      <Box
        sx={{
          width: 44,
          height: 44,
          borderRadius: 2,
          bgcolor: "primary.light",
          color: "primary.main",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexShrink: 0,
        }}
      >
        <ChatBubbleOutlineIcon fontSize="small" />
      </Box>

      <Box sx={{ maxWidth: 720 }}>
        <Typography variant="h6" sx={{ mb: 1, color: "text.primary" }}>
          Bienvenido a Cubik IA
        </Typography>
        <Typography variant="body2" sx={{ color: "text.secondary" }}>
          Estoy listo para ayudarte con calculo, algebra, estadistica y otros ejercicios matematicos.
          Puedes escribir una pregunta, insertar una formula o adjuntar una imagen del ejercicio.
        </Typography>
      </Box>
    </Paper>
  );
}
