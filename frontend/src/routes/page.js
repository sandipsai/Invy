import { redirect } from '@sveltejs/kit';

/** Redirect the root URL to the dashboard. */
export function load() {
  throw redirect(302, '/dashboard');
}