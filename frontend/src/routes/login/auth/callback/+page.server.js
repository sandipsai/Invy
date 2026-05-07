// src/routes/auth/callback/+page.server.js
import { redirect, error } from '@sveltejs/kit';

/**
 * OAuth Callback Handler
 * ─────────────────────
 * Flow:
 *   1. User clicks "Continue with Google" on /login
 *   2. Browser goes to Python backend → GET /auth/google/login
 *   3. Python redirects to Google consent screen
 *   4. Google redirects back to Python → GET /auth/google/callback
 *   5. Python validates the code, creates a session, then redirects to:
 *      http://localhost:5173/auth/callback?token=<jwt_or_session_id>
 *   6. THIS handler reads the token, stores it as a cookie, redirects to /dashboard
 *
 * Two auth token strategies supported — set whichever Python sends:
 *
 *   A) JWT in query param   → ?token=eyJ...
 *      Store as HttpOnly cookie, send on every API request as Authorization header.
 *
 *   B) Session ID in query param → ?session=abc123
 *      Python already set a server-side session; just echo the ID in a cookie
 *      so hooks.server.js can forward it on API requests.
 *
 * The query param name (?token vs ?session) is whatever your Python
 * backend sends — update PARAM_NAME below to match.
 *
 * @type {import('@sveltejs/kit').PageServerLoad}
 */

const PARAM_NAME    = 'token';   // change to 'session' if Python sends a session ID
const COOKIE_NAME   = 'session'; // must match hooks.server.js and login/+page.server.js
const COOKIE_MAX_AGE = 60 * 60 * 24 * 7; // 7 days in seconds

export async function load({ url, cookies }) {
  const token = url.searchParams.get(PARAM_NAME);

  // No token — could be an error callback from the provider
  if (!token) {
    const oauthError = url.searchParams.get('error');
    const description = url.searchParams.get('error_description');
    console.error('[auth/callback] OAuth error:', oauthError, description);
    throw error(401, oauthError ?? 'Authentication failed. No token received.');
  }

  // Store the token as a secure HttpOnly cookie.
  // The browser never reads this directly — SvelteKit's server-side
  // load functions forward it on every API request via hooks.server.js.
  cookies.set(COOKIE_NAME, token, {
    path:     '/',
    httpOnly: true,          // JS can't read it — XSS protection
    secure:   process.env.NODE_ENV === 'production', // HTTPS only in prod
    sameSite: 'lax',         // sent on same-site navigations + top-level cross-site GET
    maxAge:   COOKIE_MAX_AGE,
  });

  // Send to the page they originally wanted, or fall back to dashboard
  const returnTo = url.searchParams.get('returnTo') ?? '/dashboard';

  // Safety: only allow relative return paths (prevent open redirect)
  const safePath = returnTo.startsWith('/') ? returnTo : '/dashboard';

  throw redirect(303, safePath);
}