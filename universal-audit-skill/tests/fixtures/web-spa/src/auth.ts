export function persistSession(token: string) {
  // token survives any XSS on this origin
  localStorage.setItem('session_token', token);
}

export function readTheme(): string | null {
  // NEGATIVE: non-sensitive value in localStorage is fine
  return localStorage.getItem('ui_theme');
}
