import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { ArrowLeft, Loader2 } from 'lucide-react';
import PageShell from '../components/PageShell';
import RiskScoreCard from '../components/RiskScoreCard';
import RecoveryStrategyCard from '../components/RecoveryStrategyCard';
import SegmentCard from '../components/SegmentCard';
import ShapChart from '../components/ShapChart';
import RiskHistoryChart from '../components/RiskHistoryChart';
import CaseBriefCard from '../components/CaseBriefCard';
import { getCase, updateCaseStatus } from '../services/api';
import { CASE_STATUSES } from '../constants/caseStatus';

export default function CaseDetail() {
  const { caseId } = useParams();
  const [detail, setDetail] = useState(null);
  const [error, setError] = useState(null);
  const [statusError, setStatusError] = useState(null);
  const [isSavingStatus, setIsSavingStatus] = useState(false);

  useEffect(() => {
    let cancelled = false;
    getCase(caseId)
      .then((d) => !cancelled && setDetail(d))
      .catch((err) => !cancelled && setError(err.status === 404 ? 'Case not found.' : err.message));
    return () => {
      cancelled = true;
    };
  }, [caseId]);

  async function handleStatusChange(event) {
    setIsSavingStatus(true);
    setStatusError(null);
    try {
      setDetail(await updateCaseStatus(caseId, event.target.value));
    } catch (err) {
      setStatusError(err.message);
    } finally {
      setIsSavingStatus(false);
    }
  }

  const backLink = (
    <Link to="/cases" className="inline-flex items-center gap-1.5 text-sm text-mute hover:text-lime mb-6">
      <ArrowLeft size={16} /> Back to queue
    </Link>
  );

  if (error) {
    return (
      <PageShell>
        {backLink}
        <p role="alert" className="text-risk-high">{error}</p>
      </PageShell>
    );
  }
  if (!detail) {
    return (
      <PageShell>
        <div className="flex items-center justify-center gap-2 py-16 text-mute" role="status">
          <Loader2 size={18} className="animate-spin" /> Loading case…
        </div>
      </PageShell>
    );
  }

  const latest = detail.predictions[detail.predictions.length - 1];

  return (
    <PageShell>
      {backLink}
      <div className="flex flex-wrap items-end justify-between gap-4 mb-8">
        <div className="min-w-0">
          <p className="text-xs text-mute font-mono truncate">
            {detail.borrower_ref} · {detail.loan_type}
          </p>
          <h1 className="font-display text-3xl sm:text-4xl font-bold text-white mt-2 break-words">
            {detail.first_name} {detail.last_name}
          </h1>
        </div>
        <label className="flex items-center gap-3">
          <span className="text-sm text-mute">Status</span>
          <select
            value={detail.status}
            onChange={handleStatusChange}
            disabled={isSavingStatus}
            className="rounded-full border border-line bg-slate-soft px-4 py-2 text-sm text-white focus:border-lime/60 disabled:opacity-50"
          >
            {CASE_STATUSES.map((s) => (
              <option key={s.value} value={s.value}>
                {s.label}
              </option>
            ))}
          </select>
        </label>
      </div>
      {statusError && (
        <p role="alert" className="mb-6 text-sm text-risk-high">
          Couldn't update status: {statusError}
        </p>
      )}

      <div className="grid lg:grid-cols-3 gap-5 mb-5">
        <RiskScoreCard
          riskScore={latest.risk_score}
          riskCategory={latest.risk_category}
          riskBand={latest.risk_band}
          assetClassification={latest.asset_classification}
          policyOverride={latest.policy_override}
          warning={latest.risk_tier === 'high_no_dpd' ? 'Becomes Critical if the account crosses 90 days past due.' : null}
        />
        <RecoveryStrategyCard strategy={latest.strategy} />
        <SegmentCard segment={latest.segment} />
      </div>

      <div className="mb-5">
        <CaseBriefCard
          caseId={detail.id}
          brief={detail.latest_brief}
          borrowerFirstName={detail.first_name}
          onGenerated={(brief) => setDetail((d) => ({ ...d, latest_brief: brief }))}
        />
      </div>

      <div className="grid lg:grid-cols-2 gap-5">
        <RiskHistoryChart predictions={detail.predictions} />
        <ShapChart features={latest.shap_top_features} />
      </div>
    </PageShell>
  );
}
