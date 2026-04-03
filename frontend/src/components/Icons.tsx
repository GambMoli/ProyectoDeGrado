interface IconProps {
  className?: string;
}

export function BrandIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <rect x="4" y="5" width="16" height="14" rx="3" stroke="currentColor" strokeWidth="1.8" />
      <path d="M9 9H15" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <path d="M9 13H15" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <path d="M12 8V16" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

export function MenuIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <path d="M5 8H19" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" />
      <path d="M5 12H19" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" />
      <path d="M5 16H15" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" />
    </svg>
  );
}

export function ChatIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <path
        d="M7 7.5H17C18.1 7.5 19 8.4 19 9.5V15.5C19 16.6 18.1 17.5 17 17.5H11L7 20V17.5C5.9 17.5 5 16.6 5 15.5V9.5C5 8.4 5.9 7.5 7 7.5Z"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function HistoryIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <path d="M5 12A7 7 0 1 0 8 6.3" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
      <path d="M5 5V9H9" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M12 8.5V12L14.8 13.7" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
    </svg>
  );
}

export function ExerciseIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <path d="M9 6L15 18" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
      <path d="M7 8H11" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
      <path d="M13 16H17" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
      <path d="M8 18H16" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
    </svg>
  );
}

export function SettingsIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <path
        d="M12 8.5A3.5 3.5 0 1 1 12 15.5A3.5 3.5 0 0 1 12 8.5Z"
        stroke="currentColor"
        strokeWidth="1.7"
      />
      <path
        d="M19 13.2V10.8L16.8 10.2C16.6 9.7 16.4 9.2 16.1 8.8L17.2 6.8L15.2 4.8L13.2 5.9C12.8 5.6 12.3 5.4 11.8 5.2L11.2 3H8.8L8.2 5.2C7.7 5.4 7.2 5.6 6.8 5.9L4.8 4.8L2.8 6.8L3.9 8.8C3.6 9.2 3.4 9.7 3.2 10.2L1 10.8V13.2L3.2 13.8C3.4 14.3 3.6 14.8 3.9 15.2L2.8 17.2L4.8 19.2L6.8 18.1C7.2 18.4 7.7 18.6 8.2 18.8L8.8 21H11.2L11.8 18.8C12.3 18.6 12.8 18.4 13.2 18.1L15.2 19.2L17.2 17.2L16.1 15.2C16.4 14.8 16.6 14.3 16.8 13.8L19 13.2Z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function PlusIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <path d="M12 6V18" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" />
      <path d="M6 12H18" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" />
    </svg>
  );
}

export function UploadIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <path d="M12 16V7" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <path d="M8.5 10.5L12 7L15.5 10.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
      <path
        d="M7 18.5H17C18.1 18.5 19 17.6 19 16.5V15.8C19 14.7 18.1 13.8 17 13.8H16.3C16 10.7 14.5 9 12 9C9.5 9 8 10.7 7.7 13.8H7C5.9 13.8 5 14.7 5 15.8V16.5C5 17.6 5.9 18.5 7 18.5Z"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function CameraIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <path
        d="M7.5 7.5L8.5 5.5H15.5L16.5 7.5H18C19.1 7.5 20 8.4 20 9.5V17C20 18.1 19.1 19 18 19H6C4.9 19 4 18.1 4 17V9.5C4 8.4 4.9 7.5 6 7.5H7.5Z"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinejoin="round"
      />
      <circle cx="12" cy="13" r="3.2" stroke="currentColor" strokeWidth="1.7" />
    </svg>
  );
}

export function FormulaIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <path d="M6 7H18" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <path d="M8.5 7L15.5 17" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <path d="M6 17H18" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

export function AttachmentIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <path
        d="M9.5 12.5L13.9 8.1C15.1 6.9 17 6.9 18.2 8.1C19.4 9.3 19.4 11.2 18.2 12.4L11.5 19.1C9.8 20.8 7 20.8 5.3 19.1C3.6 17.4 3.6 14.6 5.3 12.9L12.1 6.1"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function SendIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <path
        d="M5 12L19 5L15.5 12L19 19L5 12Z"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function UserAvatarIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <circle cx="12" cy="8.5" r="3.1" stroke="currentColor" strokeWidth="1.7" />
      <path
        d="M6.5 18C7.5 15.7 9.5 14.5 12 14.5C14.5 14.5 16.5 15.7 17.5 18"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinecap="round"
      />
    </svg>
  );
}

export function BotAvatarIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <rect x="6" y="8" width="12" height="9" rx="3" stroke="currentColor" strokeWidth="1.7" />
      <path d="M12 5.5V8" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
      <circle cx="10" cy="12.5" r="0.85" fill="currentColor" />
      <circle cx="14" cy="12.5" r="0.85" fill="currentColor" />
      <path d="M10 15H14" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
    </svg>
  );
}

export function CloseIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <path d="M7 7L17 17" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <path d="M17 7L7 17" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

export function InfoIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <circle cx="12" cy="12" r="8" stroke="currentColor" strokeWidth="1.7" />
      <path d="M12 10V15" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
      <circle cx="12" cy="7.5" r="1" fill="currentColor" />
    </svg>
  );
}
