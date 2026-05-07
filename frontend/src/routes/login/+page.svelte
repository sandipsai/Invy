<!-- src/routes/login/+page.svelte -->
<script>
  import { page } from '$app/stores';
  import { PUBLIC_API_BASE } from '$env/static/public';

  /** @type {import('./$types').PageData} */
  export let data;

  // If redirected here after a failed/expired session, show a message
  $: reason = $page.url.searchParams.get('reason');

  const providers = [
    {
      id:    'google',
      label: 'Continue with Google',
      icon:  'G',
      color: '#4285f4',
    },
    {
      id:    'github',
      label: 'Continue with GitHub',
      icon:  '◎',
      color: '#333',
    },
  ];

  /**
   * Each provider link points to the Python backend's OAuth entry point.
   * FastAPI redirects to the provider, handles the callback, sets a
   * session cookie, then redirects back to the frontend at /auth/callback.
   *
   * URL shape: http://localhost:8000/auth/{provider}/login
   *            ?redirect_uri=http://localhost:5173/auth/callback
   */
  function oauthUrl(provider) {
    const callbackUrl = `${$page.url.origin}/auth/callback`;
    return `${PUBLIC_API_BASE}/auth/${provider}/login?redirect_uri=${encodeURIComponent(callbackUrl)}`;
  }
</script>

<div class="login-page">
  <div class="login-card">

    <!-- Brand -->
    <div class="brand">
      <div class="brand-icon">FT</div>
      <div>
        <div class="brand-name">FinTrack</div>
        <div class="brand-sub">Enterprise Admin</div>
      </div>
    </div>

    <h1 class="title">Sign in to your account</h1>
    <p class="subtitle">Choose a provider to continue.</p>

    <!-- Session expiry / error messages -->
    {#if reason === 'expired'}
      <div class="info-banner">Your session expired. Please sign in again.</div>
    {:else if reason === 'unauthorized'}
      <div class="info-banner warn">You need to sign in to access that page.</div>
    {/if}

    <!-- OAuth provider buttons -->
    <div class="providers">
      {#each providers as provider (provider.id)}
        <a
          class="provider-btn"
          href={oauthUrl(provider.id)}
          data-sveltekit-reload
        >
          <span class="provider-icon" style="background:{provider.color}">{provider.icon}</span>
          {provider.label}
        </a>
      {/each}
    </div>

    <p class="footer-note">
      By signing in you agree to our
      <a href="/terms" class="link">Terms of Service</a>
      and
      <a href="/privacy" class="link">Privacy Policy</a>.
    </p>

  </div>
</div>

<style>
  /* Full-page centred layout — sits outside AppShell */
  .login-page {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-app);
    padding: 24px;
  }

  .login-card {
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
    padding: 40px 36px;
    width: 100%;
    max-width: 400px;
  }

  /* Brand */
  .brand {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 28px;
  }

  .brand-icon {
    width: 36px;
    height: 36px;
    background: var(--accent);
    border-radius: var(--radius-sm);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-on-accent);
    font-size: 15px;
    font-weight: 700;
    flex-shrink: 0;
  }

  .brand-name { font-size: 15px; font-weight: 700; color: var(--text-primary); line-height: 1.2; }
  .brand-sub  { font-size: 11px; color: var(--text-muted); letter-spacing: 0.05em; }

  /* Headings */
  .title    { font-size: 20px; font-weight: 600; color: var(--text-primary); margin-bottom: 6px; }
  .subtitle { font-size: 13.5px; color: var(--text-muted); margin-bottom: 24px; }

  /* Info banners */
  .info-banner {
    padding: 10px 14px;
    border-radius: var(--radius-sm);
    font-size: 13px;
    margin-bottom: 20px;
    background: var(--accent-soft);
    color: var(--accent);
    border: 1px solid rgba(30, 102, 245, 0.2);
  }

  .info-banner.warn {
    background: var(--status-pending-bg);
    color: var(--status-pending-text);
    border-color: var(--status-pending-text);
  }

  /* OAuth buttons */
  .providers {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 24px;
  }

  .provider-btn {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 11px 16px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border);
    background: var(--bg-surface);
    color: var(--text-primary);
    font-size: 14px;
    font-weight: 500;
    text-decoration: none;
    transition: background 0.12s, border-color 0.12s, box-shadow 0.12s;
    font-family: 'DM Sans', sans-serif;
  }

  .provider-btn:hover {
    background: var(--bg-surface-alt);
    border-color: var(--text-muted);
    box-shadow: var(--shadow-sm);
  }

  .provider-icon {
    width: 28px;
    height: 28px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 13px;
    font-weight: 700;
    flex-shrink: 0;
  }

  /* Footer */
  .footer-note {
    font-size: 12px;
    color: var(--text-muted);
    text-align: center;
    line-height: 1.6;
  }

  .link {
    color: var(--accent);
    text-decoration: none;
  }

  .link:hover {
    text-decoration: underline;
  }
</style>