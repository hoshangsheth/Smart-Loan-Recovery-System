import { useState } from 'react';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';
import { Loader2, LogIn } from 'lucide-react';
import PageShell from '../components/PageShell';
import GlassCard from '../components/GlassCard';
import Button from '../components/Button';
import { TextField } from '../components/FormFields';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const { isConfigured, session, signIn } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const redirectTo = location.state?.from || '/cases';

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (session) return <Navigate to={redirectTo} replace />;

  async function handleSubmit(event) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await signIn(email.trim(), password);
      navigate(redirectTo, { replace: true });
    } catch (err) {
      setError(err.message || 'Sign-in failed.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <PageShell width="max-w-md">
      <div className="text-center mb-8">
        <span className="text-xs uppercase tracking-wider text-lime">Recovery officers</span>
        <h1 className="font-display text-3xl sm:text-4xl font-bold text-white mt-3">Sign in to your case queue</h1>
        <p className="text-mute mt-3 text-sm">
          Accounts are created by your admin. The public predictor works without signing in, but nothing is saved.
        </p>
      </div>

      <GlassCard className="p-6 sm:p-8">
        {!isConfigured ? (
          <p className="text-mute text-sm">Sign-in isn't configured for this deployment yet.</p>
        ) : (
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
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            {error && (
              <p role="alert" className="mb-4 rounded-xl border border-risk-high/30 bg-risk-high/10 px-4 py-3 text-sm text-risk-high">
                {error}
              </p>
            )}
            <Button type="submit" className="w-full" disabled={isSubmitting || !email || !password}>
              {isSubmitting ? <Loader2 size={16} className="animate-spin" /> : <LogIn size={16} />}
              {isSubmitting ? 'Signing in…' : 'Sign in'}
            </Button>
          </form>
        )}
      </GlassCard>
    </PageShell>
  );
}
