<script>
  import StatusBadge from '$lib/primitives/StatusBadge.svelte';
  import Button      from '$lib/primitives/Button.svelte';
  import Card        from '$lib/primitives/Card.svelte';
  import { enhance } from '$app/forms';
  import { goto }    from '$app/navigation';

  /** @type {import('./$types').PageData} */
  export let data;

  /** @type {import('./$types').ActionData} */
  export let form;

  $: inv = data.invoice;

  // Status transitions allowed from the current status
  const TRANSITIONS = {
    draft:   ['sent', 'cancelled'],
    sent:    ['viewed', 'paid', 'overdue', 'cancelled'],
    viewed:  ['paid', 'partial', 'overdue', 'cancelled'],
    partial: ['paid', 'overdue', 'cancelled'],
    overdue: ['paid', 'partial', 'cancelled'],
    paid:    [],
    cancelled: [],
  };

  $: allowedTransitions = TRANSITIONS[inv._statusRaw] ?? [];
  $: canDelete    = inv._statusRaw === 'draft';
  $: canDuplicate = true;
  $: canPayment   = !['draft', 'cancelled', 'paid'].includes(inv._statusRaw);

  let showPaymentForm = false;
</script>

<div class="page">

  <!-- Header -->
  <div class="page-header">
    <div class="header-left">
      <button class="back-btn" on:click={() => goto('/invoices')}>← Invoices</button>
      <h1 class="page-title">{inv.number}</h1>
      <StatusBadge status={inv.status} />
    </div>

    <div class="header-actions">
      <!-- Status transitions -->
      {#each allowedTransitions as nextStatus}
        <form method="POST" action="?/status" use:enhance>
          <input type="hidden" name="status" value={nextStatus} />
          <Button variant={nextStatus === 'paid' ? 'primary' : 'outline'} type="submit">
            Mark {nextStatus}
          </Button>
        </form>
      {/each}

      {#if canDuplicate}
        <form method="POST" action="?/duplicate" use:enhance>
          <Button variant="outline" type="submit">⊕ Duplicate</Button>
        </form>
      {/if}

      {#if canDelete}
        <form method="POST" action="?/delete" use:enhance>
          <Button variant="outline" type="submit">🗑 Delete</Button>
        </form>
      {/if}
    </div>
  </div>

  {#if form?.error}
    <div class="error-banner">{form.error}</div>
  {/if}

  <div class="layout">

    <!-- Left: invoice body -->
    <div class="main-col">

      <!-- Client + dates -->
      <Card>
        <svelte:fragment slot="header">
          <span class="card-title">Invoice Details</span>
        </svelte:fragment>
        <div class="meta-grid">
          <div class="meta-item">
            <div class="meta-label">Client</div>
            <div class="meta-value">{inv.client}</div>
            <div class="meta-sub">{inv.clientEmail}</div>
          </div>
          <div class="meta-item">
            <div class="meta-label">Issue Date</div>
            <div class="meta-value">{inv.issueDate}</div>
          </div>
          <div class="meta-item">
            <div class="meta-label">Due Date</div>
            <div class="meta-value">{inv.dueDate}</div>
          </div>
          {#if inv.poNumber}
            <div class="meta-item">
              <div class="meta-label">PO Number</div>
              <div class="meta-value">{inv.poNumber}</div>
            </div>
          {/if}
          {#if inv.paidDate}
            <div class="meta-item">
              <div class="meta-label">Paid Date</div>
              <div class="meta-value" style="color:var(--status-paid-text)">{inv.paidDate}</div>
            </div>
          {/if}
        </div>
      </Card>

      <!-- Line items -->
      <Card>
        <svelte:fragment slot="header">
          <span class="card-title">Line Items</span>
        </svelte:fragment>
        <svelte:fragment slot="raw">
          <table class="items-table">
            <thead>
              <tr>
                <th>Description</th>
                <th class="num">Qty</th>
                <th class="num">Unit Price</th>
                <th class="num">Total</th>
              </tr>
            </thead>
            <tbody>
              {#each inv.items as item (item.id)}
                <tr>
                  <td>
                    <div class="item-desc">{item.description}</div>
                    {#if item.detail}<div class="item-detail">{item.detail}</div>{/if}
                  </td>
                  <td class="num">{item.quantity} {item.unit}</td>
                  <td class="num">{item.unitPrice}</td>
                  <td class="num">{item.lineTotal}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </svelte:fragment>
      </Card>

      <!-- Payments -->
      {#if inv.payments.length > 0 || canPayment}
        <Card>
          <svelte:fragment slot="header">
            <span class="card-title">Payments</span>
            {#if canPayment}
              <Button variant="outline" on:click={() => showPaymentForm = !showPaymentForm}>
                + Record Payment
              </Button>
            {/if}
          </svelte:fragment>
          <svelte:fragment slot="raw">

            {#if showPaymentForm}
              <form method="POST" action="?/payment" use:enhance class="payment-form"
                on:submit={() => showPaymentForm = false}>
                <div class="pf-row">
                  <div class="pf-field">
                    <label class="field-label" for="pf-amount">Amount</label>
                    <input id="pf-amount" class="form-input" name="amount" type="number"
                      step="0.01" min="0.01" max={inv._balanceDueRaw} required />
                  </div>
                  <div class="pf-field">
                    <label class="field-label" for="pf-date">Payment Date</label>
                    <input id="pf-date" class="form-input" name="payment_date" type="date" required />
                  </div>
                  <div class="pf-field">
                    <label class="field-label" for="pf-method">Method</label>
                    <select id="pf-method" class="form-input" name="method">
                      <option value="bank_transfer">Bank Transfer</option>
                      <option value="credit_card">Credit Card</option>
                      <option value="cash">Cash</option>
                      <option value="cheque">Cheque</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                  <div class="pf-field">
                    <label class="field-label" for="pf-ref">Reference</label>
                    <input id="pf-ref" class="form-input" name="reference" type="text" />
                  </div>
                </div>
                <div class="pf-actions">
                  <Button variant="primary" type="submit">Save Payment</Button>
                  <Button variant="outline" on:click={() => showPaymentForm = false}>Cancel</Button>
                </div>
              </form>
            {/if}

            {#if inv.payments.length > 0}
              <table class="items-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Method</th>
                    <th>Reference</th>
                    <th class="num">Amount</th>
                  </tr>
                </thead>
                <tbody>
                  {#each inv.payments as p (p.id)}
                    <tr>
                      <td>{p.date}</td>
                      <td style="text-transform:capitalize">{p.method.replace('_', ' ')}</td>
                      <td class="mono">{p.reference || '—'}</td>
                      <td class="num" style="color:var(--status-paid-text)">{p.amount}</td>
                    </tr>
                  {/each}
                </tbody>
              </table>
            {:else if !showPaymentForm}
              <div class="empty-row">No payments recorded yet.</div>
            {/if}

          </svelte:fragment>
        </Card>
      {/if}

      <!-- Activity log -->
      {#if inv.activity.length > 0}
        <Card>
          <svelte:fragment slot="header">
            <span class="card-title">Activity</span>
          </svelte:fragment>
          <div class="activity-list">
            {#each inv.activity as entry (entry.id)}
              <div class="activity-row">
                <div class="activity-dot" />
                <div class="activity-body">
                  <div class="activity-desc">{entry.description}</div>
                  <div class="activity-date">{entry.date}</div>
                </div>
              </div>
            {/each}
          </div>
        </Card>
      {/if}

    </div>

    <!-- Right: totals sidebar -->
    <div class="sidebar">
      <Card>
        <svelte:fragment slot="header">
          <span class="card-title">Summary</span>
        </svelte:fragment>
        <div class="summary-rows">
          <div class="summary-row">
            <span>Subtotal</span><span>{inv.subtotal}</span>
          </div>
          {#if inv.discountAmount !== '$0.00'}
            <div class="summary-row">
              <span>Discount</span><span style="color:var(--status-paid-text)">−{inv.discountAmount}</span>
            </div>
          {/if}
          <div class="summary-row">
            <span>{inv.taxLabel} ({inv.taxPercent}%)</span><span>{inv.taxAmount}</span>
          </div>
          <div class="summary-row total">
            <span>Total</span><span class="total-val">{inv.total}</span>
          </div>
          {#if inv.amountPaid !== '$0.00'}
            <div class="summary-row">
              <span>Amount Paid</span>
              <span style="color:var(--status-paid-text)">{inv.amountPaid}</span>
            </div>
            <div class="summary-row">
              <span style="font-weight:600">Balance Due</span>
              <span style="font-weight:600;color:var(--status-overdue-text)">{inv.balanceDue}</span>
            </div>
          {/if}
        </div>
        {#if inv.notes}
          <div class="notes-section">
            <div class="field-label">Notes</div>
            <p class="notes-text">{inv.notes}</p>
          </div>
        {/if}
      </Card>
    </div>

  </div>
</div>

<style>
  .page {
    padding: 28px;
    max-width: 1100px;
  }

  /* ---- Header ------------------------------------------- */
  .page-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 24px;
    flex-wrap: wrap;
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .page-title {
    font-size: 22px;
    font-weight: 600;
    color: var(--text-primary);
    font-family: 'DM Mono', monospace;
  }

  .back-btn {
    font-size: 13px;
    color: var(--text-muted);
    font-family: inherit;
    transition: color 0.12s;
  }
  .back-btn:hover { color: var(--accent); }

  .header-actions {
    display: flex;
    gap: 8px;
    align-items: center;
    flex-wrap: wrap;
  }

  /* ---- Layout ------------------------------------------- */
  .layout {
    display: grid;
    grid-template-columns: 1fr 280px;
    gap: 16px;
    align-items: start;
  }

  @media (max-width: 800px) {
    .layout { grid-template-columns: 1fr; }
  }

  .main-col {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .sidebar {
    position: sticky;
    top: 20px;
  }

  /* ---- Card titles -------------------------------------- */
  .card-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
  }

  /* ---- Meta grid ---------------------------------------- */
  .meta-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 16px;
  }

  .meta-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); margin-bottom: 4px; }
  .meta-value { font-size: 14px; font-weight: 500; color: var(--text-primary); }
  .meta-sub   { font-size: 12px; color: var(--text-muted); margin-top: 2px; }

  /* ---- Items table -------------------------------------- */
  .items-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13.5px;
  }

  .items-table th {
    text-align: left;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-muted);
    padding: 10px 20px;
    border-bottom: 1px solid var(--border);
    white-space: nowrap;
  }

  .items-table td {
    padding: 12px 20px;
    border-bottom: 1px solid var(--border);
    color: var(--text-primary);
    vertical-align: top;
  }

  .items-table tr:last-child td { border-bottom: none; }
  .items-table .num { text-align: right; font-variant-numeric: tabular-nums; }

  .item-desc   { font-weight: 500; }
  .item-detail { font-size: 12px; color: var(--text-muted); margin-top: 2px; }
  .mono        { font-family: 'DM Mono', monospace; font-size: 12.5px; }

  /* ---- Payment form ------------------------------------- */
  .payment-form {
    padding: 16px 20px;
    border-bottom: 1px solid var(--border);
    background: var(--bg-surface-alt);
  }

  .pf-row {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 12px;
    margin-bottom: 12px;
  }

  .pf-field { display: flex; flex-direction: column; gap: 5px; }

  .pf-actions { display: flex; gap: 8px; }

  .field-label {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-muted);
  }

  .form-input {
    height: 34px;
    padding: 0 10px;
    border-radius: var(--radius-sm);
    font-size: 13px;
    width: 100%;
  }

  /* ---- Activity ----------------------------------------- */
  .activity-list { display: flex; flex-direction: column; gap: 0; }

  .activity-row {
    display: flex;
    gap: 12px;
    align-items: flex-start;
    padding: 12px 0;
    border-bottom: 1px solid var(--border);
  }
  .activity-row:last-child { border-bottom: none; }

  .activity-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--accent);
    flex-shrink: 0;
    margin-top: 5px;
  }

  .activity-desc { font-size: 13px; color: var(--text-primary); }
  .activity-date { font-size: 12px; color: var(--text-muted); margin-top: 2px; }

  /* ---- Summary ------------------------------------------ */
  .summary-rows {
    display: flex;
    flex-direction: column;
    gap: 0;
  }

  .summary-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 9px 0;
    font-size: 13.5px;
    border-top: 1px solid var(--border);
    color: var(--text-secondary);
  }

  .summary-row:first-child { border-top: none; }

  .summary-row.total {
    border-top: 2px solid var(--border);
    margin-top: 4px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .total-val {
    font-size: 20px;
    font-weight: 700;
    color: var(--accent);
    letter-spacing: -0.02em;
  }

  .notes-section {
    border-top: 1px solid var(--border);
    padding-top: 14px;
    margin-top: 4px;
  }

  .notes-text {
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.6;
    margin-top: 6px;
    white-space: pre-line;
  }

  /* ---- Empty state -------------------------------------- */
  .empty-row {
    padding: 20px;
    text-align: center;
    font-size: 13px;
    color: var(--text-muted);
  }

  /* ---- Error banner ------------------------------------- */
  .error-banner {
    margin-bottom: 16px;
    padding: 10px 16px;
    background: var(--status-overdue-bg);
    color: var(--status-overdue-text);
    border: 1px solid currentColor;
    border-radius: var(--radius-sm);
    font-size: 13px;
  }
</style>