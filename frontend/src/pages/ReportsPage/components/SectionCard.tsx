import type { ReactNode } from "react";
import { Paper } from "@mui/material";
import type { SxProps, Theme } from "@mui/material/styles";

interface SectionCardProps {
  children: ReactNode;
  sx?: SxProps<Theme>;
}

export function SectionCard({ children, sx }: SectionCardProps) {
  return (
    <Paper
      elevation={0}
      sx={{
        borderRadius: 2,
        bgcolor: "#FFFFFF",
        ...sx,
      }}
    >
      {children}
    </Paper>
  );
}
