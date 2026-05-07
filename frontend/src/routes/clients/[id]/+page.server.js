import { apiGet, apiPatch, apiDelete, shapeInvoiceRow } from '$lib/server/api.js';
import { redirect, fail } from '@sveltejs/kit';

/** @type {import('@sveltejs/kit').PageServerLoad} */
export async function load({ fetch, params }) {
  const [client, invoices] = await Promise.all([
    apiGet(`/clients/${params.id}`,           undefined, fetch),
    apiGet(`/clients/${params.id}/invoices`,  undefined, fetch),
  ]);

  return {
    client: {
      id:           client.id,
      name:         client.name,
      email:        client.email        ?? '',
      phone:        client.phone        ?? '',
      company:      client.company      ?? '',
      billingAddress: client.billing_address ?? '',
      taxId:        client.tax_id       ?? '',
      currency:     client.currency     ?? 'USD',
      notes:        client.notes        ?? '',
      isActive:     client.is_active,
      totalInvoiced: client.total_invoiced ?? 0,
      totalPaid:    client.total_paid   ?? 0,
      outstanding:  client.outstanding  ?? 0,
      invoiceCount: client.invoice_count ?? 0,
    },
    invoices: (invoices ?? []).map(shapeInvoiceRow),
  };
}

/** @type {import('@sveltejs/kit').Actions} */
export const actions = {
  /** Update editable client fields */
  update: async ({ request, fetch, params }) => {
    const formData = await request.formData();
    const body = {
      name:            formData.get('name'),
      email:           formData.get('email'),
      phone:           formData.get('phone'),
      company:         formData.get('company'),
      billing_address: formData.get('billing_address'),
      tax_id:          formData.get('tax_id'),
      currency:        formData.get('currency'),
      notes:           formData.get('notes'),
    };

    try {
      await apiPatch(`/clients/${params.id}`, body, fetch);
      return { success: true };
    } catch (e) {
      return fail(e?.status ?? 500, { error: e?.body?.message ?? 'Update failed.' });
    }
  },

  /** Soft-delete the client */
  delete: async ({ fetch, params }) => {
    try {
      await apiDelete(`/clients/${params.id}`, fetch);
      throw redirect(303, '/clients');
    } catch (e) {
      if (e?.status === 303) throw e;
      return fail(e?.status ?? 500, { error: e?.body?.message ?? 'Delete failed.' });
    }
  },
};