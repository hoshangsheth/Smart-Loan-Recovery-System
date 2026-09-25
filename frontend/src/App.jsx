import { Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Predictor from './pages/Predictor';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Cases from './pages/Cases';
import CaseDetail from './pages/CaseDetail';
import ProtectedRoute from './components/ProtectedRoute';
import { usePrediction } from './hooks/usePrediction';

export default function App() {
  const predictionState = usePrediction();

  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/predictor" element={<Predictor predictionState={predictionState} />} />
      <Route path="/dashboard" element={<Dashboard predictionState={predictionState} />} />
      <Route path="/login" element={<Login />} />
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
  );
}
