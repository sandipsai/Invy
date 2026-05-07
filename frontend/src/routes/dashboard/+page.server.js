import { apiGet, formatMoney, shapeInvoiceRow } from '$lib/server/api.js';

/** @type {import('@sveltejs/kit').PageServerLoad} */
export async function load({ fetch }) {
  const stats = await apiGet('/dashboard/stats', undefined, fetch);

  return {
    // ---- Stat cards ----------------------------------------
    stats: {
      netTotal:     formatMoney(stats.outstanding_amount),
      income:       formatMoney(stats.total_revenue),
      overdueAmount:formatMoney(stats.overdue_amount),
      overdueCount: stats.overdue_count,

      // For the badge on the income card
      paidCount:    stats.paid_count,
      sentCount:    stats.sent_count,
      draftCount:   stats.draft_count,
      totalClients: stats.total_clients,
    },

    // ---- Pending payments table ----------------------------
    // recent_invoices from the API — filter to non-paid for the
    // "Pending Payments" table; show all in Recent Activity
    recentInvoices: (stats.recent_invoices ?? []).map(shapeInvoiceRow),

    // ---- Activity feed -------------------------------------
    // Derive activity items from recent invoices since the API
    // returns activity per-invoice (GET /invoices/{id}), not globally.
    // The dashboard stats endpoint gives us enough to build a feed.
    activityItems: buildActivityFeed(stats.recent_invoices ?? []),
  };
}

/**
 * Build the activity feed from the recent_invoices list.
 * Each invoice contributes one entry based on its current status.
 *
 * @param {object[]} invoices
 */
function buildActivityFeed(invoices) {
  return invoices.slice(0, 5).map((inv, i) => {
    const clientName = inv.client?.name ?? 'Unknown';
    const amount     = formatMoney(inv.total, inv.currency);

    const config = statusActivityConfig(inv.status, clientName, inv.number, amount);

    return {
      id:            inv.id ?? i,
      dotVariant:    config.dotVariant,
      dotIcon:       config.dotIcon,
      title:         config.title,
      meta:          formatRelativeDate(inv.created_at),
      amount:        config.showAmount ? amount : '',
      amountVariant: config.amountVariant,
    };
  });
}

/** @param {string} status @param {string} client @param {string} number @param {string} amount */
function statusActivityConfig(status, client, number, amount) {
  switch (status) {
    case 'paid':
      return { dotVariant: 'green', dotIcon: '✓', title: `Payment received from ${client}`, showAmount: true,  amountVariant: 'positive' };
    case 'sent':
    case 'viewed':
      return { dotVariant: 'blue',  dotIcon: '✉', title: `Invoice ${number} sent to ${client}`, showAmount: true,  amountVariant: '' };
    case 'overdue':
      return { dotVariant: 'yellow', dotIcon: '!', title: `Invoice ${number} is overdue`, showAmount: true, amountVariant: 'negative' };
    case 'partial':
      return { dotVariant: 'blue',  dotIcon: '½', title: `Partial payment from ${client}`, showAmount: true, amountVariant: 'positive' };
    case 'draft':
    default:
      return { dotVariant: 'gray',  dotIcon: '✎', title: `Draft created for ${client}`, showAmount: false, amountVariant: '' };
  }
}

/**
 * Format an ISO datetime string as a relative or short date label.
 * @param {string} iso
 */
function formatRelativeDate(iso) {
  if (!iso) return '';
  const date  = new Date(iso);
  const now   = new Date();
  const diffMs = now - date;
  const diffDays = Math.floor(diffMs / 86_400_000);

  if (diffDays === 0) {
    return `Today, ${date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}`;
  }
  if (diffDays === 1) return 'Yesterday';
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}