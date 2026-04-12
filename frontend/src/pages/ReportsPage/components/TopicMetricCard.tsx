import type { ReactNode } from "react";
import { Box, Card, CardContent, Stack, Typography } from "@mui/material";

import { textPrimary, textSecondary } from "../constants";

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
  helperColor = "#2E7D32",
  topIcon,
  bottomIcon,
}: TopicMetricCardProps) {
  return (
    <Card elevation={0} sx={{ height: "100%" }}>
      <CardContent sx={{ p: 3, "&:last-child": { pb: 3 } }}>
        <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 1.5 }}>
          <Typography sx={{ fontSize: 14, fontWeight: 600, color: textSecondary }}>{title}</Typography>
          <Box sx={{ color: "#1547A1", lineHeight: 1 }}>{topIcon}</Box>
        </Stack>
        <Typography sx={{ fontSize: 20, fontWeight: 800, color: textPrimary, mb: 1.25 }}>
          {value}
        </Typography>
        <Stack direction="row" spacing={0.75} alignItems="center">
          {bottomIcon ? <Box sx={{ color: helperColor, lineHeight: 1 }}>{bottomIcon}</Box> : null}
          <Typography sx={{ fontSize: 13, fontWeight: 600, color: helperColor }}>{helper}</Typography>
        </Stack>
      </CardContent>
    </Card>
  );
}
