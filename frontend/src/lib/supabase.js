import { createClient } from '@supabase/supabase-js';

const url = import.meta.env.VITE_SUPABASE_URL;
const publishableKey = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY;

// Null when the env vars aren't set: the app then runs in anonymous mode
// (predictor works, nothing is saved) instead of crashing on load.
export const supabase = url && publishableKey ? createClient(url, publishableKey) : null;
