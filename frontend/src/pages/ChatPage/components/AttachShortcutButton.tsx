import UploadFileIcon from "@mui/icons-material/UploadFile";
import { Box, Button } from "@mui/material";

interface AttachShortcutButtonProps {
  onClick: () => void;
}

export function AttachShortcutButton({ onClick }: AttachShortcutButtonProps) {
  return (
    <Box sx={{ position: "absolute", right: { xs: 24, md: 40 }, bottom: { xs: 24, md: 40 } }}>
      <Button
        variant="contained"
        onClick={onClick}
        sx={{
          minWidth: 56,
          width: 56,
          height: 56,
          borderRadius: 2,
          p: 0,
        }}
      >
        <UploadFileIcon />
      </Button>
    </Box>
  );
}
