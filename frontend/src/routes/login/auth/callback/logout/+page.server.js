// src/routes/auth/logout/+page.server.js
import { redirect } from '@sveltejs/kit';
import { PUBLIC_API_BASE } from '$env/static/public';

const COOKIE_NAME = 'session';

/**
 * Logout handler.
 *
 * Steps:
 *   1. Read the current session token from the cookie
 *   2. Tell the Python backend to invalidate the server-side session (if any)
 *   3. Clear the cookie on the SvelteKit side
 *   4. Redirect to /login
 *
 * If Python doesn't have a logout endpoint yet, step 2 is skipped silently.
 *
 * @type {import('@sveltejs/kit').PageServerLoad}
 */
export async function load({ cookies, fetch }) {
  const token = cookies.get(COOKIE_NAME);

  // Tell Python to invalidate the session server-side.
  // This is best-effort — we clear the cookie regardless of the result.
  if (token) {
    try {
      await fetch(`${PUBLIC_API_BASE}/auth/logout`, {
        method:  'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type':  'application/json',
        },
      });
    } catch {
      // Backend unreachable — still clear the cookie locally
      console.warn('[auth/logout] Could not reach backend to invalidate session.');
    }
  }

  // Expire the cookie immediately
  cookies.delete(COOKIE_NAME, { path: '/' });

  throw redirect(303, '/login?reason=logged_out');
}