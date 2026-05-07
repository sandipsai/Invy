// src/routes/login/+page.server.js
import { redirect } from '@sveltejs/kit';

/**
 * If the user already has a valid session cookie, skip the
 * login page and send them straight to the dashboard.
 *
 * When you wire up real session validation in hooks.server.js,
 * replace the cookie check below with: if (event.locals.user)
 *
 * @type {import('@sveltejs/kit').PageServerLoad}
 */
export async function load({ cookies }) {
  const session = cookies.get('session');
  if (session) throw redirect(302, '/dashboard');
  return {};
}