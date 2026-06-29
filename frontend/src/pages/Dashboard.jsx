import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { RefreshCcw } from 'lucide-react';
import Nav from '../components/Nav';
import Button from '../components/Button';
import RiskScoreCard from '../components/RiskScoreCard';
import RecoveryStrategyCard from '../components/RecoveryStrategyCard';
import SegmentCard from '../components/SegmentCard';
import EmiSummaryCard from '../components/EmiSummaryCard';
import BorrowerProfileCard from '../components/BorrowerProfileCard';
import ShapChart from '../components/ShapChart';
import AnalyticsCharts from '../components/AnalyticsCharts';
import PdfDownloadButton from '../components/PdfDownloadButton';
import { getAnalytics } from '../services/api';
import { getDashboardRiskBand, RISK_COLORS } from '../utils/risk';

export default function Dashboard({ predictionState }) {
  const navigate = useNavigate();
  const { result, borrowerInput, reset } = predictionState;
  const [analytics, setAnalytics] = useState(null);

  useEffect(() => {
    if (!result || !borrowerInput) return;
    getAnalytics({
      emi_to_income_ratio: result.calculated.emi_to_income_ratio,
      collateral_coverage: result.calculated.collateral_coverage,
      loan_tenure: result.calculated.loan_tenure_used,
      missed_payments: borrowerInput.missed_payments,
      loan_amount: borrowerInput.loan_amount,
      collateral_value: borrowerInput.collateral_value,
      risk_score: result.risk_score,
    })
      .then(setAnalytics)
      .catch(() => setAnalytics(null));
  }, [result, borrowerInput]);

  if (!result || !borrowerInput) {
    return (
      <div className="min-h-screen bg-night">
        <Nav />
        <div className="flex flex-col items-center justify-center min-h-[70vh] px-6 text-center">
          <p className="text-mute mb-6">
            No borrower prediction found. Please fill the borrower's details and predict first.
          </p>
          <Button variant="primary" onClick={() => navigate('/predictor')}>
            Go to Predictor
          </Button>
        </div>
      </div>
    );
  }

  const dashboardBand = getDashboardRiskBand(result.risk_score);
  const accentColor = RISK_COLORS[dashboardBand];

  return (
    <div className="min-h-screen bg-night">
      <Nav />
      <section className="px-6 pt-32 pb-24 max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="flex flex-wrap items-end justify-between gap-4 mb-10"
        >
          <div>
            <span className="text-xs uppercase tracking-wider" style={{ color: accentColor }}>
              Recovery Insights Dashboard
            </span>
            <h1 className="font-display text-4xl font-bold text-white mt-2">
              Borrower Risk, Strategy &amp; Visual Analytics
            </h1>
          </div>
          <div className="flex gap-3">
            <PdfDownloadButton result={result} input={borrowerInput} />
            <Button
              variant="ghost"
              onClick={() => {
                reset();
                navigate('/predictor');
              }}
            >
              <RefreshCcw size={16} /> New Prediction
            </Button>
          </div>
        </motion.div>

        <div className="grid lg:grid-cols-3 gap-5 mb-8">
          <RiskScoreCard riskScore={result.risk_score} riskCategory={result.risk_category} />
          <RecoveryStrategyCard strategy={result.strategy} />
          <SegmentCard segment={result.segment} />
        </div>

        <div className="grid lg:grid-cols-2 gap-5 mb-8">
          <BorrowerProfileCard input={borrowerInput} borrowerId={result.borrower_id} />
          <EmiSummaryCard
            calculated={result.calculated}
            loanAmount={borrowerInput.loan_amount}
            outstandingLoan={borrowerInput.outstanding_loan}
          />
        </div>

        <div className="mb-8">
          <ShapChart features={result.shap_top_features} />
        </div>

        <AnalyticsCharts analytics={analytics} />
      </section>
    </div>
  );
}
