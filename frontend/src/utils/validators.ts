export function isValidEmail(value: string): boolean {
  const normalized = value.trim();
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(normalized);
}

export function matchesPasswordStandard(value: string): boolean {
  const normalized = value.trim();
  return (
    normalized.length >= 8 &&
    /[A-Z]/.test(normalized) &&
    /[a-z]/.test(normalized) &&
    /\d/.test(normalized) &&
    /[^A-Za-z0-9]/.test(normalized)
  );
}
