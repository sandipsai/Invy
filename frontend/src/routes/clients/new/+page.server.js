import { apiPost }       from '$lib/server/api.js';
import { redirect, fail } from '@sveltejs/kit';

/** No load needed — form is static */
export function load() {
  return {};
}

/** @type {import('@sveltejs/kit').Actions} */
export const actions = {
  create: async ({ request, fetch }) => {
    const f = await request.formData();

    const body = {
      name:             f.get('name'),
      email:            f.get('email'),
      phone:            f.get('phone')            ?? '',
      company:          f.get('company')          ?? '',
      billing_address:  f.get('billing_address')  ?? '',
      tax_id:           f.get('tax_id')           ?? '',
      currency:         f.get('currency')         ?? 'USD',
      notes:            f.get('notes')            ?? '',
    };

    try {
      const client = await apiPost('/clients/', body, fetch);
      throw redirect(303, `/clients/${client.id}`);
    } catch (e) {
      if (e?.status === 303) throw e;
      return fail(e?.status ?? 500, {
        error: e?.body?.message ?? 'Failed to create client.',
        values: Object.fromEntries(f), // preserve form values on error
      });
    }
  },
};