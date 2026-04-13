import type { ReactNode } from "react";
import { Avatar, Box, Card, CardContent, Stack, Typography } from "@mui/material";


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
    <Card elevation={0} sx={{ height: "100%" }}>
      <CardContent sx={{ p: 3, "&:last-child": { pb: 3 } }}>
        <Stack direction="row" spacing={2} alignItems="center">
          <Avatar sx={{ bgcolor: iconBg, color: iconColor, width: 48, height: 48 }}>{icon}</Avatar>
          <Box>
            <Typography sx={{ fontSize: 14, fontWeight: 600, color: "text.secondary" }}>{label}</Typography>
            <Stack direction="row" spacing={0.75} alignItems="baseline">
              <Typography sx={{ fontSize: 24, fontWeight: 800, color: "text.primary" }}>{value}</Typography>
              {suffix ? (
                <Typography sx={{ fontSize: 14, fontWeight: 600, color: "text.secondary" }}>
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
