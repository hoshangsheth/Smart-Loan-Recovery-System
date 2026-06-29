import { Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Predictor from './pages/Predictor';
import Dashboard from './pages/Dashboard';
import { usePrediction } from './hooks/usePrediction';

export default function App() {
  const predictionState = usePrediction();

  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/predictor" element={<Predictor predictionState={predictionState} />} />
      <Route path="/dashboard" element={<Dashboard predictionState={predictionState} />} />
    </Routes>
  );
}
