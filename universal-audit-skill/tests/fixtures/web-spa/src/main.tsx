import { Comment } from './Comment';
import { persistSession } from './auth';

const params = new URLSearchParams(window.location.search);
export function boot(token: string) {
  persistSession(token);
  return Comment({ raw: params.get('c') ?? '' });
}
