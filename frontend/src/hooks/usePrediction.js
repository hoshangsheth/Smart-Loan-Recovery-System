import { useCallback, useState } from 'react';
import { predictRisk } from '../services/api';

/**
 * Owns the "current borrower" state for the whole guided workflow.
 * The backend is stateless, so this hook is the single source of truth
 * the Predictor, Dashboard, and PDF-download steps all read from.
 */
export function usePrediction() {
  const [borrowerInput, setBorrowerInput] = useState(null);
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const runPrediction = useCallback(async (input) => {
    setIsLoading(true);
    setError(null);
    try {
      const prediction = await predictRisk(input);
      setBorrowerInput(input);
      setResult(prediction);
      return prediction;
    } catch (err) {
      setError(err.message || 'Something went wrong while predicting risk.');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setBorrowerInput(null);
    setResult(null);
    setError(null);
  }, []);

  return { borrowerInput, result, isLoading, error, runPrediction, reset };
}
