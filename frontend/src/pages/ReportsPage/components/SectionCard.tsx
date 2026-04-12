import type { ReactNode } from "react";
import { Paper } from "@mui/material";
import type { SxProps, Theme } from "@mui/material/styles";

import { cardBorder } from "../constants";

interface SectionCardProps {
  children: ReactNode;
  sx?: SxProps<Theme>;
}

export function SectionCard({ children, sx }: SectionCardProps) {
  return (
    <Paper
      elevation={0}
      sx={{
        borderRadius: "20px",
        border: `1px solid ${cardBorder}`,
        bgcolor: "#FFFFFF",
        boxShadow: "0 1px 3px rgba(15, 23, 42, 0.05)",
        ...sx,
      }}
    >
      {children}
    </Paper>
  );
}
