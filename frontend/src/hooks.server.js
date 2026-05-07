import { PUBLIC_API_BASE } from '$env/static/public';

let startupChecked = false;

/** @type {import('@sveltejs/kit').Handle} */
export async function handle({ event, resolve }) {
  // Attach useful context to locals 
  event.locals.apiBase = PUBLIC_API_BASE;

  // Dev startup health check 
  if (!startupChecked && import.meta.env.DEV) {
    startupChecked = true;
    checkBackendHealth();
  }

  const response = await resolve(event);
  return response;
}

/**
 * Global error handler — called when an unexpected error is thrown
 * inside a load() or action that wasn't caught by the page's error boundary.
 * Prevents raw stack traces from leaking to the browser in production.
 *
 * @type {import('@sveltejs/kit').HandleServerError}
 */
export function handleError({ error, event }) {
  const message = error instanceof Error ? error.message : 'An unexpected error occurred.';

  console.error(`[hooks] Unhandled error on ${event.url.pathname}:`, error);

  return {
    message,
    // In production you'd send this to Sentry / Datadog here
  };
}

/**
 * Ping the FastAPI health endpoint on dev startup.
 * Logs a warning if the backend isn't reachable so the dev
 * knows immediately rather than getting cryptic fetch errors.
 */
async function checkBackendHealth() {
  try {
    const res = await fetch(`${PUBLIC_API_BASE}/`);
    if (res.ok) {
      const data = await res.json();
      console.log(`[hooks] Backend connected — ${data.app} v${data.version}`);
    } else {
      console.warn(`[hooks] Backend responded with ${res.status} at ${PUBLIC_API_BASE}`);
    }
  } catch {
    console.warn(
      `[hooks] Backend unreachable at ${PUBLIC_API_BASE}\n` +
      `         Run: uvicorn app.main:app --reload`
    );
  }
}