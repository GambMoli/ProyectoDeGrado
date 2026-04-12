import type { ReactNode } from "react";
import { Box, Card, CardContent, Stack, Typography } from "@mui/material";

import { textPrimary } from "../constants";

interface TopicMetricCardProps {
  title: string;
  value: string;
  helper: string;
  helperColor?: string;
  topIcon: ReactNode;
  bottomIcon?: ReactNode;
}

export function TopicMetricCard({
  title,
  value,
  helper,
  helperColor = "#16A34A",
  topIcon,
  bottomIcon,
}: TopicMetricCardProps) {
  return (
    <Card
      elevation={0}
      sx={{
        borderRadius: "18px",
        border: "1px solid #DCE5F3",
        boxShadow: "none",
        height: "100%",
      }}
    >
      <CardContent sx={{ p: 2.25, "&:last-child": { pb: 2.25 } }}>
        <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 1.5 }}>
          <Typography sx={{ fontSize: 14, fontWeight: 500, color: "#52627A" }}>{title}</Typography>
          <Box sx={{ color: "#647BFF", lineHeight: 1 }}>{topIcon}</Box>
        </Stack>
        <Typography sx={{ fontSize: 18, fontWeight: 800, color: textPrimary, mb: 1.25 }}>
          {value}
        </Typography>
        <Stack direction="row" spacing={0.75} alignItems="center">
          {bottomIcon ? <Box sx={{ color: helperColor, lineHeight: 1 }}>{bottomIcon}</Box> : null}
          <Typography sx={{ fontSize: 13, fontWeight: 500, color: helperColor }}>{helper}</Typography>
        </Stack>
      </CardContent>
    </Card>
  );
}
