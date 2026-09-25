import { useState } from 'react';
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { Loader2, LogIn, MailCheck, UserPlus } from 'lucide-react';
import PageShell from '../components/PageShell';
import GlassCard from '../components/GlassCard';
import Button from '../components/Button';
import { TextField } from '../components/FormFields';
import { useAuth } from '../context/AuthContext';
import { useAuthProviders } from '../hooks/useAuthProviders';
import ConsentCheckbox from '../components/ConsentCheckbox';

const MIN_PASSWORD_LENGTH = 8;

function GoogleIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 48 48" aria-hidden="true">
      <path fill="#FFC107" d="M43.6 20.5H42V20H24v8h11.3C33.7 32.7 29.2 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34 6.1 29.3 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.3-.1-2.4-.4-3.5z" />
      <path fill="#FF3D00" d="m6.3 14.7 6.6 4.8C14.7 15.1 19 12 24 12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34 6.1 29.3 4 24 4 16.3 4 9.7 8.3 6.3 14.7z" />
      <path fill="#4CAF50" d="M24 44c5.2 0 9.9-2 13.4-5.2l-6.2-5.2C29.2 35.1 26.7 36 24 36c-5.2 0-9.6-3.3-11.3-7.9l-6.5 5C9.5 39.6 16.2 44 24 44z" />
      <path fill="#1976D2" d="M43.6 20.5H42V20H24v8h11.3c-.8 2.2-2.2 4.2-4.1 5.6l6.2 5.2C36.9 39.2 44 34 44 24c0-1.3-.1-2.4-.4-3.5z" />
    </svg>
  );
}

export default function Login({ mode = 'signin' }) {
  const isSignUp = mode === 'signup';
  const { isConfigured, session, signIn, signUp, signInWithGoogle } = useAuth();
  const providers = useAuthProviders();
  const navigate = useNavigate();
  const location = useLocation();
  const redirectTo = location.state?.from || '/cases';

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [pendingConfirmation, setPendingConfirmation] = useState(null);
  const [agreed, setAgreed] = useState(false);

  if (session) return <Navigate to={redirectTo} replace />;

  const passwordTooShort = isSignUp && password.length > 0 && password.length < MIN_PASSWORD_LENGTH;
  const passwordsDiffer = isSignUp && confirmPassword.length > 0 && password !== confirmPassword;
  const canSubmit = isSignUp
    ? email && password.length >= MIN_PASSWORD_LENGTH && password === confirmPassword && agreed
    : email && password;

  async function handleSubmit(event) {
    event.preventDefault();
    if (!canSubmit) return;
    setError(null);
    setIsSubmitting(true);
    try {
      if (isSignUp) {
        const needsConfirmation = await signUp(email.trim(), password);
        if (needsConfirmation) {
          setPendingConfirmation(email.trim());
          return;
        }
      } else {
        await signIn(email.trim(), password);
      }
      navigate(redirectTo, { replace: true });
    } catch (err) {
      setError(err.message || 'Something went wrong. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleGoogle() {
    setError(null);
    try {
      await signInWithGoogle({ consented: isSignUp && agreed });
    } catch (err) {
      setError(err.message);
    }
  }

  if (pendingConfirmation) {
    return (
      <PageShell width="max-w-md">
        <GlassCard className="p-6 sm:p-8 text-center">
          <MailCheck className="mx-auto text-lime mb-4" size={32} />
          <h1 className="font-display text-2xl font-bold text-white">Check your inbox</h1>
          <p className="text-mute text-sm mt-3">
            We sent a confirmation link to <span className="text-white">{pendingConfirmation}</span>. Open it to
            activate your account, then sign in.
          </p>
          <Link to="/login" className="inline-block mt-6 text-sm text-lime hover:underline">
            Back to sign in
          </Link>
        </GlassCard>
      </PageShell>
    );
  }

  return (
    <PageShell width="max-w-md">
      <div className="text-center mb-8">
        <span className="text-xs uppercase tracking-wider text-lime">Recovia</span>
        <h1 className="font-display text-3xl sm:text-4xl font-bold text-white mt-3">
          {isSignUp ? 'Create your account' : 'Sign in to your case queue'}
        </h1>
        <p className="text-mute mt-3 text-sm">
          {isSignUp
            ? 'Save predictions as cases, track them over time, and generate AI case briefs.'
            : 'The public predictor works without an account, but nothing is saved.'}
        </p>
      </div>

      <GlassCard className="p-6 sm:p-8">
        {!isConfigured ? (
          <p className="text-mute text-sm">Accounts aren't configured for this deployment yet.</p>
        ) : (
          <>
            {isSignUp && (
              <div className="mb-6 rounded-2xl border border-line bg-slate-soft p-4">
                <ConsentCheckbox checked={agreed} onChange={setAgreed} />
              </div>
            )}
            {providers.google && (
              <>
                <Button variant="ghost" className="w-full" onClick={handleGoogle} disabled={isSignUp && !agreed}>
                  <GoogleIcon /> Continue with Google
                </Button>
                <div className="flex items-center gap-3 my-6 text-xs text-mute" aria-hidden="true">
                  <span className="h-px flex-1 bg-line" /> or with email <span className="h-px flex-1 bg-line" />
                </div>
              </>
            )}

            <form onSubmit={handleSubmit} noValidate>
              <TextField
                label="Email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
              <TextField
                label="Password"
                type="password"
                autoComplete={isSignUp ? 'new-password' : 'current-password'}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                hint={isSignUp ? `At least ${MIN_PASSWORD_LENGTH} characters.` : undefined}
                aria-invalid={passwordTooShort || undefined}
              />
              {isSignUp && (
                <TextField
                  label="Confirm password"
                  type="password"
                  autoComplete="new-password"
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  aria-invalid={passwordsDiffer || undefined}
                />
              )}
              {passwordsDiffer && (
                <p className="-mt-3 mb-4 text-xs text-risk-high" role="alert">
                  Passwords don't match.
                </p>
              )}
              {error && (
                <p role="alert" className="mb-4 rounded-xl border border-risk-high/30 bg-risk-high/10 px-4 py-3 text-sm text-risk-high">
                  {error}
                </p>
              )}
              <Button type="submit" className="w-full" disabled={isSubmitting || !canSubmit}>
                {isSubmitting ? (
                  <Loader2 size={16} className="animate-spin" />
                ) : isSignUp ? (
                  <UserPlus size={16} />
                ) : (
                  <LogIn size={16} />
                )}
                {isSubmitting ? 'Please wait…' : isSignUp ? 'Create account' : 'Sign in'}
              </Button>
            </form>

            {(providers.signupEnabled || !isSignUp) && (
              <p className="text-center text-sm text-mute mt-6">
                {isSignUp ? (
                  <>
                    Already have an account?{' '}
                    <Link to="/login" state={location.state} className="text-lime hover:underline">
                      Sign in
                    </Link>
                  </>
                ) : (
                  providers.signupEnabled && (
                    <>
                      New here?{' '}
                      <Link to="/signup" state={location.state} className="text-lime hover:underline">
                        Create an account
                      </Link>
                    </>
                  )
                )}
              </p>
            )}
          </>
        )}
      </GlassCard>
    </PageShell>
  );
}
