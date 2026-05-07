import { apiGet, apiPatch, apiPost, apiDelete } from '$lib/server/api.js';
import { fail } from '@sveltejs/kit';

/** @type {import('@sveltejs/kit').PageServerLoad} */
export async function load({ fetch }) {
  const [profile, taxRates] = await Promise.all([
    apiGet('/settings/profile',   undefined, fetch),
    apiGet('/settings/tax-rates', undefined, fetch),
  ]);

  return {
    profile:  profile  ?? {},
    taxRates: taxRates ?? [],
  };
}

/** @type {import('@sveltejs/kit').Actions} */
export const actions = {

  /** Save business profile */
  saveProfile: async ({ request, fetch }) => {
    const f = await request.formData();

    const body = {
      business_name:         f.get('business_name'),
      email:                 f.get('email'),
      phone:                 f.get('phone'),
      address:               f.get('address'),
      tax_id:                f.get('tax_id'),
      website:               f.get('website'),
      default_currency:      f.get('default_currency'),
      default_tax_percent:   Number(f.get('default_tax_percent') || 0),
      default_payment_terms: Number(f.get('default_payment_terms') || 30),
      invoice_footer:        f.get('invoice_footer'),
      bank_details:          f.get('bank_details'),
    };

    try {
      const updated = await apiPatch('/settings/profile', body, fetch);
      return { success: true, profile: updated };
    } catch (e) {
      return fail(e?.status ?? 500, { error: e?.body?.message ?? 'Failed to save profile.' });
    }
  },

  /** Add a new tax rate preset */
  addTaxRate: async ({ request, fetch }) => {
    const f = await request.formData();

    const body = {
      name:        f.get('name'),
      rate:        Number(f.get('rate') || 0),
      description: f.get('description') ?? '',
      is_default:  f.get('is_default') === 'true',
    };

    try {
      await apiPost('/settings/tax-rates', body, fetch);
      return { success: true };
    } catch (e) {
      return fail(e?.status ?? 500, { error: e?.body?.message ?? 'Failed to add tax rate.' });
    }
  },

  /** Soft-delete a tax rate preset */
  deleteTaxRate: async ({ request, fetch }) => {
    const f = await request.formData();
    const id = f.get('rate_id');

    try {
      await apiDelete(`/settings/tax-rates/${id}`, fetch);
      return { success: true };
    } catch (e) {
      return fail(e?.status ?? 500, { error: e?.body?.message ?? 'Failed to delete tax rate.' });
    }
  },
};