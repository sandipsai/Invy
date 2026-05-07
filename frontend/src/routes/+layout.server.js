import { apiGet } from '$lib/server/api.js';

/**
 * Root layout load — runs on every navigation server-side.
 * Fetches the business profile so AppShell can show the
 * business name and initialise the user avatar.
 *
 * Failure is non-fatal: if the backend is down we degrade
 * gracefully with empty defaults rather than a hard error.
 *
 * @type {import('@sveltejs/kit').LayoutServerLoad}
 */
export async function load({ fetch }) {
  try {
    const profile = await apiGet('/settings/profile', undefined, fetch);
    return {
      profile: {
        businessName: profile.business_name ?? 'My Business',
        email:        profile.email         ?? '',
        logoUrl:      profile.logo_url      ?? '',
      },
    };
  } catch {
    // Backend unreachable or erroring — return safe defaults
    return {
      profile: {
        businessName: 'My Business',
        email:        '',
        logoUrl:      '',
      },
    };
  }
}