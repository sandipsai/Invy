import { apiGet, formatMoney } from '$lib/server/api.js';

/** @type {import('@sveltejs/kit').PageServerLoad} */
export async function load({ fetch }) {
  // Run both requests in parallel
  const [stats, clients] = await Promise.all([
    apiGet('/dashboard/stats', undefined, fetch),
    apiGet('/clients/', { limit: 50, is_active: true }, fetch),
  ]);

  // Revenue by client — sort descending, take top 8
  const revenueByClient = (clients ?? [])
    .filter(c => (c.total_invoiced ?? 0) > 0)
    .sort((a, b) => b.total_invoiced - a.total_invoiced)
    .slice(0, 8)
    .map(c => ({
      label:        c.name,
      value:        c.total_invoiced ?? 0,
      displayValue: formatMoney(c.total_invoiced ?? 0, c.currency),
    }));

  return {
    stats: {
      ytdRevenue:    formatMoney(stats.total_revenue),
      outstanding:   formatMoney(stats.outstanding_amount),
      overdueAmount: formatMoney(stats.overdue_amount),
      totalInvoices: stats.total_invoices,
      paidCount:     stats.paid_count,
      overdueCount:  stats.overdue_count,
      totalClients:  stats.total_clients,
    },
    revenueByClient,
  };
}