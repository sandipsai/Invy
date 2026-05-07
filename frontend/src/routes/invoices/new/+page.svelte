<script>
  import CreateInvoice from '$lib/pages/CreateInvoice.svelte';
  import { goto }     from '$app/navigation';

  /** @type {import('./$types').PageData} */
  export let data;

  /** @type {import('./$types').ActionData} */
  export let form;

  async function onSend(e) {
    const body = e.detail;
    const res  = await fetch('?/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(buildPayload(body)),
    });
    const result = await res.json();
    if (result.type === 'redirect') goto(result.location);
  }

  async function onSaveDraft(e) {
    const body = e.detail;
    const res  = await fetch('?/draft', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(buildPayload(body)),
    });
    const result = await res.json();
    if (result.data?.invoiceId) {
      goto(`/invoices/${result.data.invoiceId}`);
    }
  }

  /**
   * Translate CreateInvoice's internal state into the API POST body.
   * @param {object} detail — from the 'send' or 'saveDraft' event
   */
  function buildPayload(detail) {
    return {
      client_id:        Number(detail.clientId),
      issue_date:       detail.issueDate,
      due_date:         detail.dueDate,
      currency:         'USD',
      tax_label:        'Tax',
      tax_percent:      detail.taxRate * 100,   // component stores 0.08, API wants 8
      discount_percent: 0,
      notes:            detail.notes ?? '',
      items: (detail.items ?? []).map((it, i) => ({
        description:      it.description,
        quantity:         it.qty,
        unit_price:       it.rate,
        discount_percent: 0,
        tax_percent:      null,                  // inherit invoice-level tax
        sort_order:       i,
      })),
    };
  }
</script>

{#if form?.error}
  <div class="error-banner">{form.error}</div>
{/if}

<CreateInvoice
  clients={data.clients}
  on:send={onSend}
  on:saveDraft={onSaveDraft}
  on:preview={() => {/* future PDF preview */}}
/>

<style>
  .error-banner {
    margin: 16px 28px 0;
    padding: 10px 16px;
    background: var(--status-overdue-bg);
    color: var(--status-overdue-text);
    border: 1px solid var(--status-overdue-text);
    border-radius: var(--radius-sm);
    font-size: 13px;
  }
</style>