<script>
  import Card        from '$lib/primitives/Card.svelte';
  import Button      from '$lib/primitives/Button.svelte';
  import DataTable   from '$lib/components/DataTable.svelte';
  import InvoiceRow  from '$lib/components/InvoiceRow.svelte';
  import { enhance } from '$app/forms';
  import { goto }    from '$app/navigation';
  import { formatMoney } from '$lib/server/api.js';

  /** @type {import('./$types').PageData} */
  export let data;

  /** @type {import('./$types').ActionData} */
  export let form;

  $: c = data.client;

  let editing = false;

  const invoiceColumns = [
    { key: 'id',      label: 'Invoice ID'             },
    { key: 'date',    label: 'Date'                   },
    { key: 'amount',  label: 'Amount', align: 'right' },
    { key: 'status',  label: 'Status'                 },
    { key: 'actions', label: ''                       },
  ];
</script>

<div class="page">

  <!-- Header -->
  <div class="page-header">
    <div class="header-left">
      <button class="back-btn" on:click={() => goto('/clients')}>← Clients</button>
      <h1 class="page-title">{c.name}</h1>
      {#if !c.isActive}
        <span class="inactive-tag">Inactive</span>
      {/if}
    </div>
    <div class="header-actions">
      <Button variant="outline" on:click={() => editing = !editing}>
        {editing ? 'Cancel' : '✎ Edit'}
      </Button>
      <Button variant="primary" on:click={() => goto(`/invoices/new?client=${c.id}`)}>
        + New Invoice
      </Button>
    </div>
  </div>

  {#if form?.error}
    <div class="error-banner">{form.error}</div>
  {/if}

  <div class="layout">
    <div class="main-col">

      <!-- Info / Edit form -->
      <Card>
        <svelte:fragment slot="header">
          <span class="card-title">Client Info</span>
        </svelte:fragment>

        {#if editing}
          <form method="POST" action="?/update" use:enhance
            on:submit={() => editing = false}>
            <div class="form-grid">
              <div class="form-field">
                <label class="field-label" for="cf-name">Name</label>
                <input id="cf-name" class="form-input" name="name" value={c.name} required />
              </div>
              <div class="form-field">
                <label class="field-label" for="cf-email">Email</label>
                <input id="cf-email" class="form-input" name="email" type="email" value={c.email} />
              </div>
              <div class="form-field">
                <label class="field-label" for="cf-phone">Phone</label>
                <input id="cf-phone" class="form-input" name="phone" value={c.phone} />
              </div>
              <div class="form-field">
                <label class="field-label" for="cf-company">Company</label>
                <input id="cf-company" class="form-input" name="company" value={c.company} />
              </div>
              <div class="form-field full">
                <label class="field-label" for="cf-address">Billing Address</label>
                <input id="cf-address" class="form-input" name="billing_address" value={c.billingAddress} />
              </div>
              <div class="form-field">
                <label class="field-label" for="cf-tax">Tax ID</label>
                <input id="cf-tax" class="form-input" name="tax_id" value={c.taxId} />
              </div>
              <div class="form-field">
                <label class="field-label" for="cf-currency">Currency</label>
                <select id="cf-currency" class="form-input" name="currency">
                  {#each ['USD','EUR','GBP','INR','JPY'] as cur}
                    <option value={cur} selected={c.currency === cur}>{cur}</option>
                  {/each}
                </select>
              </div>
              <div class="form-field full">
                <label class="field-label" for="cf-notes">Notes</label>
                <textarea id="cf-notes" class="form-input" name="notes"
                  style="height:70px;resize:none;padding:8px">{c.notes}</textarea>
              </div>
            </div>
            <div class="form-actions">
              <Button variant="primary" type="submit">Save Changes</Button>
              <Button variant="outline" on:click={() => editing = false}>Cancel</Button>
            </div>
          </form>

        {:else}
          <div class="info-grid">
            <div class="info-item">
              <div class="info-label">Email</div>
              <div class="info-value">{c.email || '—'}</div>
            </div>
            <div class="info-item">
              <div class="info-label">Phone</div>
              <div class="info-value">{c.phone || '—'}</div>
            </div>
            <div class="info-item">
              <div class="info-label">Company</div>
              <div class="info-value">{c.company || '—'}</div>
            </div>
            <div class="info-item">
              <div class="info-label">Tax ID</div>
              <div class="info-value">{c.taxId || '—'}</div>
            </div>
            <div class="info-item">
              <div class="info-label">Currency</div>
              <div class="info-value">{c.currency}</div>
            </div>
            {#if c.billingAddress}
              <div class="info-item full">
                <div class="info-label">Billing Address</div>
                <div class="info-value">{c.billingAddress}</div>
              </div>
            {/if}
            {#if c.notes}
              <div class="info-item full">
                <div class="info-label">Notes</div>
                <div class="info-value" style="white-space:pre-line">{c.notes}</div>
              </div>
            {/if}
          </div>
        {/if}
      </Card>

      <!-- Invoice history -->
      <Card>
        <svelte:fragment slot="header">
          <span class="card-title">Invoice History</span>
          <span class="count-badge">{data.invoices.length}</span>
        </svelte:fragment>
        <svelte:fragment slot="raw">
          <DataTable columns={invoiceColumns}>
            {#each data.invoices as invoice (invoice.id)}
              <InvoiceRow
                {invoice}
                on:action={e => goto(`/invoices/${e.detail.invoice._raw.id}`)}
              />
            {:else}
              <tr>
                <td colspan="5" style="padding:24px;text-align:center;color:var(--text-muted);font-size:13px">
                  No invoices yet.
                </td>
              </tr>
            {/each}
          </DataTable>
        </svelte:fragment>
      </Card>

    </div>

    <!-- Sidebar: billing stats + danger zone -->
    <div class="sidebar">
      <Card>
        <svelte:fragment slot="header">
          <span class="card-title">Billing Summary</span>
        </svelte:fragment>
        <div class="billing-stats">
          <div class="billing-stat">
            <div class="billing-label">Total Invoiced</div>
            <div class="billing-value">{c.totalInvoiced.toLocaleString('en-US', { style:'currency', currency: c.currency })}</div>
          </div>
          <div class="billing-stat">
            <div class="billing-label">Total Paid</div>
            <div class="billing-value" style="color:var(--status-paid-text)">
              {c.totalPaid.toLocaleString('en-US', { style:'currency', currency: c.currency })}
            </div>
          </div>
          <div class="billing-stat">
            <div class="billing-label">Outstanding</div>
            <div class="billing-value" style="color:{c.outstanding > 0 ? 'var(--status-overdue-text)' : 'var(--text-primary)'}">
              {c.outstanding.toLocaleString('en-US', { style:'currency', currency: c.currency })}
            </div>
          </div>
          <div class="billing-stat">
            <div class="billing-label">Total Invoices</div>
            <div class="billing-value">{c.invoiceCount}</div>
          </div>
        </div>
      </Card>

      <!-- Danger zone -->
      {#if c.isActive}
        <div class="danger-zone">
          <div class="danger-title">Danger Zone</div>
          <p class="danger-desc">Deactivating this client hides them from the clients list. All invoice history is preserved.</p>
          <form method="POST" action="?/delete" use:enhance>
            <Button variant="outline" type="submit" style="color:var(--status-overdue-text);border-color:var(--status-overdue-text)">
              Deactivate Client
            </Button>
          </form>
        </div>
      {/if}
    </div>
  </div>

</div>

<style>
  .page { padding: 28px; max-width: 1100px; }

  .page-header {
    display: flex; align-items: center;
    justify-content: space-between; gap: 16px;
    margin-bottom: 24px; flex-wrap: wrap;
  }

  .header-left { display: flex; align-items: center; gap: 12px; }

  .page-title { font-size: 22px; font-weight: 600; color: var(--text-primary); }

  .back-btn { font-size: 13px; color: var(--text-muted); font-family: inherit; transition: color 0.12s; }
  .back-btn:hover { color: var(--accent); }

  .inactive-tag {
    padding: 2px 8px; border-radius: 100px;
    background: var(--status-draft-bg); color: var(--status-draft-text);
    font-size: 11px; font-weight: 600;
  }

  .header-actions { display: flex; gap: 8px; }

  .layout {
    display: grid;
    grid-template-columns: 1fr 260px;
    gap: 16px;
    align-items: start;
  }
  @media (max-width: 800px) { .layout { grid-template-columns: 1fr; } }

  .main-col { display: flex; flex-direction: column; gap: 16px; }
  .sidebar  { position: sticky; top: 20px; display: flex; flex-direction: column; gap: 16px; }

  .card-title { font-size: 14px; font-weight: 600; color: var(--text-primary); }

  .count-badge {
    padding: 2px 8px; border-radius: 100px;
    background: var(--bg-surface-alt); border: 1px solid var(--border);
    font-size: 12px; color: var(--text-muted);
  }

  /* Info display */
  .info-grid, .form-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }
  @media (max-width: 600px) {
    .info-grid, .form-grid { grid-template-columns: 1fr; }
  }

  .full { grid-column: 1 / -1; }

  .info-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); margin-bottom: 3px; }
  .info-value { font-size: 13.5px; color: var(--text-primary); }

  /* Edit form */
  .field-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); margin-bottom: 4px; display: block; }
  .form-field  { display: flex; flex-direction: column; }
  .form-input  { height: 34px; padding: 0 10px; border-radius: var(--radius-sm); font-size: 13.5px; width: 100%; }
  .form-actions { display: flex; gap: 8px; margin-top: 16px; }

  /* Billing stats */
  .billing-stats { display: flex; flex-direction: column; gap: 0; }
  .billing-stat  { padding: 10px 0; border-bottom: 1px solid var(--border); }
  .billing-stat:first-child { padding-top: 0; }
  .billing-stat:last-child  { border-bottom: none; padding-bottom: 0; }
  .billing-label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); font-weight: 500; }
  .billing-value { font-size: 16px; font-weight: 600; color: var(--text-primary); margin-top: 3px; font-variant-numeric: tabular-nums; }

  /* Danger zone */
  .danger-zone {
    background: var(--bg-surface);
    border: 1px solid var(--status-overdue-bg);
    border-radius: var(--radius-md);
    padding: 16px 18px;
  }
  .danger-title { font-size: 13px; font-weight: 600; color: var(--status-overdue-text); margin-bottom: 6px; }
  .danger-desc  { font-size: 12.5px; color: var(--text-secondary); line-height: 1.5; margin-bottom: 12px; }

  /* Error */
  .error-banner {
    margin-bottom: 16px; padding: 10px 16px;
    background: var(--status-overdue-bg); color: var(--status-overdue-text);
    border: 1px solid currentColor; border-radius: var(--radius-sm); font-size: 13px;
  }
</style>