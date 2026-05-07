import { apiGet, shapeInvoiceRow } from '$lib/server/api.js';

const PER_PAGE = 5;

/** @type {import('@sveltejs/kit').PageServerLoad} */
export async function load({ fetch, url }) {
  const status  = url.searchParams.get('status')  ?? '';
  const search  = url.searchParams.get('search')  ?? '';
  const page    = Math.max(1, Number(url.searchParams.get('page') ?? 1));
  const skip    = (page - 1) * PER_PAGE;

  // Map UI tab keys to API status values
  // 'all' → no status filter; others pass through directly
  const params = {
    limit:  PER_PAGE,
    skip,
    ...(status && status !== 'all' ? { status } : {}),
    ...(search ? { search } : {}),
  };

  const invoices = await apiGet('/invoices/', params, fetch);

  return {
    invoices:   (invoices ?? []).map(shapeInvoiceRow),
    activeTab:  status || 'all',
    search,
    currentPage: page,
    perPage:    PER_PAGE,
    // The API doesn't return a total count in the list response,
    // so we infer: if we got a full page, there may be more.
    // A proper total requires a COUNT endpoint — stub for now.
    total: invoices?.length === PER_PAGE ? page * PER_PAGE + 1 : (page - 1) * PER_PAGE + (invoices?.length ?? 0),
  };
}