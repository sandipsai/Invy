import { apiGet, shapeClient } from '$lib/server/api.js';

/** @type {import('@sveltejs/kit').PageServerLoad} */
export async function load({ fetch, url }) {
  const search = url.searchParams.get('search') ?? '';

  const clients = await apiGet('/clients/', {
    search,
    limit: 100,
    is_active: true,
  }, fetch);

  return {
    clients: (clients ?? []).map(shapeClient),
    search,
  };
}