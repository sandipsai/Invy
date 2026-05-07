<script>
  import Card        from '$lib/primitives/Card.svelte';
  import Button      from '$lib/primitives/Button.svelte';
  import { enhance } from '$app/forms';

  /** @type {import('./$types').PageData} */
  export let data;

  /** @type {import('./$types').ActionData} */
  export let form;

  $: p = data.profile;

  const currencies = ['USD','EUR','GBP','INR','JPY','CAD','AUD'];

  let showAddTaxRate = false;
</script>

<div class="page">

  <div class="page-header">
    <div>
      <h1 class="page-title">Settings</h1>
      <p class="page-sub">Manage your business profile and billing configuration.</p>
    </div>
  </div>

  {#if form?.error}
    <div class="error-banner">{form.error}</div>
  {/if}

  {#if form?.success}
    <div class="success-banner">Changes saved successfully.</div>
  {/if}

  <!-- Business Profile -->
  <form method="POST" action="?/saveProfile" use:enhance class="form-section">
    <div class="section-header">
      <div class="section-icon">⊙</div>
      <span class="section-title">Business Profile</span>
    </div>
    <div class="section-body">
      <div class="form-grid cols-2">
        <div class="form-field">
          <label class="field-label" for="s-bname">Business Name</label>
          <input id="s-bname" class="form-input" name="business_name" value={p.business_name ?? ''} required />
        </div>
        <div class="form-field">
          <label class="field-label" for="s-email">Email</label>
          <input id="s-email" class="form-input" name="email" type="email" value={p.email ?? ''} />
        </div>
        <div class="form-field">
          <label class="field-label" for="s-phone">Phone</label>
          <input id="s-phone" class="form-input" name="phone" value={p.phone ?? ''} />
        </div>
        <div class="form-field">
          <label class="field-label" for="s-website">Website</label>
          <input id="s-website" class="form-input" name="website" value={p.website ?? ''} />
        </div>
        <div class="form-field full">
          <label class="field-label" for="s-address">Address</label>
          <input id="s-address" class="form-input" name="address" value={p.address ?? ''} />
        </div>
        <div class="form-field">
          <label class="field-label" for="s-taxid">Tax ID</label>
          <input id="s-taxid" class="form-input" name="tax_id" value={p.tax_id ?? ''} />
        </div>
        <div class="form-field">
          <label class="field-label" for="s-currency">Default Currency</label>
          <div class="select-wrap">
            <select id="s-currency" class="form-input" name="default_currency">
              {#each currencies as cur}
                <option value={cur} selected={p.default_currency === cur}>{cur}</option>
              {/each}
            </select>
          </div>
        </div>
        <div class="form-field">
          <label class="field-label" for="s-tax">Default Tax %</label>
          <input id="s-tax" class="form-input" name="default_tax_percent"
            type="number" step="0.01" min="0" max="100" value={p.default_tax_percent ?? 0} />
        </div>
        <div class="form-field">
          <label class="field-label" for="s-terms">Default Payment Days</label>
          <input id="s-terms" class="form-input" name="default_payment_terms"
            type="number" min="1" value={p.default_payment_terms ?? 30} />
        </div>
        <div class="form-field full">
          <label class="field-label" for="s-footer">Invoice Footer</label>
          <input id="s-footer" class="form-input" name="invoice_footer" value={p.invoice_footer ?? ''} />
        </div>
        <div class="form-field full">
          <label class="field-label" for="s-bank">Bank Details</label>
          <textarea id="s-bank" class="form-input" name="bank_details"
            style="height:80px;resize:none;padding:8px">{p.bank_details ?? ''}</textarea>
        </div>
      </div>
      <div class="form-actions">
        <Button variant="primary" type="submit">Save Profile</Button>
      </div>
    </div>
  </form>

  <!-- Tax Rate Presets -->
  <div class="form-section">
    <div class="section-header">
      <div class="section-icon">%</div>
      <span class="section-title">Tax Rate Presets</span>
      <button class="link-btn" on:click={() => showAddTaxRate = !showAddTaxRate}>
        {showAddTaxRate ? 'Cancel' : '+ Add Rate'}
      </button>
    </div>

    {#if showAddTaxRate}
      <form method="POST" action="?/addTaxRate" use:enhance
        class="add-tax-form" on:submit={() => showAddTaxRate = false}>
        <div class="form-grid cols-3">
          <div class="form-field">
            <label class="field-label" for="tr-name">Name</label>
            <input id="tr-name" class="form-input" name="name" placeholder="e.g. GST 18%" required />
          </div>
          <div class="form-field">
            <label class="field-label" for="tr-rate">Rate %</label>
            <input id="tr-rate" class="form-input" name="rate" type="number" step="0.01" min="0" max="100" required />
          </div>
          <div class="form-field">
            <label class="field-label" for="tr-desc">Description</label>
            <input id="tr-desc" class="form-input" name="description" placeholder="Optional" />
          </div>
        </div>
        <div class="form-actions">
          <Button variant="primary" type="submit">Add Rate</Button>
        </div>
      </form>
    {/if}

    <div class="tax-rate-list">
      {#each data.taxRates as rate (rate.id)}
        <div class="tax-rate-row">
          <div class="tr-info">
            <span class="tr-name">{rate.name}</span>
            {#if rate.is_default}
              <span class="default-tag">Default</span>
            {/if}
            {#if rate.description}
              <span class="tr-desc">{rate.description}</span>
            {/if}
          </div>
          <span class="tr-rate">{rate.rate}%</span>
          <form method="POST" action="?/deleteTaxRate" use:enhance>
            <input type="hidden" name="rate_id" value={rate.id} />
            <button class="delete-btn" aria-label="Delete {rate.name}">×</button>
          </form>
        </div>
      {:else}
        <div class="empty-rates">No tax rate presets yet.</div>
      {/each}
    </div>
  </div>

</div>

<style>
  .page { padding: 28px; max-width: 680px; }

  .page-header { margin-bottom: 24px; }
  .page-title  { font-size: 22px; font-weight: 600; color: var(--text-primary); }
  .page-sub    { font-size: 13px; color: var(--text-muted); margin-top: 4px; }

  /* Form sections */
  .form-section {
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-sm);
    overflow: hidden;
    margin-bottom: 16px;
  }

  .section-header {
    display: flex; align-items: center; gap: 10px;
    padding: 14px 20px; border-bottom: 1px solid var(--border);
  }

  .section-icon {
    width: 24px; height: 24px; border-radius: 5px;
    background: var(--accent-soft); color: var(--accent);
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; flex-shrink: 0;
  }

  .section-title { font-size: 13.5px; font-weight: 600; color: var(--text-primary); flex: 1; }

  .link-btn { font-size: 12.5px; color: var(--accent); font-family: inherit; }
  .link-btn:hover { text-decoration: underline; }

  .section-body { padding: 18px 20px; }
  .add-tax-form { padding: 14px 20px; border-bottom: 1px solid var(--border); background: var(--bg-surface-alt); }

  /* Form layout */
  .form-grid { display: grid; gap: 12px; }
  .cols-2 { grid-template-columns: 1fr 1fr; }
  .cols-3 { grid-template-columns: 1fr 1fr 1fr; }
  @media (max-width: 560px) { .cols-2, .cols-3 { grid-template-columns: 1fr; } }

  .full { grid-column: 1 / -1; }

  .form-field  { display: flex; flex-direction: column; gap: 4px; }
  .field-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); }
  .form-input  { height: 34px; padding: 0 10px; border-radius: var(--radius-sm); font-size: 13.5px; width: 100%; }
  .form-actions { display: flex; gap: 8px; margin-top: 14px; }

  .select-wrap { position: relative; }
  .select-wrap::after {
    content: '⌄'; position: absolute; right: 10px; top: 50%;
    transform: translateY(-55%); color: var(--text-muted); pointer-events: none;
  }
  .select-wrap .form-input { -webkit-appearance: none; appearance: none; padding-right: 28px; cursor: pointer; }

  /* Tax rates list */
  .tax-rate-list { display: flex; flex-direction: column; }

  .tax-rate-row {
    display: flex; align-items: center; gap: 12px;
    padding: 12px 20px; border-bottom: 1px solid var(--border);
  }
  .tax-rate-row:last-child { border-bottom: none; }

  .tr-info    { flex: 1; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
  .tr-name    { font-size: 13.5px; font-weight: 500; color: var(--text-primary); }
  .tr-desc    { font-size: 12px; color: var(--text-muted); }
  .tr-rate    { font-family: 'DM Mono', monospace; font-size: 13px; font-weight: 600; color: var(--text-primary); flex-shrink: 0; }

  .default-tag {
    padding: 1px 6px; border-radius: 100px;
    background: var(--accent-soft); color: var(--accent);
    font-size: 10px; font-weight: 600;
  }

  .delete-btn {
    width: 26px; height: 26px; border-radius: 5px;
    display: flex; align-items: center; justify-content: center;
    font-size: 17px; color: var(--text-muted);
    transition: background 0.12s, color 0.12s; font-family: inherit;
  }
  .delete-btn:hover { background: var(--status-overdue-bg); color: var(--status-overdue-text); }

  .empty-rates { padding: 20px; text-align: center; font-size: 13px; color: var(--text-muted); }

  /* Feedback banners */
  .error-banner, .success-banner {
    margin-bottom: 16px; padding: 10px 16px;
    border-radius: var(--radius-sm); font-size: 13px; border: 1px solid currentColor;
  }
  .error-banner   { background: var(--status-overdue-bg); color: var(--status-overdue-text); }
  .success-banner { background: var(--status-paid-bg);    color: var(--status-paid-text); }
</style>