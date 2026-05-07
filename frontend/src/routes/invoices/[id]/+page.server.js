import { apiGet, apiPatch, apiPost, apiDelete, formatMoney, formatDate } from '$lib/server/api.js';
import { redirect, fail } from '@sveltejs/kit';

/** @type {import('@sveltejs/kit').PageServerLoad} */
export async function load({ fetch, params }) {
  const invoice = await apiGet(`/invoices/${params.id}`, undefined, fetch);

  return {
    invoice: shapeInvoiceDetail(invoice),
  };
}

/** @type {import('@sveltejs/kit').Actions} */
export const actions = {
  /** Transition invoice status */
  status: async ({ request, fetch, params }) => {
    const formData = await request.formData();
    const status   = formData.get('status');

    try {
      await apiPatch(`/invoices/${params.id}/status`, { status }, fetch);
      return { success: true };
    } catch (e) {
      return fail(e?.status ?? 500, { error: e?.body?.message ?? 'Status update failed.' });
    }
  },

  /** Record a payment */
  payment: async ({ request, fetch, params }) => {
    const formData = await request.formData();
    const body = {
      amount:       Number(formData.get('amount')),
      method:       formData.get('method') ?? 'bank_transfer',
      reference:    formData.get('reference') ?? '',
      payment_date: formData.get('payment_date'),
      notes:        formData.get('notes') ?? '',
    };

    try {
      await apiPost(`/invoices/${params.id}/payments`, body, fetch);
      return { success: true };
    } catch (e) {
      return fail(e?.status ?? 500, { error: e?.body?.message ?? 'Payment failed.' });
    }
  },

  /** Delete a draft invoice */
  delete: async ({ fetch, params }) => {
    try {
      await apiDelete(`/invoices/${params.id}`, fetch);
      throw redirect(303, '/invoices');
    } catch (e) {
      if (e?.status === 303) throw e;
      return fail(e?.status ?? 500, { error: e?.body?.message ?? 'Delete failed.' });
    }
  },

  /** Duplicate an invoice */
  duplicate: async ({ fetch, params }) => {
    try {
      const newInvoice = await apiPost(`/invoices/${params.id}/duplicate`, {}, fetch);
      throw redirect(303, `/invoices/${newInvoice.id}`);
    } catch (e) {
      if (e?.status === 303) throw e;
      return fail(e?.status ?? 500, { error: e?.body?.message ?? 'Duplicate failed.' });
    }
  },
};

/**
 * Shape the full InvoiceOut API response into what InvoiceDetail.svelte needs.
 * @param {object} inv
 */
function shapeInvoiceDetail(inv) {
  const clientName = inv.client?.name ?? '';

  return {
    id:             inv.id,
    number:         inv.number,
    status:         inv.status,
    client:         clientName,
    clientEmail:    inv.client?.email ?? '',
    issueDate:      formatDate(inv.issue_date),
    dueDate:        formatDate(inv.due_date),
    paidDate:       inv.paid_date ? formatDate(inv.paid_date) : null,
    currency:       inv.currency,
    subtotal:       formatMoney(inv.subtotal,        inv.currency),
    discountAmount: formatMoney(inv.discount_amount, inv.currency),
    taxLabel:       inv.tax_label,
    taxPercent:     inv.tax_percent,
    taxAmount:      formatMoney(inv.tax_amount,      inv.currency),
    total:          formatMoney(inv.total,            inv.currency),
    amountPaid:     formatMoney(inv.amount_paid,     inv.currency),
    balanceDue:     formatMoney(inv.balance_due,     inv.currency),
    notes:          inv.notes          ?? '',
    terms:          inv.terms          ?? '',
    footer:         inv.footer         ?? '',
    poNumber:       inv.po_number      ?? '',

    items: (inv.items ?? []).map(item => ({
      id:          item.id,
      description: item.description,
      detail:      item.detail ?? '',
      quantity:    item.quantity,
      unit:        item.unit ?? '',
      unitPrice:   formatMoney(item.unit_price, inv.currency),
      lineTotal:   formatMoney(item.line_total,  inv.currency),
    })),

    payments: (inv.payments ?? []).map(p => ({
      id:          p.id,
      amount:      formatMoney(p.amount, inv.currency),
      method:      p.method,
      reference:   p.reference ?? '',
      date:        formatDate(p.payment_date),
    })),

    activity: (inv.activity ?? []).map(a => ({
      id:          a.id,
      event:       a.event,
      description: a.description,
      date:        new Date(a.created_at).toLocaleDateString('en-US', {
        month: 'short', day: 'numeric', year: 'numeric',
        hour: 'numeric', minute: '2-digit',
      }),
    })),

    // Raw numeric values for the payment form
    _balanceDueRaw: inv.balance_due,
    _statusRaw:     inv.status,
  };
}