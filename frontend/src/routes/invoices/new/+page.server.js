import { apiGet, apiPost } from '$lib/server/api.js';
import { redirect, fail }  from '@sveltejs/kit';

/** @type {import('@sveltejs/kit').PageServerLoad} */
export async function load({ fetch }) {
  const clients = await apiGet('/clients/', { limit: 200 }, fetch);

  return {
    clients: (clients ?? []).map(c => ({
      id:   c.id,
      name: c.name,
    })),
  };
}

/** @type {import('@sveltejs/kit').Actions} */
export const actions = {
  /**
   * Create a new invoice. Called by CreateInvoice.svelte on send/draft.
   * Expects JSON in the request body.
   */
  create: async ({ request, fetch }) => {
    let body;
    try {
      body = await request.json();
    } catch {
      return fail(400, { error: 'Invalid request body.' });
    }

    try {
      const invoice = await apiPost('/invoices/', body, fetch);
      // Redirect to the new invoice's detail page
      throw redirect(303, `/invoices/${invoice.id}`);
    } catch (e) {
      // Re-throw SvelteKit redirects
      if (e?.status === 303) throw e;

      return fail(e?.status ?? 500, {
        error: e?.body?.message ?? 'Failed to create invoice.',
      });
    }
  },

  /**
   * Save as draft — same as create but doesn't redirect away.
   */
  draft: async ({ request, fetch }) => {
    let body;
    try {
      body = await request.json();
    } catch {
      return fail(400, { error: 'Invalid request body.' });
    }

    try {
      const invoice = await apiPost('/invoices/', body, fetch);
      return { success: true, invoiceId: invoice.id, number: invoice.number };
    } catch (e) {
      return fail(e?.status ?? 500, {
        error: e?.body?.message ?? 'Failed to save draft.',
      });
    }
  },
};