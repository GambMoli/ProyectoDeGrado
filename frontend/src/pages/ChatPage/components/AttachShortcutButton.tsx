import UploadFileIcon from "@mui/icons-material/UploadFile";
import { Box, Button } from "@mui/material";

interface AttachShortcutButtonProps {
  onClick: () => void;
}

export function AttachShortcutButton({ onClick }: AttachShortcutButtonProps) {
  return (
    <Box sx={{ position: "absolute", right: 24, bottom: 120 }}>
      <Button
        variant="contained"
        onClick={onClick}
        sx={{
          minWidth: 50,
          width: 50,
          height: 50,
          borderRadius: 3,
          bgcolor: "#1E3A8A",
          boxShadow: "0 10px 20px rgba(30,58,138,0.2)",
          "&:hover": { bgcolor: "#1E40AF" },
        }}
      >
        <UploadFileIcon />
      </Button>
    </Box>
  );
}
