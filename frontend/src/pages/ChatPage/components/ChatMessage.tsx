import { Avatar, Box, Paper, Typography } from "@mui/material";

import { BotAvatarIcon, MathContent, MathFormula, UserAvatarIcon } from "../../../components";
import type { Message } from "../../../types/api";

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isAssistantLike = message.role !== "user";
  const exercise = isAssistantLike ? message.exercise : null;
  const resolution = exercise?.resolution ?? null;
  const shouldShowBody = !isAssistantLike || !resolution || message.content.trim().length < 180;

  return (
    <Box
      sx={{
        display: "flex",
        alignItems: "flex-start",
        gap: 2,
        flexDirection: isAssistantLike ? "row" : "row-reverse",
        mb: 3,
      }}
    >
      <Avatar
        sx={{
          width: 32,
          height: 32,
          bgcolor: isAssistantLike ? "#EDF3FD" : "#F3F5F8",
          color: isAssistantLike ? "#2154B6" : "#7C889D",
          border: "1px solid #DFE8F7",
        }}
      >
        {isAssistantLike ? (
          <BotAvatarIcon style={{ width: 16 }} />
        ) : (
          <UserAvatarIcon style={{ width: 16 }} />
        )}
      </Avatar>

      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          gap: 1.5,
          alignItems: isAssistantLike ? "flex-start" : "flex-end",
          maxWidth: { xs: "90%", md: "75%" },
        }}
      >
        {shouldShowBody ? (
          <Paper
            elevation={0}
            sx={{
              bgcolor: isAssistantLike ? "#F3F6FB" : "#1F56BE",
              color: isAssistantLike ? "#19315E" : "#FFF",
              p: 2,
              borderRadius: 3,
              borderTopLeftRadius: isAssistantLike ? "4px" : "24px",
              borderTopRightRadius: isAssistantLike ? "24px" : "4px",
              border: isAssistantLike ? "1px solid #E4EAF3" : "none",
              boxShadow: "0 10px 24px rgba(64,97,161,0.08)",
            }}
          >
            <MathContent content={message.content} />
          </Paper>
        ) : null}

        {resolution ? (
          <Paper
            elevation={0}
            sx={{
              p: 3,
              borderRadius: 3,
              bgcolor: "#F3F6FB",
              border: "1px solid #E2E9F3",
              color: "#19315E",
              width: "100%",
              boxShadow: "0 10px 24px rgba(64,97,161,0.08)",
            }}
          >
            <Typography variant="subtitle1" sx={{ fontWeight: 800, color: "#2154B6", mb: 2 }}>
              Resolucion paso a paso:
            </Typography>

            <Box
              component="ol"
              sx={{
                m: 0,
                pl: 2,
                display: "grid",
                gap: 1.5,
                color: "#19315E",
                fontSize: "0.93rem",
              }}
            >
              {resolution.steps.map((step, index) => (
                <li key={`${step}-${index}`}>
                  <MathContent content={step} />
                </li>
              ))}
            </Box>

            <Box
              sx={{
                my: 2,
                p: 2,
                borderRadius: 2,
                bgcolor: "#FFF",
                border: "1px solid #E2E8F1",
                display: "flex",
                flexDirection: "column",
                gap: 1,
              }}
            >
              <Typography variant="caption" sx={{ fontWeight: 700, color: "#5C6F93" }}>
                Expresion interpretada
              </Typography>
              {exercise?.extracted_expression ? (
                <MathFormula
                  expression={exercise.extracted_expression}
                  displayMode
                  source="plain"
                  style={{ overflowX: "auto" }}
                />
              ) : null}
              <Typography variant="caption" sx={{ fontWeight: 700, color: "#5C6F93", mt: 1 }}>
                Resultado
              </Typography>
              <MathFormula
                expression={resolution.final_result}
                displayMode
                source="plain"
                style={{ overflowX: "auto" }}
              />
            </Box>

            <Box sx={{ color: "#5C6F93", fontSize: "0.92rem" }}>
              <MathContent content={resolution.explanation} />
            </Box>

            {exercise?.error_message ? (
              <Typography sx={{ color: "#C84444", mt: 2, fontSize: "0.9rem" }}>
                {exercise.error_message}
              </Typography>
            ) : null}
          </Paper>
        ) : null}
      </Box>
    </Box>
  );
}
