interface StatusBannerProps {
  tone?: "info" | "error";
  message: string;
}

export function StatusBanner({ tone = "info", message }: StatusBannerProps) {
  return <div className={`status-banner status-banner--${tone}`}>{message}</div>;
}
