import type { ReactNode } from "react";
import { Avatar, Box, Card, CardContent, Stack, Typography } from "@mui/material";

import { textPrimary, textSecondary } from "../constants";

interface StudentMetricCardProps {
  icon: ReactNode;
  iconBg: string;
  iconColor: string;
  label: string;
  value: string;
  suffix?: string;
}

export function StudentMetricCard({
  icon,
  iconBg,
  iconColor,
  label,
  value,
  suffix,
}: StudentMetricCardProps) {
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
      <CardContent sx={{ p: 2.5, "&:last-child": { pb: 2.5 } }}>
        <Stack direction="row" spacing={2} alignItems="center">
          <Avatar sx={{ bgcolor: iconBg, color: iconColor, width: 50, height: 50 }}>{icon}</Avatar>
          <Box>
            <Typography sx={{ fontSize: 14, fontWeight: 500, color: "#52627A" }}>{label}</Typography>
            <Stack direction="row" spacing={0.75} alignItems="baseline">
              <Typography sx={{ fontSize: 22, fontWeight: 800, color: textPrimary }}>{value}</Typography>
              {suffix ? (
                <Typography sx={{ fontSize: 14, fontWeight: 500, color: textSecondary }}>
                  {suffix}
                </Typography>
              ) : null}
            </Stack>
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );
}
