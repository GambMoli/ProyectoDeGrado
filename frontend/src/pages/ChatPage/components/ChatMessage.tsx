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
      }}
    >
      <Avatar
        sx={{
          width: 40,
          height: 40,
          bgcolor: isAssistantLike ? "primary.light" : "background.paper",
          color: isAssistantLike ? "primary.main" : "text.secondary",
          border: "1px solid",
          borderColor: "divider",
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
          maxWidth: { xs: "100%", md: "78%" },
        }}
      >
        {shouldShowBody ? (
          <Paper
            sx={{
              bgcolor: isAssistantLike ? "background.paper" : "primary.main",
              color: isAssistantLike ? "text.primary" : "#FFFFFF",
              p: 2.5,
              borderTopLeftRadius: isAssistantLike ? 2 : 8,
              borderTopRightRadius: isAssistantLike ? 8 : 2,
              borderColor: isAssistantLike ? "divider" : "primary.main",
            }}
          >
            <MathContent content={message.content} />
          </Paper>
        ) : null}

        {resolution ? (
          <Paper
            sx={{
              p: 3,
              width: "100%",
              bgcolor: "background.paper",
            }}
          >
            <Typography variant="subtitle1" sx={{ color: "primary.main", mb: 2 }}>
              Resolucion paso a paso
            </Typography>

            <Box
              component="ol"
              sx={{
                m: 0,
                pl: 2.5,
                display: "grid",
                gap: 1.5,
                color: "text.primary",
                fontSize: "0.95rem",
              }}
            >
              {resolution.steps.map((step, index) => (
                <li key={`${step}-${index}`}>
                  <MathContent content={step} />
                </li>
              ))}
            </Box>

            <Paper
              sx={{
                my: 2.5,
                p: 2.5,
                bgcolor: "background.default",
              }}
            >
              <Typography variant="caption" sx={{ fontWeight: 800, color: "text.secondary", display: "block", mb: 1 }}>
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
              <Typography variant="caption" sx={{ fontWeight: 800, color: "text.secondary", display: "block", mb: 1, mt: 2 }}>
                Resultado
              </Typography>
              <MathFormula
                expression={resolution.final_result}
                displayMode
                source="plain"
                style={{ overflowX: "auto" }}
              />
            </Paper>

            <Box sx={{ color: "text.secondary", fontSize: "0.94rem" }}>
              <MathContent content={resolution.explanation} />
            </Box>

            {exercise?.error_message ? (
              <Typography sx={{ color: "error.main", mt: 2, fontSize: "0.9rem", fontWeight: 600 }}>
                {exercise.error_message}
              </Typography>
            ) : null}
          </Paper>
        ) : null}
      </Box>
    </Box>
  );
}
