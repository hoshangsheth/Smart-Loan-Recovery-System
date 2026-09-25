import { Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Predictor from './pages/Predictor';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Cases from './pages/Cases';
import CaseDetail from './pages/CaseDetail';
import ProtectedRoute from './components/ProtectedRoute';
import ConsentGate from './components/ConsentGate';
import Terms from './pages/legal/Terms';
import Privacy from './pages/legal/Privacy';
import ResponsibleRecovery from './pages/legal/ResponsibleRecovery';
import { useAuth } from './context/AuthContext';
import { usePrediction } from './hooks/usePrediction';

export default function App() {
  const predictionState = usePrediction();
  const { session, profile } = useAuth();

  return (
    <>
    {session && profile?.consent_required && <ConsentGate />}
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/predictor" element={<Predictor predictionState={predictionState} />} />
      <Route path="/dashboard" element={<Dashboard predictionState={predictionState} />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Login mode="signup" />} />
      <Route path="/terms" element={<Terms />} />
      <Route path="/privacy" element={<Privacy />} />
      <Route path="/responsible-recovery" element={<ResponsibleRecovery />} />
      <Route
        path="/cases"
        element={
          <ProtectedRoute>
            <Cases />
          </ProtectedRoute>
        }
      />
      <Route
        path="/cases/:caseId"
        element={
          <ProtectedRoute>
            <CaseDetail />
          </ProtectedRoute>
        }
      />
    </Routes>
    </>
  );
}
