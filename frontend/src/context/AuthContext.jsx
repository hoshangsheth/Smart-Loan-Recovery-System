import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { supabase } from '../lib/supabase';
import { acceptTerms, getMe } from '../services/api';

const AuthContext = createContext(null);

const redirectUrl = () => `${window.location.origin}/cases`;
// Set when someone ticks the consent box before signing up or continuing with Google;
// the acceptance is recorded as soon as their session exists.
// Expires so an abandoned sign-up can't grant consent for someone else on a shared browser.
const PENDING_CONSENT_KEY = 'recovia.pendingConsent';
const PENDING_CONSENT_TTL_MS = 15 * 60 * 1000;

function readPendingConsent() {
  try {
    const setAt = Number(localStorage.getItem(PENDING_CONSENT_KEY));
    return Boolean(setAt) && Date.now() - setAt < PENDING_CONSENT_TTL_MS;
  } catch {
    return false;
  }
}

function writePendingConsent(value) {
  try {
    if (value) localStorage.setItem(PENDING_CONSENT_KEY, String(Date.now()));
    else localStorage.removeItem(PENDING_CONSENT_KEY);
  } catch {
    // storage unavailable: the consent screen will ask after sign-in instead
  }
}

export function AuthProvider({ children }) {
  const [session, setSession] = useState(null);
  const [isReady, setIsReady] = useState(!supabase);
  // undefined while loading for a signed-in user, null when unavailable (signed out or API down).
  const [profile, setProfile] = useState(undefined);

  useEffect(() => {
    if (!supabase) return undefined;
    supabase.auth.getSession().then(({ data }) => {
      setSession(data.session);
      setIsReady(true);
    });
    const { data } = supabase.auth.onAuthStateChange((_event, next) => setSession(next));
    return () => data.subscription.unsubscribe();
  }, []);

  const refreshProfile = useCallback(async () => {
    try {
      let me = await getMe();
      if (me.consent_required && readPendingConsent()) {
        me = await acceptTerms(me.terms_version);
      }
      writePendingConsent(false);
      setProfile(me);
    } catch {
      setProfile(null);
    }
  }, []);

  const userId = session?.user?.id;
  useEffect(() => {
    if (userId) {
      setProfile(undefined);
      refreshProfile();
    } else {
      setProfile(null);
    }
  }, [userId, refreshProfile]);

  const value = useMemo(
    () => ({
      isConfigured: Boolean(supabase),
      isReady,
      session,
      user: session?.user ?? null,
      isAdmin: session?.user?.app_metadata?.role === 'admin',
      profile,
      refreshProfile,
      async acceptCurrentTerms() {
        setProfile(await acceptTerms(profile.terms_version));
      },
      async signIn(email, password) {
        const { error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) throw error;
      },
      /** Resolves to true when the account still needs its email confirmed. */
      async signUp(email, password) {
        writePendingConsent(true);
        const { data, error } = await supabase.auth.signUp({
          email,
          password,
          options: { emailRedirectTo: redirectUrl() },
        });
        if (error) {
          writePendingConsent(false);
          throw error;
        }
        return !data.session;
      },
      async signInWithGoogle({ consented = false } = {}) {
        if (consented) writePendingConsent(true);
        const { error } = await supabase.auth.signInWithOAuth({
          provider: 'google',
          options: { redirectTo: redirectUrl() },
        });
        if (error) {
          writePendingConsent(false);
          throw error;
        }
      },
      async signOut() {
        await supabase.auth.signOut();
      },
    }),
    [isReady, session, profile, refreshProfile]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
