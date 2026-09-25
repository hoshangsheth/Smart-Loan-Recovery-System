import { useEffect, useState } from 'react';

const url = import.meta.env.VITE_SUPABASE_URL;
const publishableKey = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY;

/**
 * Reads the project's public auth settings so the UI only offers what is
 * actually enabled in the Supabase dashboard (e.g. hides Google until it's set up).
 */
export function useAuthProviders() {
  const [providers, setProviders] = useState({ google: false, signupEnabled: true });

  useEffect(() => {
    if (!url || !publishableKey) return;
    fetch(`${url}/auth/v1/settings`, { headers: { apikey: publishableKey } })
      .then((res) => (res.ok ? res.json() : null))
      .then((s) => s && setProviders({ google: Boolean(s.external?.google), signupEnabled: !s.disable_signup }))
      .catch(() => {});
  }, []);

  return providers;
}
