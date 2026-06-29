import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import Nav from '../components/Nav';
import BorrowerForm from '../components/BorrowerForm';
import { usePrediction } from '../hooks/usePrediction';

export default function Predictor({ predictionState }) {
  const navigate = useNavigate();
  const { runPrediction, isLoading, error } = predictionState;

  async function handleSubmit(input) {
    try {
      await runPrediction(input);
      navigate('/dashboard');
    } catch {
      // error is already surfaced via predictionState.error
    }
  }

  return (
    <div className="min-h-screen bg-night">
      <Nav />
      <section className="px-6 pt-32 pb-24">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="max-w-2xl mx-auto text-center mb-10"
        >
          <span className="text-xs uppercase tracking-wider text-lime">AI Loan Risk Predictor</span>
          <h1 className="font-display text-4xl font-bold text-white mt-3">
            Tell us about the borrower.
          </h1>
        </motion.div>

        <BorrowerForm onSubmit={handleSubmit} isLoading={isLoading} error={error} />
      </section>
    </div>
  );
}
