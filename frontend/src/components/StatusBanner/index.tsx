import { Alert, Box } from "@mui/material";

interface StatusBannerProps {
  tone?: "info" | "error";
  message: string;
}

export function StatusBanner({ tone = "info", message }: StatusBannerProps) {
  return (
    <Box sx={{ p: 1 }}>
      <Alert
        severity={tone}
        variant="outlined"
        sx={{
          borderRadius: 3,
          bgcolor: tone === "error" ? "#FFF2F2" : "inherit",
          borderColor: tone === "error" ? "#F3D4D4" : "inherit",
          color: tone === "error" ? "#C84444" : "inherit",
          fontWeight: 600,
          "& .MuiAlert-icon": { color: "inherit" },
        }}
      >
        {message}
      </Alert>
    </Box>
  );
}
