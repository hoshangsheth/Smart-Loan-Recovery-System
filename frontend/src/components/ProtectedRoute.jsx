import { Navigate, useLocation } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import PageShell from './PageShell';

export default function ProtectedRoute({ children }) {
  const { isConfigured, isReady, session } = useAuth();
  const location = useLocation();

  if (!isConfigured) {
    return (
      <PageShell>
        <p className="text-center text-mute">
          Sign-in isn't configured for this deployment yet. Set <code className="font-mono text-white">VITE_SUPABASE_URL</code>{' '}
          and <code className="font-mono text-white">VITE_SUPABASE_PUBLISHABLE_KEY</code>.
        </p>
      </PageShell>
    );
  }
  if (!isReady) {
    return (
      <PageShell>
        <div className="flex justify-center text-mute" role="status">
          <Loader2 className="animate-spin" size={22} />
          <span className="sr-only">Loading</span>
        </div>
      </PageShell>
    );
  }
  if (!session) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }
  return children;
}
